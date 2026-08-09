import os
from datetime import timedelta
from threading import Barrier, Thread
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from django.db import close_old_connections, connection
from django.utils import timezone
from psycopg import connect

from config.cleanup_claims import (
    acquire_cleanup_claims,
    begin_claim,
    complete_claim,
    create_pending_claim,
    fail_claim,
    reclaim_expired_claim,
)
from modules.identity.models import CleanupWorkClaim
from modules.identity.tasks import run_cleanup_claim_task
from modules.platform_event.models import OutboxEvent
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(slug=f"claim-{uuid4().hex[:8]}", name="Claim tenant")


def require_postgres() -> None:
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific cleanup claim contract")


@pytest.fixture
def runtime_connection():
    require_postgres()
    runtime_url = os.environ.get("DATABASE_RUNTIME_TEST_URL")
    if not runtime_url:
        pytest.skip("explicit runtime test URL is not configured")
    with connect(runtime_url, autocommit=False) as runtime:
        yield runtime
        runtime.rollback()


@pytest.mark.django_db(transaction=True)
def test_claiming_disabled_is_fail_closed(settings, tenant):
    claim = create_pending_claim(tenant_id=tenant.id)
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = False

    assert acquire_cleanup_claims(tenant_id=tenant.id) == []
    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.PENDING
    with tenant_atomic(tenant.id):
        assert not OutboxEvent.objects.filter(tenant_id=tenant.id).exists()


@pytest.mark.django_db(transaction=True)
def test_acquisition_is_bounded_and_emits_minimal_outbox(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )

    leases = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)

    assert len(leases) == 1
    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.DISPATCHED
    with tenant_atomic(tenant.id):
        event = OutboxEvent.objects.get(
            topic="identity.cleanup.passcode_change.requested", tenant_id=tenant.id
        )
    assert set(event.payload) == {"claim_id", "tenant_id", "fencing_generation"}
    assert event.payload["claim_id"] == str(claim.id)


@pytest.mark.django_db(transaction=True)
def test_valid_owner_can_run_and_complete_once(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    lease = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]

    assert begin_claim(
        claim_id=lease.claim_id,
        tenant_id=tenant.id,
        owner_token=lease.owner_token,
        generation=lease.fencing_generation,
    )
    assert complete_claim(
        claim_id=lease.claim_id,
        tenant_id=tenant.id,
        owner_token=lease.owner_token,
        generation=lease.fencing_generation,
    )
    assert not begin_claim(
        claim_id=lease.claim_id,
        tenant_id=tenant.id,
        owner_token=lease.owner_token,
        generation=lease.fencing_generation,
    )
    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.SUCCEEDED


@pytest.mark.django_db(transaction=True)
def test_stale_owner_is_rejected(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    lease = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]

    assert not begin_claim(
        claim_id=claim.id,
        tenant_id=tenant.id,
        owner_token=uuid4(),
        generation=lease.fencing_generation,
    )


@pytest.mark.django_db(transaction=True)
def test_expired_reclaim_fences_old_owner(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    old_lease = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]
    with tenant_atomic(tenant.id):
        CleanupWorkClaim.objects.filter(pk=claim.id).update(
            lease_expires_at=timezone.now() - timedelta(minutes=1)
        )

    new_lease = reclaim_expired_claim(claim_id=claim.id, tenant_id=tenant.id)

    assert new_lease is not None
    assert new_lease.owner_token != old_lease.owner_token
    assert new_lease.fencing_generation == old_lease.fencing_generation + 1
    assert not begin_claim(
        claim_id=claim.id,
        tenant_id=tenant.id,
        owner_token=old_lease.owner_token,
        generation=old_lease.fencing_generation,
    )


@pytest.mark.django_db(transaction=True)
def test_failure_retries_then_dead(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    settings.CODESHO_CLEANUP_MAX_RETRIES = 0
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    lease = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]

    assert fail_claim(
        claim_id=claim.id,
        tenant_id=tenant.id,
        owner_token=lease.owner_token,
        generation=lease.fencing_generation,
        failure_code="cleanup_error",
    ) == CleanupWorkClaim.State.DEAD
    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.last_failure_code == "cleanup_error"


@pytest.mark.django_db(transaction=True)
def test_outbox_failure_rolls_back_claim_transition(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )

    with patch(
        "config.cleanup_claims.append_outbox_event",
        side_effect=RuntimeError("simulated outbox failure"),
    ), pytest.raises(RuntimeError, match="simulated outbox failure"):
        acquire_cleanup_claims(tenant_id=tenant.id, limit=1)

    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.PENDING
    with tenant_atomic(tenant.id):
        assert not OutboxEvent.objects.filter(tenant_id=tenant.id).exists()


