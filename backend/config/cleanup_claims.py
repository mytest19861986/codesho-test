"""Tenant-safe claim, lease and fencing operations for cleanup work."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from modules.identity.models import CleanupWorkClaim
from modules.platform_event.services import append_outbox_event
from modules.platform_tenant.context import current_tenant_id, tenant_atomic

TOPIC = "identity.cleanup.passcode_change.requested"
ROUTING_KEYS = frozenset({"claim_id", "tenant_id", "fencing_generation"})


def current_claim_tenant_id() -> UUID | None:
    return current_tenant_id()


@dataclass(frozen=True, slots=True)
class ClaimLease:
    claim_id: UUID
    tenant_id: UUID
    owner_token: UUID
    fencing_generation: int
    lease_expires_at: datetime


def _db_now() -> datetime:
    with connection.cursor() as cursor:
        cursor.execute("SELECT CURRENT_TIMESTAMP")
        value = cursor.fetchone()[0]
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timezone.is_naive(value):
        return timezone.make_aware(value, UTC)
    return cast(datetime, value)


def _validate_limit(limit: int) -> int:
    if not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    return limit


def acquire_cleanup_claims(*, tenant_id: UUID, limit: int | None = None) -> list[ClaimLease]:
    """Claim due work for exactly one tenant and append dispatch intents atomically."""
    if not settings.CODESHO_CLEANUP_CLAIMING_ENABLED:
        return []
    tenant_id = UUID(str(tenant_id))
    configured_limit = limit if limit is not None else settings.CODESHO_CLEANUP_CLAIMS_PER_CYCLE
    limit = _validate_limit(configured_limit)
    leases: list[ClaimLease] = []
    with tenant_atomic(tenant_id), transaction.atomic():
        now = _db_now()
        claims = list(
            CleanupWorkClaim.objects.select_for_update(skip_locked=True)
            .filter(
                tenant_id=tenant_id,
                kind=CleanupWorkClaim.Kind.PASSCODE_CHANGE_CHALLENGE_CLEANUP,
                state__in=[CleanupWorkClaim.State.PENDING, CleanupWorkClaim.State.RETRYABLE],
                next_eligible_at__lte=now,
            )
            .order_by("next_eligible_at", "id")[:limit]
        )
        for claim in claims:
            owner = uuid.uuid4()
            generation = claim.fencing_generation + 1
            expiry = now + timedelta(seconds=settings.CODESHO_CLEANUP_LEASE_SECONDS)
            claim.state = CleanupWorkClaim.State.DISPATCHED
            claim.owner_token = owner
            claim.fencing_generation = generation
            claim.claimed_at = now
            claim.lease_expires_at = expiry
            claim.save(
                update_fields=[
                    "state",
                    "owner_token",
                    "fencing_generation",
                    "claimed_at",
                    "lease_expires_at",
                    "updated_at",
                ]
            )
            append_outbox_event(
                topic=TOPIC,
                aggregate_type="cleanup_claim",
                aggregate_id=str(claim.id),
                tenant_id=tenant_id,
                payload={
                    "claim_id": str(claim.id),
                    "tenant_id": str(tenant_id),
                    "fencing_generation": generation,
                },
            )
            leases.append(ClaimLease(claim.id, tenant_id, owner, generation, expiry))
    return leases


def _owned_claim(
    *, claim_id: UUID, tenant_id: UUID, owner_token: UUID, generation: int
) -> CleanupWorkClaim:
    return CleanupWorkClaim.objects.select_for_update().get(
        id=claim_id,
        tenant_id=tenant_id,
        owner_token=owner_token,
        fencing_generation=generation,
    )


def renew_claim(*, claim_id: UUID, tenant_id: UUID, owner_token: UUID, generation: int) -> bool:
    with tenant_atomic(UUID(str(tenant_id))), transaction.atomic():
        now = _db_now()
        try:
            claim = _owned_claim(
                claim_id=claim_id,
                tenant_id=tenant_id,
                owner_token=owner_token,
                generation=generation,
            )
        except CleanupWorkClaim.DoesNotExist:
            return False
        if claim.state not in {
            CleanupWorkClaim.State.CLAIMED,
            CleanupWorkClaim.State.DISPATCHED,
            CleanupWorkClaim.State.RUNNING,
        }:
            return False
        if claim.lease_expires_at is None or claim.lease_expires_at <= now:
            return False
        claim.lease_expires_at = now + timedelta(seconds=settings.CODESHO_CLEANUP_LEASE_SECONDS)
        claim.save(update_fields=["lease_expires_at", "updated_at"])
        return True


def begin_claim(*, claim_id: UUID, tenant_id: UUID, owner_token: UUID, generation: int) -> bool:
    with tenant_atomic(UUID(str(tenant_id))), transaction.atomic():
        now = _db_now()
        try:
            claim = _owned_claim(
                claim_id=claim_id,
                tenant_id=tenant_id,
                owner_token=owner_token,
                generation=generation,
            )
        except CleanupWorkClaim.DoesNotExist:
            return False
        if claim.state == CleanupWorkClaim.State.SUCCEEDED:
            return False
        if claim.state not in {CleanupWorkClaim.State.CLAIMED, CleanupWorkClaim.State.DISPATCHED}:
            return False
        if claim.lease_expires_at is None or claim.lease_expires_at <= now:
            return False
        claim.state = CleanupWorkClaim.State.RUNNING
        claim.started_at = now
        claim.save(update_fields=["state", "started_at", "updated_at"])
        return True


def complete_claim(*, claim_id: UUID, tenant_id: UUID, owner_token: UUID, generation: int) -> bool:
    with tenant_atomic(UUID(str(tenant_id))), transaction.atomic():
        now = _db_now()
        try:
            claim = _owned_claim(
                claim_id=claim_id,
                tenant_id=tenant_id,
                owner_token=owner_token,
                generation=generation,
            )
        except CleanupWorkClaim.DoesNotExist:
            return False
        if claim.state == CleanupWorkClaim.State.SUCCEEDED:
            return False
        if (
            claim.state != CleanupWorkClaim.State.RUNNING
            or claim.lease_expires_at is None
            or claim.lease_expires_at <= now
        ):
            return False
        claim.state = CleanupWorkClaim.State.SUCCEEDED
        claim.completed_at = now
        claim.owner_token = None
        claim.lease_expires_at = None
        claim.save(
            update_fields=["state", "completed_at", "owner_token", "lease_expires_at", "updated_at"]
        )
        return True


def create_pending_claim(
    *, tenant_id: UUID, next_eligible_at: datetime | None = None
) -> CleanupWorkClaim:
    tenant_id = UUID(str(tenant_id))
    with tenant_atomic(tenant_id), transaction.atomic():
        return CleanupWorkClaim.objects.create(
            tenant_id=tenant_id,
            kind=CleanupWorkClaim.Kind.PASSCODE_CHANGE_CHALLENGE_CLEANUP,
            next_eligible_at=next_eligible_at or _db_now(),
        )
