import uuid
import pytest

from modules.learning.models import (
    Assignment,
    AssignmentState,
    Course,
    Feedback,
    Lesson,
    Module,
    PublicationState,
    Submission,
    SubmissionState,
)
from modules.learning.submissions import SubmissionEngine
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db(transaction=True)
def test_submission_and_feedback_cross_tenant_isolation_negative():
    tenant1 = Tenant.objects.create(name="T1", slug=f"t1-{uuid.uuid4().hex[:6]}")
    tenant2 = Tenant.objects.create(name="T2", slug=f"t2-{uuid.uuid4().hex[:6]}")

    student1 = uuid.uuid4()
    mentor1 = uuid.uuid4()

    with tenant_atomic(tenant1.id):
        course1 = Course.objects.create(
            tenant=tenant1,
            code=f"C1-{uuid.uuid4().hex[:4]}",
            title="Course 1",
            state=PublicationState.PUBLISHED,
        )
        module1 = Module.objects.create(
            tenant=tenant1,
            course=course1,
            code="M1",
            title="Module 1",
            position=1,
        )
        lesson1 = Lesson.objects.create(
            tenant=tenant1,
            course=course1,
            module=module1,
            code="L1",
            title="Lesson 1",
            position=1,
            state=PublicationState.PUBLISHED,
        )
        assignment1 = Assignment.objects.create(
            tenant=tenant1,
            lesson=lesson1,
            code="A1",
            title="Assignment 1",
            state=AssignmentState.PUBLISHED,
        )
        sub1 = SubmissionEngine.submit_assignment(
            tenant_id=tenant1.id,
            student_id=student1,
            assignment_id=assignment1.id,
            content="tenant 1 student submission code",
        )
        SubmissionEngine.claim_submission(
            tenant_id=tenant1.id,
            mentor_id=mentor1,
            submission_id=sub1.id,
        )
        fb1 = SubmissionEngine.complete_review(
            tenant_id=tenant1.id,
            mentor_id=mentor1,
            submission_id=sub1.id,
            feedback_content="Tenant 1 feedback",
            score=90,
        )

    # Querying under Tenant 2 MUST NOT leak any row or allow modification
    with tenant_atomic(tenant2.id):
        # 1. Assignment isolation
        assert Assignment.objects.filter(tenant=tenant2).count() == 0
        assert Assignment.objects.filter(tenant=tenant2, id=assignment1.id).first() is None

        # 2. Submission isolation
        assert Submission.objects.filter(tenant=tenant2).count() == 0
        assert Submission.objects.filter(tenant=tenant2, id=sub1.id).first() is None

        # 3. Feedback isolation
        assert Feedback.objects.filter(tenant=tenant2).count() == 0
        assert Feedback.objects.filter(tenant=tenant2, id=fb1.id).first() is None
