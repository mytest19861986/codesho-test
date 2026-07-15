from uuid import uuid4

import pytest
from django.db import connection

from modules.identity.models import User
from modules.platform_tenant.context import current_tenant_id, tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


@pytest.mark.django_db(transaction=True)
def test_context_is_reset_after_transaction():
    tenant_id = uuid4()
    assert current_tenant_id() is None
    with tenant_atomic(tenant_id):
        assert current_tenant_id() == tenant_id
    assert current_tenant_id() is None


@pytest.mark.django_db(transaction=True)
def test_membership_rls_fails_closed_without_context():
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific RLS contract")

    tenant = Tenant.objects.create(slug="alpha", name="Alpha")
    user = User.objects.create_user(username="learner", email="learner@example.com")
    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant,
            user=user,
            role=TenantMembership.Role.LEARNER,
        )
        assert TenantMembership.objects.filter(tenant=tenant).count() == 1

    assert TenantMembership.objects.filter(tenant=tenant).count() == 0


@pytest.mark.django_db(transaction=True)
def test_context_does_not_leak_across_reused_connection():
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific pooling contract")

    first = Tenant.objects.create(slug="first", name="First")
    second = Tenant.objects.create(slug="second", name="Second")
    user = User.objects.create_user(username="mentor", email="mentor@example.com")

    with tenant_atomic(first.id):
        TenantMembership.objects.create(
            tenant=first,
            user=user,
            role=TenantMembership.Role.MENTOR,
        )
    with tenant_atomic(second.id):
        assert TenantMembership.objects.filter(tenant=first).count() == 0
