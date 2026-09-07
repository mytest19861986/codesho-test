from __future__ import annotations

import pytest
from django.test import Client

from modules.identity.models import User
from modules.learning.models import (
    LearningPath,
    PublicationState,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


@pytest.fixture
def cross_role_setup(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant = Tenant.objects.create(slug="tenant-e2e", name="Tenant E2E")

    admin_user = User.objects.create_user(username="admin-e2e", email="admin@example.com")
    mentor_user = User.objects.create_user(username="mentor-e2e", email="mentor@example.com")
    student_user = User.objects.create_user(username="student-e2e", email="student@example.com")
    parent_user = User.objects.create_user(username="parent-e2e", email="parent@example.com")

    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant, user=admin_user, role=TenantMembership.Role.ADMIN
        )
        TenantMembership.objects.create(
            tenant=tenant, user=mentor_user, role=TenantMembership.Role.MENTOR
        )
        TenantMembership.objects.create(
            tenant=tenant, user=student_user, role=TenantMembership.Role.LEARNER
        )
        TenantMembership.objects.create(
            tenant=tenant, user=parent_user, role=TenantMembership.Role.GUARDIAN
        )

        lp = LearningPath.objects.create(
            tenant=tenant,
            code="e2e-lp",
            title="E2E Learning Path",
            state=PublicationState.PUBLISHED,
        )

    def create_client(user):
        c = Client()
        c.force_login(user)
        s = c.session
        s["session_auth_epoch"] = user.session_auth_epoch
        s.save()
        return c

    return {
        "tenant": tenant,
        "admin_user": admin_user,
        "mentor_user": mentor_user,
        "student_user": student_user,
        "parent_user": parent_user,
        "admin_client": create_client(admin_user),
        "mentor_client": create_client(mentor_user),
        "student_client": create_client(student_user),
        "parent_client": create_client(parent_user),
        "lp": lp,
    }


@pytest.mark.django_db(transaction=True)
def test_full_cross_role_e2e_flow(cross_role_setup):
    data = cross_role_setup
    tenant = data["tenant"]
    admin_client = data["admin_client"]
    mentor_client = data["mentor_client"]
    student_client = data["student_client"]
    parent_client = data["parent_client"]
    student_user = data["student_user"]
    mentor_user = data["mentor_user"]
    lp = data["lp"]

    host = f"{tenant.slug}.localhost"

    # Step 1: Admin creates course and publishes it
    res_c = admin_client.post(
        "/api/v1/learning/admin/curriculum/",
        data={
            "type": "course",
            "learning_path_id": str(lp.id),
            "code": "e2e-c1",
            "title": "E2E Course",
        },
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_c.status_code == 201
    course_id = res_c.json()["id"]

    res_pub_c = admin_client.post(
        "/api/v1/learning/admin/curriculum/transition/",
        data={"type": "course", "id": course_id, "action": "publish"},
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_pub_c.status_code == 200
    assert res_pub_c.json()["state"] == "published"

    # Step 2: Admin creates lesson and publishes it
    res_l = admin_client.post(
        "/api/v1/learning/admin/curriculum/",
        data={
            "type": "lesson",
            "course_id": course_id,
            "code": "e2e-l1",
            "title": "E2E Lesson",
            "position": 1,
        },
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_l.status_code == 201
    lesson_id = res_l.json()["id"]

    res_pub_l = admin_client.post(
        "/api/v1/learning/admin/curriculum/transition/",
        data={"type": "lesson", "id": lesson_id, "action": "publish"},
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_pub_l.status_code == 200

    # Step 3: Admin creates assignment and publishes it
    res_a = admin_client.post(
        "/api/v1/learning/admin/curriculum/",
        data={"type": "assignment", "lesson_id": lesson_id, "code": "e2e-a1", "title": "E2E Task"},
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_a.status_code == 201
    assignment_id = res_a.json()["id"]

    res_pub_a = admin_client.post(
        "/api/v1/learning/admin/curriculum/transition/",
        data={"type": "assignment", "id": assignment_id, "action": "publish"},
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_pub_a.status_code == 200

    # Step 4: Student discovers published course and lessons
    res_st_c = student_client.get("/api/v1/learning/courses/", HTTP_HOST=host)
    assert res_st_c.status_code == 200
    courses_found = [c["id"] for c in res_st_c.json()["results"]]
    assert str(course_id) in courses_found

    res_st_l = student_client.get(f"/api/v1/learning/courses/{course_id}/lessons/", HTTP_HOST=host)
    assert res_st_l.status_code == 200
    assert len(res_st_l.json()["results"]) == 1

    # Step 5: Student drafts and submits assignment
    res_draft = student_client.post(
        "/api/v1/learning/submissions/draft/",
        data={
            "assignment_id": assignment_id,
            "student_id": str(student_user.id),
            "content": "def solution(): return 42",
        },
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_draft.status_code == 200
    submission_id = res_draft.json()["id"]

    res_sub = student_client.post(
        f"/api/v1/learning/submissions/{submission_id}/submit/",
        HTTP_HOST=host,
    )
    assert res_sub.status_code == 200
    assert res_sub.json()["state"] == "submitted"

    # Step 6: Mentor sees submission in queue, starts review, and completes with feedback
    res_queue = mentor_client.get("/api/v1/learning/mentor/queue/", HTTP_HOST=host)
    assert res_queue.status_code == 200
    queue_items = res_queue.json()["results"]
    assert any(q["id"] == submission_id for q in queue_items)

    res_start = mentor_client.post(
        f"/api/v1/learning/mentor/submissions/{submission_id}/start-review/",
        HTTP_HOST=host,
    )
    assert res_start.status_code == 200
    assert res_start.json()["state"] == "under_review"

    res_complete = mentor_client.post(
        f"/api/v1/learning/mentor/submissions/{submission_id}/complete-review/",
        data={"mentor_id": str(mentor_user.id), "feedback": "Flawless cross-role solution!"},
        content_type="application/json",
        HTTP_HOST=host,
    )
    assert res_complete.status_code == 200

    # Step 7: Student fetches updated feedback
    res_st_fb = student_client.get(
        f"/api/v1/learning/student/submissions/{submission_id}/feedback/",
        HTTP_HOST=host,
    )
    assert res_st_fb.status_code == 200
    feedbacks = res_st_fb.json()["results"]
    assert len(feedbacks) == 1
    assert feedbacks[0]["content"] == "Flawless cross-role solution!"

    # Step 8: Parent views updated summary and sees 100% completion & feedback
    res_par = parent_client.get(
        f"/api/v1/learning/parent/students/{student_user.id}/summary/",
        HTTP_HOST=host,
    )
    assert res_par.status_code == 200
    par_data = res_par.json()
    assert par_data["completed_lessons"] == 1
    assert par_data["completion_percentage"] == 100
    assert len(par_data["recent_feedbacks"]) == 1
    assert par_data["recent_feedbacks"][0]["content"] == "Flawless cross-role solution!"
