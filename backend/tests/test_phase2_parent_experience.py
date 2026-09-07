from __future__ import annotations

import pytest
from django.test import Client

from modules.identity.models import User
from modules.learning.models import (
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
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


@pytest.fixture
def parent_setup(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant_a = Tenant.objects.create(slug="tenant-a", name="Tenant A")
    tenant_b = Tenant.objects.create(slug="tenant-b", name="Tenant B")

    parent_user = User.objects.create_user(username="parent-user", email="parent@example.com")
    student_user = User.objects.create_user(username="student-user", email="student@example.com")
    mentor_user = User.objects.create_user(username="mentor-user", email="mentor@example.com")
    parent_b_user = User.objects.create_user(username="parent-b-user", email="parent_b@example.com")

    with tenant_atomic(tenant_a.id):
        TenantMembership.objects.create(
            tenant=tenant_a, user=parent_user, role=TenantMembership.Role.GUARDIAN
        )
        TenantMembership.objects.create(
            tenant=tenant_a, user=student_user, role=TenantMembership.Role.LEARNER
        )
        TenantMembership.objects.create(
            tenant=tenant_a, user=mentor_user, role=TenantMembership.Role.MENTOR
        )

        lp = LearningPath.objects.create(
            tenant=tenant_a, code="py-core", title="Python Core", state=PublicationState.PUBLISHED
        )
        course = Course.objects.create(
            tenant=tenant_a,
            learning_path=lp,
            code="py-101",
            title="Python 101",
            state=PublicationState.PUBLISHED,
        )
        lesson1 = Lesson.objects.create(
            tenant=tenant_a,
            course=course,
            code="l1",
            title="Lesson 1",
            position=1,
            state=PublicationState.PUBLISHED,
        )
        lesson2 = Lesson.objects.create(
            tenant=tenant_a,
            course=course,
            code="l2",
            title="Lesson 2",
            position=2,
            state=PublicationState.PUBLISHED,
        )
        assert lesson2.id is not None
        assignment = Assignment.objects.create(
            tenant=tenant_a,
            lesson=lesson1,
            code="a1",
            title="Task 1",
            state=AssignmentState.PUBLISHED,
        )
        submission = Submission.objects.create(
            tenant=tenant_a,
            assignment=assignment,
            student_id=student_user.id,
            content="print('hello')",
            state=SubmissionState.REVIEWED,
        )
        Feedback.objects.create(
            tenant=tenant_a,
            submission=submission,
            mentor_id=mentor_user.id,
            content="Great work on Python 101!",
        )
        Progress.objects.create(
            tenant=tenant_a,
            lesson=lesson1,
            student_id=student_user.id,
            state=ProgressState.COMPLETED,
        )

    with tenant_atomic(tenant_b.id):
        TenantMembership.objects.create(
            tenant=tenant_b, user=parent_b_user, role=TenantMembership.Role.GUARDIAN
        )

    parent_client = Client()
    parent_client.force_login(parent_user)
    s = parent_client.session
    s["session_auth_epoch"] = parent_user.session_auth_epoch
    s.save()

    return {
        "tenant_a": tenant_a,
        "tenant_b": tenant_b,
        "parent_user": parent_user,
        "parent_b_user": parent_b_user,
        "student_user": student_user,
        "mentor_user": mentor_user,
        "parent_client": parent_client,
    }


@pytest.mark.django_db(transaction=True)
def test_parent_summary_and_progress_flow(parent_setup):
    data = parent_setup
    tenant_a = data["tenant_a"]
    client = data["parent_client"]
    student_user = data["student_user"]

    # 1. Parent accesses student summary
    res = client.get(
        f"/api/v1/learning/parent/students/{student_user.id}/summary/",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res.status_code == 200
    summary = res.json()
    assert summary["student_id"] == str(student_user.id)
    assert summary["total_lessons"] == 2
    assert summary["completed_lessons"] == 1
    assert summary["completion_percentage"] == 50
    assert len(summary["submissions"]) == 1
    assert len(summary["recent_feedbacks"]) == 1
    assert summary["recent_feedbacks"][0]["content"] == "Great work on Python 101!"

    # 2. Parent accesses student progress list
    res_prog = client.get(
        f"/api/v1/learning/parent/students/{student_user.id}/progress/",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res_prog.status_code == 200
    progress_list = res_prog.json()["results"]
    assert len(progress_list) == 1
    assert progress_list[0]["state"] == "completed"
    assert progress_list[0]["lesson_code"] == "l1"

    # 3. Parent accesses student feedback list
    res_fb = client.get(
        f"/api/v1/learning/parent/students/{student_user.id}/feedbacks/",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res_fb.status_code == 200
    fb_list = res_fb.json()["results"]
    assert len(fb_list) == 1
    assert fb_list[0]["content"] == "Great work on Python 101!"


@pytest.mark.django_db(transaction=True)
def test_parent_cross_tenant_and_role_denials(parent_setup):
    data = parent_setup
    tenant_a = data["tenant_a"]
    tenant_b = data["tenant_b"]
    parent_b_user = data["parent_b_user"]
    mentor_user = data["mentor_user"]
    student_user = data["student_user"]

    # 1. Cross-tenant access: Parent B tries to access Student in Tenant A
    client_b = Client()
    client_b.force_login(parent_b_user)
    s = client_b.session
    s["session_auth_epoch"] = parent_b_user.session_auth_epoch
    s.save()

    # Under Tenant B host, student does not exist
    res_b = client_b.get(
        f"/api/v1/learning/parent/students/{student_user.id}/summary/",
        HTTP_HOST=f"{tenant_b.slug}.localhost",
    )
    assert res_b.status_code == 404

    # Under Tenant A host, Parent B has no membership -> 403
    res_cross = client_b.get(
        f"/api/v1/learning/parent/students/{student_user.id}/summary/",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res_cross.status_code in (403, 404)

    # 2. Learner and Mentor role access denied to parent endpoint
    mentor_client = Client()
    mentor_client.force_login(mentor_user)
    s_m = mentor_client.session
    s_m["session_auth_epoch"] = mentor_user.session_auth_epoch
    s_m.save()

    res_mentor = mentor_client.get(
        f"/api/v1/learning/parent/students/{student_user.id}/summary/",
        HTTP_HOST=f"{tenant_a.slug}.localhost",
    )
    assert res_mentor.status_code == 403
