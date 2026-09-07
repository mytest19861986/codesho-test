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
def admin_setup(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant = Tenant.objects.create(slug="tenant-admin", name="Tenant Admin")

    admin_user = User.objects.create_user(username="admin-user", email="admin@example.com")
    learner_user = User.objects.create_user(username="learner-user", email="learner@example.com")
    mentor_user = User.objects.create_user(username="mentor-user", email="mentor@example.com")

    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant, user=admin_user, role=TenantMembership.Role.ADMIN
        )
        TenantMembership.objects.create(
            tenant=tenant, user=learner_user, role=TenantMembership.Role.LEARNER
        )
        TenantMembership.objects.create(
            tenant=tenant, user=mentor_user, role=TenantMembership.Role.MENTOR
        )

        lp = LearningPath.objects.create(
            tenant=tenant, code="lp-main", title="Main Path", state=PublicationState.PUBLISHED
        )

    admin_client = Client()
    admin_client.force_login(admin_user)
    s = admin_client.session
    s["session_auth_epoch"] = admin_user.session_auth_epoch
    s.save()

    return {
        "tenant": tenant,
        "admin_user": admin_user,
        "learner_user": learner_user,
        "mentor_user": mentor_user,
        "admin_client": admin_client,
        "learning_path": lp,
    }


@pytest.mark.django_db(transaction=True)
def test_admin_curriculum_crud_and_transitions(admin_setup):
    data = admin_setup
    tenant = data["tenant"]
    client = data["admin_client"]
    lp = data["learning_path"]

    # 1. Admin creates draft course
    res_c = client.post(
        "/api/v1/learning/admin/curriculum/",
        data={
            "type": "course",
            "learning_path_id": str(lp.id),
            "code": "py-advanced",
            "title": "Python Advanced",
        },
        content_type="application/json",
        HTTP_HOST=f"{tenant.slug}.localhost",
    )
    assert res_c.status_code == 201
    course_data = res_c.json()
    course_id = course_data["id"]
    assert course_data["state"] == "draft"

    # 2. Admin creates draft lesson
    res_l = client.post(
        "/api/v1/learning/admin/curriculum/",
        data={
            "type": "lesson",
            "course_id": course_id,
            "code": "async-py",
            "title": "Asyncio in Python",
            "position": 1,
        },
        content_type="application/json",
        HTTP_HOST=f"{tenant.slug}.localhost",
    )
    assert res_l.status_code == 201
    lesson_data = res_l.json()
    lesson_id = lesson_data["id"]
    assert lesson_id is not None
    assert lesson_data["state"] == "draft"

    # 3. Admin transitions course from DRAFT -> PUBLISHED
    res_pub = client.post(
        "/api/v1/learning/admin/curriculum/transition/",
        data={"type": "course", "id": course_id, "action": "publish"},
        content_type="application/json",
        HTTP_HOST=f"{tenant.slug}.localhost",
    )
    assert res_pub.status_code == 200
    assert res_pub.json()["state"] == "published"

    # 4. Invalid transition directly to draft -> 409
    res_inv = client.post(
        "/api/v1/learning/admin/curriculum/transition/",
        data={"type": "course", "id": course_id, "action": "draft"},
        content_type="application/json",
        HTTP_HOST=f"{tenant.slug}.localhost",
    )
    assert res_inv.status_code in (400, 409)

    # 5. Archive transition PUBLISHED -> ARCHIVED
    res_arc = client.post(
        "/api/v1/learning/admin/curriculum/transition/",
        data={"type": "course", "id": course_id, "action": "archive"},
        content_type="application/json",
        HTTP_HOST=f"{tenant.slug}.localhost",
    )
    assert res_arc.status_code == 200
    assert res_arc.json()["state"] == "archived"


@pytest.mark.django_db(transaction=True)
def test_admin_authorization_matrix(admin_setup):
    data = admin_setup
    tenant = data["tenant"]
    learner_user = data["learner_user"]
    mentor_user = data["mentor_user"]

    # Learner access denied to admin curriculum
    learner_client = Client()
    learner_client.force_login(learner_user)
    s = learner_client.session
    s["session_auth_epoch"] = learner_user.session_auth_epoch
    s.save()

    res_learner = learner_client.get(
        "/api/v1/learning/admin/curriculum/",
        HTTP_HOST=f"{tenant.slug}.localhost",
    )
    assert res_learner.status_code == 403

    # Mentor access denied to admin curriculum
    mentor_client = Client()
    mentor_client.force_login(mentor_user)
    s_m = mentor_client.session
    s_m["session_auth_epoch"] = mentor_user.session_auth_epoch
    s_m.save()

    res_mentor = mentor_client.get(
        "/api/v1/learning/admin/curriculum/",
        HTTP_HOST=f"{tenant.slug}.localhost",
    )
    assert res_mentor.status_code == 403
