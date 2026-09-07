from uuid import UUID

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    Assignment,
    AssignmentState,
    Course,
    Feedback,
    LearningPath,
    Lesson,
    Progress,
    ProgressState,
    PublicationState,
    Submission,
    SubmissionState,
)


class ContentStateMachine:
    VALID_TRANSITIONS = {
        PublicationState.DRAFT: {PublicationState.PUBLISHED},
        PublicationState.PUBLISHED: {PublicationState.ARCHIVED},
        PublicationState.ARCHIVED: set(),
    }

    @classmethod
    def transition(cls, entity, target_state: PublicationState) -> None:
        current = entity.state
        if target_state not in cls.VALID_TRANSITIONS.get(current, set()):
            raise ValidationError(
                f"Invalid publication transition from '{current}' to '{target_state}'."
            )
        entity.state = target_state
        entity.save()


class AssignmentStateMachine:
    VALID_TRANSITIONS = {
        AssignmentState.DRAFT: {AssignmentState.PUBLISHED},
        AssignmentState.PUBLISHED: {AssignmentState.CLOSED},
        AssignmentState.CLOSED: set(),
    }

    @classmethod
    def transition(cls, assignment: Assignment, target_state: AssignmentState) -> None:
        current = assignment.state
        if target_state not in cls.VALID_TRANSITIONS.get(current, set()):
            raise ValidationError(
                f"Invalid assignment transition from '{current}' to '{target_state}'."
            )
        assignment.state = target_state
        assignment.save()


class SubmissionStateMachine:
    VALID_TRANSITIONS = {
        SubmissionState.DRAFT: {SubmissionState.SUBMITTED},
        SubmissionState.SUBMITTED: {SubmissionState.UNDER_REVIEW},
        SubmissionState.UNDER_REVIEW: {SubmissionState.REVIEWED, SubmissionState.DRAFT},
        SubmissionState.REVIEWED: set(),
    }

    @classmethod
    def submit(cls, submission: Submission) -> None:
        if submission.state != SubmissionState.DRAFT:
            raise ValidationError(f"Cannot submit submission in state '{submission.state}'.")
        if not submission.content or submission.content.strip() == "":
            raise ValidationError("Cannot submit empty submission content.")
        submission.state = SubmissionState.SUBMITTED
        submission.submitted_at = timezone.now()
        submission.save()

    @classmethod
    def start_review(cls, submission: Submission) -> None:
        if submission.state != SubmissionState.SUBMITTED:
            raise ValidationError(
                f"Cannot start review on submission in state '{submission.state}'."
            )
        submission.state = SubmissionState.UNDER_REVIEW
        submission.save()

    @classmethod
    def complete_review(
        cls, submission: Submission, mentor_id: UUID, feedback_content: str
    ) -> Feedback:
        if submission.state != SubmissionState.UNDER_REVIEW:
            raise ValidationError(
                f"Cannot complete review on submission in state '{submission.state}'."
            )
        if not feedback_content or feedback_content.strip() == "":
            raise ValidationError("Feedback content cannot be empty.")

        feedback = Feedback.objects.create(
            tenant=submission.tenant,
            submission=submission,
            mentor_id=mentor_id,
            content=feedback_content,
        )
        submission.state = SubmissionState.REVIEWED
        submission.save()

        # Deterministically advance Progress for this student and lesson
        progress, _ = Progress.objects.get_or_create(
            tenant=submission.tenant,
            lesson=submission.assignment.lesson,
            student_id=submission.student_id,
            defaults={"state": ProgressState.IN_PROGRESS},
        )
        if progress.state != ProgressState.COMPLETED:
            progress.state = ProgressState.COMPLETED
            progress.completed_at = timezone.now()
            progress.save()

        return feedback

    @classmethod
    def request_revision(cls, submission: Submission) -> None:
        if submission.state != SubmissionState.UNDER_REVIEW:
            raise ValidationError(
                f"Cannot request revision on submission in state '{submission.state}'."
            )
        submission.state = SubmissionState.DRAFT
        submission.save()


class ProgressStateMachine:
    VALID_TRANSITIONS = {
        ProgressState.NOT_STARTED: {ProgressState.IN_PROGRESS},
        ProgressState.IN_PROGRESS: {ProgressState.COMPLETED},
        ProgressState.COMPLETED: set(),
    }

    @classmethod
    def start(cls, progress: Progress) -> None:
        if progress.state != ProgressState.NOT_STARTED:
            raise ValidationError(f"Progress already started: '{progress.state}'.")
        progress.state = ProgressState.IN_PROGRESS
        progress.save()

    @classmethod
    def complete(cls, progress: Progress) -> None:
        if progress.state != ProgressState.IN_PROGRESS:
            raise ValidationError(f"Cannot complete progress from state '{progress.state}'.")
        progress.state = ProgressState.COMPLETED
        progress.completed_at = timezone.now()
        progress.save()


class ParentLearningSummaryService:
    @staticmethod
    def get_summary_for_student(tenant, student_id: UUID) -> dict:
        learning_paths = LearningPath.objects.filter(
            tenant=tenant, state=PublicationState.PUBLISHED
        ).order_by("code")
        courses = Course.objects.filter(tenant=tenant, state=PublicationState.PUBLISHED).order_by(
            "code"
        )
        all_lessons = Lesson.objects.filter(tenant=tenant, state=PublicationState.PUBLISHED)
        total_lessons_count = all_lessons.count()

        completed_progress = Progress.objects.filter(
            tenant=tenant,
            student_id=student_id,
            state=ProgressState.COMPLETED,
        )
        completed_lessons_count = completed_progress.count()
        completion_pct = (
            int((completed_lessons_count / total_lessons_count) * 100)
            if total_lessons_count > 0
            else 0
        )

        active_assignments = Assignment.objects.filter(
            tenant=tenant, state=AssignmentState.PUBLISHED
        ).order_by("code")[:10]

        submissions = (
            Submission.objects.filter(tenant=tenant, student_id=student_id)
            .select_related("assignment", "assignment__lesson")
            .order_by("-submitted_at", "-created_at")[:10]
        )

        recent_feedbacks = (
            Feedback.objects.filter(tenant=tenant, submission__student_id=student_id)
            .select_related("submission")
            .order_by("-created_at")[:5]
        )

        return {
            "student_id": student_id,
            "learning_paths": learning_paths,
            "courses": courses,
            "total_lessons": total_lessons_count,
            "completed_lessons": completed_lessons_count,
            "completion_percentage": completion_pct,
            "active_assignments": active_assignments,
            "submissions": submissions,
            "recent_feedbacks": recent_feedbacks,
        }
