from __future__ import annotations

import pytest
from django.test import Client

from modules.identity.models import User
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


@pytest.fixture
def auth_matrix_setup(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant_1 = Tenant.objects.create(slug="tenant-1", name="Tenant 1")
    tenant_2 = Tenant.objects.create(slug="tenant-2", name="Tenant 2")

    student_1 = User.objects.create_user(username="student-1", email="student1@example.com")
    mentor_1 = User.objects.create_user(username="mentor-1", email="mentor1@example.com")
    parent_1 = User.objects.create_user(username="parent-1", email="parent1@example.com")
    admin_1 = User.objects.create_user(username="admin-1", email="admin1@example.com")

    student_2 = User.objects.create_user(username="student-2", email="student2@example.com")

    with tenant_atomic(tenant_1.id):
        TenantMembership.objects.create(
            tenant=tenant_1, user=student_1, role=TenantMembership.Role.LEARNER
        )
        TenantMembership.objects.create(
            tenant=tenant_1, user=mentor_1, role=TenantMembership.Role.MENTOR
        )
        TenantMembership.objects.create(
            tenant=tenant_1, user=parent_1, role=TenantMembership.Role.GUARDIAN
        )
        TenantMembership.objects.create(
            tenant=tenant_1, user=admin_1, role=TenantMembership.Role.ADMIN
        )

    with tenant_atomic(tenant_2.id):
        TenantMembership.objects.create(
            tenant=tenant_2, user=student_2, role=TenantMembership.Role.LEARNER
        )

    def create_client(user):
        c = Client()
        c.force_login(user)
        s = c.session
        s["session_auth_epoch"] = user.session_auth_epoch
        s.save()
        return c

    return {
        "tenant_1": tenant_1,
        "tenant_2": tenant_2,
        "student_1": student_1,
        "client_student": create_client(student_1),
        "client_mentor": create_client(mentor_1),
        "client_parent": create_client(parent_1),
        "client_admin": create_client(admin_1),
        "client_student_2": create_client(student_2),
    }


@pytest.mark.django_db(transaction=True)
def test_comprehensive_cross_role_authorization_matrix(auth_matrix_setup):
    data = auth_matrix_setup
    t1 = data["tenant_1"]
    t2 = data["tenant_2"]
    host1 = f"{t1.slug}.localhost"
    host2 = f"{t2.slug}.localhost"

    st_client = data["client_student"]
    men_client = data["client_mentor"]
    par_client = data["client_parent"]
    adm_client = data["client_admin"]
    st2_client = data["client_student_2"]
    student_1 = data["student_1"]

    # 1. Admin endpoints protection
    # Admin allowed
    res = adm_client.get("/api/v1/learning/admin/curriculum/", HTTP_HOST=host1)
    assert res.status_code == 200
    # Student, Mentor, Parent denied
    assert st_client.get("/api/v1/learning/admin/curriculum/", HTTP_HOST=host1).status_code == 403
    assert men_client.get("/api/v1/learning/admin/curriculum/", HTTP_HOST=host1).status_code == 403
    assert par_client.get("/api/v1/learning/admin/curriculum/", HTTP_HOST=host1).status_code == 403

    # 2. Parent endpoints protection
    # Parent & Admin allowed (or 404 if no activity, but not 403)
    res_par = par_client.get(
        f"/api/v1/learning/parent/students/{student_1.id}/summary/", HTTP_HOST=host1
    )
    assert res_par.status_code in (200, 404)
    # Student & Mentor strictly denied
    assert (
        st_client.get(
            f"/api/v1/learning/parent/students/{student_1.id}/summary/", HTTP_HOST=host1
        ).status_code
        == 403
    )
    assert (
        men_client.get(
            f"/api/v1/learning/parent/students/{student_1.id}/summary/", HTTP_HOST=host1
        ).status_code
        == 403
    )

    # 3. Cross-Tenant Denial & Own Tenant Boundaries
    # Tenant 2 client accessing Tenant 1 host fails with 403/404
    assert st2_client.get("/api/v1/learning/admin/curriculum/", HTTP_HOST=host1).status_code in (
        403,
        404,
    )
    assert st2_client.get(
        f"/api/v1/learning/parent/students/{student_1.id}/summary/", HTTP_HOST=host1
    ).status_code in (403, 404)

    # Tenant 2 client accessing its own tenant admin is denied
    assert st2_client.get("/api/v1/learning/admin/curriculum/", HTTP_HOST=host2).status_code == 403
