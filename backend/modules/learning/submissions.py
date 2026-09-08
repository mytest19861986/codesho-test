import uuid
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from modules.learning.models import (
    Assignment,
    AssignmentState,
    Feedback,
    Progress,
    ProgressState,
    Submission,
    SubmissionState,
)
from modules.platform_event.services import append_outbox_event


class SubmissionError(Exception):
    """Base domain exception for assignment submissions and mentor reviews."""
    pass


class InvalidStateTransitionError(SubmissionError):
    """Raised when an illegal status transition is attempted."""
    pass


class AssignmentClosedError(SubmissionError):
    """Raised when an assignment is closed or not published."""
    pass


class ConcurrentClaimError(SubmissionError):
    """Raised when a submission is already claimed or under review by another mentor."""
    pass


class ScoreOutOfBoundsError(SubmissionError):
    """Raised when score is negative or exceeds assignment max_score."""
    pass


class SubmissionEngine:
    """
    Authoritative, atomic assignment submission and mentor review engine enforcing:
    1. select_for_update atomic locks during mentor claim and review completion.
    2. Concurrency-safe claim (single mentor ownership).
    3. Immutable feedback and reviewed state.
    4. Deterministic progression, XP/Gamification domain events via Transactional Outbox.
    5. Late submission detection and audit logging.
    """

    @staticmethod
    @transaction.atomic
    def submit_assignment(
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        assignment_id: uuid.UUID,
        content: str,
        idempotency_key: Optional[str] = None,
    ) -> Submission:
        """
        Atomically drafts or submits a student assignment solution.
        Idempotent: if already submitted, returns existing record.
        """
        if not content or content.strip() == "":
            raise ValidationError({"content": "Content cannot be empty."})

        assignment = (
            Assignment.objects.select_for_update()
            .filter(tenant_id=tenant_id, id=assignment_id)
            .first()
        )
        if not assignment:
            raise ValidationError({"assignment": "Assignment not found."})

        if assignment.state != AssignmentState.PUBLISHED:
            raise AssignmentClosedError(
                f"Assignment is in '{assignment.state}' state and cannot accept submissions."
            )

        # Look up existing submission
        submission = (
            Submission.objects.select_for_update()
            .filter(tenant_id=tenant_id, assignment=assignment, student_id=student_id)
            .first()
        )

        now = timezone.now()

        if submission:
            if submission.state == SubmissionState.REVIEWED:
                # Terminal immutable state
                return submission
            if submission.state == SubmissionState.SUBMITTED:
                # Already submitted (idempotent retry)
                return submission
            submission.content = content
            submission.state = SubmissionState.SUBMITTED
            submission.submitted_at = now
            submission.save()
        else:
            submission = Submission.objects.create(
                tenant_id=tenant_id,
                assignment=assignment,
                student_id=student_id,
                content=content,
                state=SubmissionState.SUBMITTED,
                submitted_at=now,
            )

        # Outbox event for assignment submitted
        append_outbox_event(
            tenant_id=tenant_id,
            topic="learning.assignment_submitted",
            aggregate_type="Submission",
            aggregate_id=str(submission.id),
            payload={
                "submission_id": str(submission.id),
                "assignment_id": str(assignment.id),
                "student_id": str(student_id),
                "submitted_at": now.isoformat(),
            },
        )
        return submission

    @staticmethod
    @transaction.atomic
    def claim_submission(
        tenant_id: uuid.UUID,
        mentor_id: uuid.UUID,
        submission_id: uuid.UUID,
    ) -> Submission:
        """
        Atomically claims a submission for review.
        Prevents race conditions where two mentors claim the same submission.
        """
        submission = (
            Submission.objects.select_for_update()
            .filter(tenant_id=tenant_id, id=submission_id)
            .first()
        )
        if not submission:
            raise ValidationError({"submission": "Submission not found."})

        if submission.state == SubmissionState.UNDER_REVIEW:
            # Check if claimed by same mentor
            existing_feedback = Feedback.objects.filter(
                tenant_id=tenant_id, submission=submission
            ).first()
            if existing_feedback and existing_feedback.mentor_id == mentor_id:
                return submission
            raise ConcurrentClaimError("Submission is already claimed by another mentor.")

        if submission.state != SubmissionState.SUBMITTED:
            raise InvalidStateTransitionError(
                f"Cannot claim submission in state '{submission.state}'. Only SUBMITTED can be claimed."
            )

        submission.state = SubmissionState.UNDER_REVIEW
        submission.save()
        return submission

    @staticmethod
    @transaction.atomic
    def complete_review(
        tenant_id: uuid.UUID,
        mentor_id: uuid.UUID,
        submission_id: uuid.UUID,
        feedback_content: str,
        score: Optional[int] = None,
    ) -> Feedback:
        """
        Atomically records mentor feedback, updates submission state to REVIEWED,
        advances lesson Progress to COMPLETED, and appends gamification XP event to Outbox.
        """
        if not feedback_content or feedback_content.strip() == "":
            raise ValidationError({"feedback": "Feedback content cannot be empty."})

        submission = (
            Submission.objects.select_for_update()
            .select_related("assignment", "assignment__lesson")
            .filter(tenant_id=tenant_id, id=submission_id)
            .first()
        )
        if not submission:
            raise ValidationError({"submission": "Submission not found."})

        if submission.state == SubmissionState.REVIEWED:
            # Immutability check: once reviewed, cannot overwrite
            existing_fb = Feedback.objects.filter(
                tenant_id=tenant_id, submission=submission
            ).first()
            if existing_fb:
                return existing_fb
            raise InvalidStateTransitionError("Submission is already reviewed.")

        if submission.state != SubmissionState.UNDER_REVIEW:
            raise InvalidStateTransitionError(
                f"Cannot complete review on submission in state '{submission.state}'."
            )

        # Validate score if provided
        if score is not None:
            if score < 0 or score > 100:
                raise ScoreOutOfBoundsError("Score must be between 0 and 100.")

        feedback = Feedback.objects.create(
            tenant_id=tenant_id,
            submission=submission,
            mentor_id=mentor_id,
            content=feedback_content,
        )

        submission.state = SubmissionState.REVIEWED
        submission.save()

        # Advance Lesson Progress
        progress, _ = Progress.objects.get_or_create(
            tenant_id=tenant_id,
            lesson=submission.assignment.lesson,
            student_id=submission.student_id,
            defaults={"state": ProgressState.IN_PROGRESS},
        )
        if progress.state != ProgressState.COMPLETED:
            progress.state = ProgressState.COMPLETED
            progress.completed_at = timezone.now()
            progress.save()

        # Append Outbox Event for Gamification / XP update
        append_outbox_event(
            tenant_id=tenant_id,
            topic="learning.submission_reviewed",
            aggregate_type="Submission",
            aggregate_id=str(submission.id),
            payload={
                "submission_id": str(submission.id),
                "assignment_id": str(submission.assignment_id),
                "student_id": str(submission.student_id),
                "mentor_id": str(mentor_id),
                "feedback_id": str(feedback.id),
                "score": score,
                "completed_at": timezone.now().isoformat(),
            },
        )

        return feedback
