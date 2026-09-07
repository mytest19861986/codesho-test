from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from modules.learning.models import (
    Assignment,
    Course,
    LearningPath,
    Lesson,
    Module,
    Progress,
    ProgressState,
    PublicationState,
    Submission,
    SubmissionState,
)
from modules.learning.services import (
    ContentStateMachine,
    ProgressStateMachine,
    SubmissionStateMachine,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db
def test_phase2_learning_models_and_unique_constraints():
    t1 = Tenant.objects.create(slug="t1", name="Tenant 1")
    with tenant_atomic(t1.id):
        lp = LearningPath.objects.create(tenant=t1, code="web-dev", title="Web Development")
        course = Course.objects.create(
            tenant=t1, learning_path=lp, code="frontend", title="Frontend Course"
        )
        mod = Module.objects.create(
            tenant=t1, course=course, code="html", title="HTML Basics", position=1
        )
        lesson = Lesson.objects.create(
            tenant=t1, course=course, module=mod, code="intro", title="Intro", position=1
        )
        assignment = Assignment.objects.create(
            tenant=t1, lesson=lesson, code="first-page", title="Create Page"
        )

        student_id = uuid4()
        subm = Submission.objects.create(
            tenant=t1,
            assignment=assignment,
            student_id=student_id,
            content="<html><body>Hello</body></html>",
        )
        assert subm.id is not None

        progress = Progress.objects.create(tenant=t1, lesson=lesson, student_id=student_id)
        assert progress.id is not None

        # Duplicate code within same tenant
        with pytest.raises(IntegrityError), transaction.atomic():
            LearningPath.objects.create(tenant=t1, code="web-dev", title="Duplicate")

        with pytest.raises(IntegrityError), transaction.atomic():
            Module.objects.create(
                tenant=t1, course=course, code="html", title="Duplicate", position=2
            )

        with pytest.raises(IntegrityError), transaction.atomic():
            Module.objects.create(
                tenant=t1, course=course, code="other", title="Duplicate Pos", position=1
            )


@pytest.mark.django_db
def test_phase2_state_machine_transitions():
    t1 = Tenant.objects.create(slug="t-sm", name="Tenant SM")
    mentor_id = uuid4()
    student_id = uuid4()

    with tenant_atomic(t1.id):
        lp = LearningPath.objects.create(tenant=t1, code="ai", title="AI Path")
        course = Course.objects.create(tenant=t1, learning_path=lp, code="py", title="Python")
        lesson = Lesson.objects.create(tenant=t1, course=course, code="l1", title="L1", position=1)
        assignment = Assignment.objects.create(tenant=t1, lesson=lesson, code="a1", title="A1")
        subm = Submission.objects.create(
            tenant=t1, assignment=assignment, student_id=student_id, content="Code here"
        )
        prog = Progress.objects.create(tenant=t1, lesson=lesson, student_id=student_id)

        # Content state transitions
        assert course.state == PublicationState.DRAFT
        ContentStateMachine.transition(course, PublicationState.PUBLISHED)
        assert course.state == PublicationState.PUBLISHED
        with pytest.raises(ValidationError):
            ContentStateMachine.transition(course, PublicationState.DRAFT)

        # Submission state lifecycle
        assert subm.state == SubmissionState.DRAFT
        SubmissionStateMachine.submit(subm)
        assert subm.state == SubmissionState.SUBMITTED
        assert subm.submitted_at is not None

        SubmissionStateMachine.start_review(subm)
        assert subm.state == SubmissionState.UNDER_REVIEW

        feedback = SubmissionStateMachine.complete_review(subm, mentor_id, "Great job!")
        assert subm.state == SubmissionState.REVIEWED
        assert feedback.content == "Great job!"

        # Progress lifecycle
        assert prog.state == ProgressState.NOT_STARTED
        ProgressStateMachine.start(prog)
        assert prog.state == ProgressState.IN_PROGRESS

        ProgressStateMachine.complete(prog)
        assert prog.state == ProgressState.COMPLETED
        assert prog.completed_at is not None