@pytest.mark.django_db(transaction=True)
def test_retry_limit_one_then_dead(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    settings.CODESHO_CLEANUP_MAX_RETRIES = 1
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    first = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]
    assert fail_claim(
        claim_id=claim.id,
        tenant_id=tenant.id,
        owner_token=first.owner_token,
        generation=first.fencing_generation,
        failure_code="cleanup_error",
    ) == CleanupWorkClaim.State.RETRYABLE
    with tenant_atomic(tenant.id):
        CleanupWorkClaim.objects.filter(pk=claim.id).update(
            next_eligible_at=timezone.now() - timedelta(minutes=1)
        )
    second = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]
    assert fail_claim(
        claim_id=claim.id,
        tenant_id=tenant.id,
        owner_token=second.owner_token,
        generation=second.fencing_generation,
        failure_code="cleanup_error",
    ) == CleanupWorkClaim.State.DEAD
    assert acquire_cleanup_claims(tenant_id=tenant.id, limit=1) == []


@pytest.mark.django_db(transaction=True)
def test_lease_expiry_equal_to_db_time_is_reclaimable(settings, tenant):
    require_postgres()
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    lease = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]
    boundary = timezone.now()
    with tenant_atomic(tenant.id):
        CleanupWorkClaim.objects.filter(pk=claim.id).update(lease_expires_at=boundary)

    with patch("config.cleanup_claims._db_now", return_value=boundary):
        reclaimed = reclaim_expired_claim(claim_id=claim.id, tenant_id=tenant.id)

    assert reclaimed is not None
    assert reclaimed.owner_token != lease.owner_token


@pytest.mark.django_db(transaction=True)
def test_actual_cleanup_task_failure_retries_then_dead(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    settings.CODESHO_CLEANUP_MAX_RETRIES = 1
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    first = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]
    task_kwargs = {
        "tenant_id": str(tenant.id),
        "claim_id": str(claim.id),
        "fencing_generation": first.fencing_generation,
        "owner_token": str(first.owner_token),
    }

    with patch(
        "modules.identity.tasks.cleanup_current_tenant",
        side_effect=RuntimeError("controlled cleanup failure"),
    ), pytest.raises(RuntimeError, match="controlled cleanup failure"):
        run_cleanup_claim_task.apply(kwargs=task_kwargs, throw=True)

    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.RETRYABLE
    assert claim.retry_count == 1
    assert claim.owner_token is None
    assert claim.lease_expires_at is None
    assert claim.last_failure_code == "cleanup_error"
    assert "controlled cleanup failure" not in str(claim.last_failure_code)

    with tenant_atomic(tenant.id):
        CleanupWorkClaim.objects.filter(pk=claim.id).update(
            next_eligible_at=timezone.now() - timedelta(minutes=1)
        )
    second = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)[0]
    task_kwargs.update(
        fencing_generation=second.fencing_generation,
        owner_token=str(second.owner_token),
    )
    with patch(
        "modules.identity.tasks.cleanup_current_tenant",
        side_effect=RuntimeError("controlled cleanup failure"),
    ), pytest.raises(RuntimeError, match="controlled cleanup failure"):
        run_cleanup_claim_task.apply(kwargs=task_kwargs, throw=True)

    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.DEAD
    assert claim.retry_count == 2


@pytest.mark.django_db(transaction=True)
def test_postgres_claim_rls_and_runtime_privileges(runtime_connection, tenant, settings):
    require_postgres()
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM identity_cleanupworkclaim")
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(tenant.id)])
        cursor.execute(
            "SELECT count(*) FROM identity_cleanupworkclaim WHERE id = %s", [claim.id]
        )
        assert cursor.fetchone()[0] == 1
        cursor.execute(
            "SELECT has_table_privilege(current_user, "
            "'identity_cleanupworkclaim', 'DELETE'), "
            "has_table_privilege(current_user, "
            "'identity_cleanupworkclaim', 'TRUNCATE')"
        )
        assert cursor.fetchone() == (False, False)
        cursor.execute(
            "SELECT relforcerowsecurity FROM pg_class "
            "WHERE oid = 'identity_cleanupworkclaim'::regclass"
        )
        assert cursor.fetchone()[0] is True


@pytest.mark.django_db(transaction=True)
def test_postgres_competing_claimers_do_not_double_own(settings, tenant):
    require_postgres()
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )
    start = Barrier(2)
    results: list[object] = []

    def acquire() -> None:
        close_old_connections()
        try:
            start.wait(timeout=10)
            results.append(acquire_cleanup_claims(tenant_id=UUID(str(tenant.id)), limit=1))
        except BaseException as exc:  # pragma: no cover - asserted by parent
            results.append(exc)
        finally:
            close_old_connections()

    first, second = Thread(target=acquire), Thread(target=acquire)
    first.start()
    second.start()
    first.join(timeout=20)
    second.join(timeout=20)
    assert not first.is_alive() and not second.is_alive()
    assert all(not isinstance(result, BaseException) for result in results)
    assert sum(bool(result) for result in results) == 1
    with tenant_atomic(tenant.id):
        claim.refresh_from_db()
    assert claim.fencing_generation == 1
