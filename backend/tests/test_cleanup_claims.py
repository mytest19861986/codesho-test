from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from config.cleanup_claims import (
    acquire_cleanup_claims,
    begin_claim,
    complete_claim,
    create_pending_claim,
)
from modules.identity.models import CleanupWorkClaim
from modules.platform_event.models import OutboxEvent
from modules.platform_tenant.models import Tenant


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(slug=f"claim-{uuid4().hex[:8]}", name="Claim tenant")


@pytest.mark.django_db(transaction=True)
def test_claiming_disabled_is_fail_closed(settings, tenant):
    claim = create_pending_claim(tenant_id=tenant.id)
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = False

    assert acquire_cleanup_claims(tenant_id=tenant.id) == []
    claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.PENDING
    assert not OutboxEvent.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_acquisition_is_bounded_and_emits_minimal_outbox(settings, tenant):
    settings.CODESHO_CLEANUP_CLAIMING_ENABLED = True
    claim = create_pending_claim(
        tenant_id=tenant.id, next_eligible_at=timezone.now() - timedelta(minutes=1)
    )

    leases = acquire_cleanup_claims(tenant_id=tenant.id, limit=1)

    assert len(leases) == 1
    claim.refresh_from_db()
    assert claim.state == CleanupWorkClaim.State.DISPATCHED
    event = OutboxEvent.objects.get(topic="identity.cleanup.passcode_change.requested")
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
