import uuid
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from modules.learning.models import (
    Assignment,
    AssignmentState,
    Course,
    Feedback,
    Lesson,
    Module,
    Progress,
    ProgressState,
    PublicationState,
    Submission,
    SubmissionState,
)
from modules.learning.submissions import (
    SubmissionEngine,
    AssignmentClosedError,
    ConcurrentClaimError,
    InvalidStateTransitionError,
    ScoreOutOfBoundsError,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant
from modules.platform_event.models import OutboxEvent


@pytest.mark.django_db(transaction=True)
class TestP3VS6SubmissionWorkflow:
    def setup_method(self):
        self.tenant = Tenant.objects.create(
            name="Test Academy VS6",
            slug=f"test-academy-vs6-{uuid.uuid4().hex[:6]}",
        )
        self.student = uuid.uuid4()
        self.mentor_1 = uuid.uuid4()
        self.mentor_2 = uuid.uuid4()

        with tenant_atomic(self.tenant.id):
            self.course = Course.objects.create(
                tenant=self.tenant,
                code=f"CS-P3VS6-{uuid.uuid4().hex[:4]}",
                title="Advanced AI & Python",
                state=PublicationState.PUBLISHED,
            )
            self.module = Module.objects.create(
                tenant=self.tenant,
                course=self.course,
                code="MOD-1",
                title="Module 1",
                position=1,
            )
            self.lesson = Lesson.objects.create(
                tenant=self.tenant,
                course=self.course,
                module=self.module,
                code="LES-1",
                title="Lesson 1: Functions",
                position=1,
                state=PublicationState.PUBLISHED,
            )
            self.assignment = Assignment.objects.create(
                tenant=self.tenant,
                lesson=self.lesson,
                code="ASGN-1",
                title="Assignment 1: Build a Calculator",
                state=AssignmentState.PUBLISHED,
            )

    def test_student_submission_lifecycle(self):
        with tenant_atomic(self.tenant.id):
            # 1. Submit assignment
            sub = SubmissionEngine.submit_assignment(
                tenant_id=self.tenant.id,
                student_id=self.student,
                assignment_id=self.assignment.id,
                content="def add(a, b): return a + b",
            )
            assert sub.state == SubmissionState.SUBMITTED
            assert sub.submitted_at is not None

            # 2. Mentor claims submission
            claimed = SubmissionEngine.claim_submission(
                tenant_id=self.tenant.id,
                mentor_id=self.mentor_1,
                submission_id=sub.id,
            )
            assert claimed.state == SubmissionState.UNDER_REVIEW

            # 3. Mentor completes review with feedback & score
            feedback = SubmissionEngine.complete_review(
                tenant_id=self.tenant.id,
                mentor_id=self.mentor_1,
                submission_id=sub.id,
                feedback_content="Excellent implementation of calculator function.",
                score=95,
            )
            assert feedback.mentor_id == self.mentor_1
            assert feedback.content == "Excellent implementation of calculator function."

            # Verify submission is now REVIEWED (terminal state)
            sub.refresh_from_db()
            assert sub.state == SubmissionState.REVIEWED

            # Verify Lesson Progress is advanced to COMPLETED
            progress = Progress.objects.get(
                tenant_id=self.tenant.id,
                lesson=self.lesson,
                student_id=self.student,
            )
            assert progress.state == ProgressState.COMPLETED

            # Verify Outbox domain event generated
            outbox_event = OutboxEvent.objects.filter(
                tenant_id=self.tenant.id,
                topic="learning.submission_reviewed",
            ).first()
            assert outbox_event is not None
            assert outbox_event.payload["score"] == 95

    def test_concurrent_mentor_claim_prevented(self):
        with tenant_atomic(self.tenant.id):
            sub = SubmissionEngine.submit_assignment(
                tenant_id=self.tenant.id,
                student_id=self.student,
                assignment_id=self.assignment.id,
                content="def sub(a, b): return a - b",
            )

            # Mentor 1 claims first
            SubmissionEngine.claim_submission(
                tenant_id=self.tenant.id,
                mentor_id=self.mentor_1,
                submission_id=sub.id,
            )

            # Mentor 2 attempts to claim the same submission
            with pytest.raises(ConcurrentClaimError):
                SubmissionEngine.claim_submission(
                    tenant_id=self.tenant.id,
                    mentor_id=self.mentor_2,
                    submission_id=sub.id,
                )

    def test_submission_immutability_after_reviewed(self):
        with tenant_atomic(self.tenant.id):
            sub = SubmissionEngine.submit_assignment(
                tenant_id=self.tenant.id,
                student_id=self.student,
                assignment_id=self.assignment.id,
                content="solution 1",
            )
            SubmissionEngine.claim_submission(
                tenant_id=self.tenant.id,
                mentor_id=self.mentor_1,
                submission_id=sub.id,
            )
            SubmissionEngine.complete_review(
                tenant_id=self.tenant.id,
                mentor_id=self.mentor_1,
                submission_id=sub.id,
                feedback_content="Approved",
                score=100,
            )

            # Idempotent re-submit returns same reviewed record without modifying content
            resub = SubmissionEngine.submit_assignment(
                tenant_id=self.tenant.id,
                student_id=self.student,
                assignment_id=self.assignment.id,
                content="solution 2 (attempt to cheat)",
            )
            assert resub.content == "solution 1"
            assert resub.state == SubmissionState.REVIEWED

    def test_closed_assignment_rejects_submission(self):
        with tenant_atomic(self.tenant.id):
            self.assignment.state = AssignmentState.CLOSED
            self.assignment.save()

            with pytest.raises(AssignmentClosedError):
                SubmissionEngine.submit_assignment(
                    tenant_id=self.tenant.id,
                    student_id=self.student,
                    assignment_id=self.assignment.id,
                    content="late code",
                )

    def test_score_out_of_bounds_validation(self):
        with tenant_atomic(self.tenant.id):
            sub = SubmissionEngine.submit_assignment(
                tenant_id=self.tenant.id,
                student_id=self.student,
                assignment_id=self.assignment.id,
                content="solution",
            )
            SubmissionEngine.claim_submission(
                tenant_id=self.tenant.id,
                mentor_id=self.mentor_1,
                submission_id=sub.id,
            )
            with pytest.raises(ScoreOutOfBoundsError):
                SubmissionEngine.complete_review(
                    tenant_id=self.tenant.id,
                    mentor_id=self.mentor_1,
                    submission_id=sub.id,
                    feedback_content="Score invalid",
                    score=150,
                )
