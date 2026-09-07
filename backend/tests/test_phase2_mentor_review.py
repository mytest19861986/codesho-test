from __future__ import annotations

import pytest
from django.test import Client

from modules.identity.models import User
from modules.learning.models import (
    Assignment,
    AssignmentState,
    Course,
    Feedback,
    Lesson,
    Progress,
    ProgressState,
    PublicationState,
    Submission,
    SubmissionState,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


@pytest.fixture
def test_setup(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant_a = Tenant.objects.create(slug="tenant-a", name="Tenant A")
    tenant_b = Tenant.objects.create(slug="tenant-b", name="Tenant B")

    student_user = User.objects.create_user(username="student-user", email="student@example.com")
    mentor_user = User.objects.create_user(username="mentor-user", email="mentor@example.com")
    mentor_b_user = User.objects.create_user(username="mentor-b-user", email="mentor_b@example.com")

    with tenant_atomic(tenant_a.id):
        TenantMembership.objects.create(
            tenant=tenant_a, user=student_user, role=TenantMembership.Role.LEARNER
        )
        TenantMembership.objects.create(
            tenant=tenant_a, user=mentor_user, role=TenantMembership.Role.MENTOR
        )
        course = Course.objects.create(
            tenant=tenant_a, code="py-101", title="Python 101", state=PublicationState.PUBLISHED
        )
        lesson = Lesson.objects.create(
            tenant=tenant_a,
            course=course,
            code="l1",
            title="Lesson 1",
            position=1,
            state=PublicationState.PUBLISHED,
        )
        assignment = Assignment.objects.create(
            tenant=tenant_a,
            lesson=lesson,
            code="a1",
            title="Task 1",
            state=AssignmentState.PUBLISHED,
        )
        submission = Submission.objects.create(
            tenant=tenant_a,
            assignment=assignment,
            student_id=student_user.id,
            content="Initial Code",
            state=SubmissionState.SUBMITTED,
        )

    with tenant_atomic(tenant_b.id):
        TenantMembership.objects.create(
            tenant=tenant_b, user=mentor_b_user, role=TenantMembership.Role.MENTOR
        )

    mentor_client = Client()
    mentor_client.force_login(mentor_user)
    s = mentor_client.session
    s["session_auth_epoch"] = mentor_user.session_auth_epoch
    s.save()

    return {
        "tenant_a": tenant_a,
        "tenant_b": tenant_b,
        "mentor_user": mentor_user,
        "mentor_b_user": mentor_b_user,
        "student_user": student_user,
        "submission": submission,
        "client": mentor_client,
    }


@pytest.mark.django_db(transaction=True)
def test_mentor_review_flow_success(test_setup):
    data = test_setup
    tenant_a = data["tenant_a"]
    client = data["client"]
    submission = data["submission"]
    mentor_user = data["mentor_user"]

    # 1. Mentor views queue
    res = client.get("/api/v1/learning/mentor/queue/", HTTP_HOST=f"{tenant_a.slug}.localhost")
    assert res.status_code == 200
    results = res.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(submission.id)
    assert results[0]["state"] == "submitted"
    assert results[0]["assignment_title"] == "Task 1"

    # 2. Mentor starts review
    res_start = client.post(
        f"/api/v1/learning/mentor/submissions/{submission.id}/start-review/",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res_start.status_code == 200
    submission.refresh_from_db()
    assert submission.state == "under_review"

    # 3. Mentor completes review with feedback
    res_comp = client.post(
        f"/api/v1/learning/mentor/submissions/{submission.id}/complete-review/",
        data={"mentor_id": str(mentor_user.id), "feedback": "Excellent work! Code is clean."},
        content_type="application/json",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res_comp.status_code == 200
    submission.refresh_from_db()
    assert submission.state == "reviewed"
    assert Feedback.objects.filter(submission=submission, tenant=tenant_a).count() == 1

    # 4. Progress was automatically advanced to COMPLETED
    progress = Progress.objects.get(
        tenant=tenant_a, student_id=data["student_user"].id, lesson=submission.assignment.lesson
    )
    assert progress.state == ProgressState.COMPLETED
    assert progress.completed_at is not None

    # 5. Student can fetch feedback
    res_fb = client.get(
        f"/api/v1/learning/student/submissions/{submission.id}/feedback/",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res_fb.status_code == 200
    fb_list = res_fb.json()["results"]
    assert len(fb_list) == 1
    assert fb_list[0]["submission"] == str(submission.id)
    assert fb_list[0]["content"] == "Excellent work! Code is clean."


@pytest.mark.django_db(transaction=True)
def test_cross_tenant_denial(test_setup):
    data = test_setup
    tenant_b = data["tenant_b"]
    client = data["client"]
    submission = data["submission"]

    # Accessing submission under Tenant B host should fail closed
    res = client.get(
        f"/api/v1/learning/mentor/submissions/{submission.id}/",
        HTTP_HOST=f"{tenant_b.slug}.localhost",
    )
    assert res.status_code in (403, 404)
