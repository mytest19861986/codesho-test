"""Application orchestration for tenant-scoped passcode challenge cleanup."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import NAMESPACE_URL, uuid5

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone

from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.platform_event.security_audit import (
    PasscodeChangeAuditMetadata,
    append_security_event,
    passcode_change_challenge_expired,
)
from modules.platform_tenant.context import current_tenant_id, tenant_atomic
from modules.platform_tenant.models import Tenant
from modules.platform_tenant.tasks import BaseTenantTask

__all__ = [
    "BaseTenantTask",
    "CleanupResult",
    "cleanup_current_tenant",
    "cleanup_passcode_change_challenges",
]


@dataclass(frozen=True, slots=True)
class CleanupResult:
    expired: int
    deleted: int


def _database_now() -> datetime:
    with connection.cursor() as cursor:
        cursor.execute("SELECT CURRENT_TIMESTAMP")
        value = cursor.fetchone()[0]
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timezone.is_naive(value):
        return timezone.make_aware(value, UTC)
    return cast(datetime, value)


def _metadata(
    c: PasscodeChangeChallenge, credential: PasscodeCredential, user: User
) -> PasscodeChangeAuditMetadata:
    stable = f"codesho:passcode-change-expiry:{c.id}"
    return PasscodeChangeAuditMetadata(
        event_id=uuid5(NAMESPACE_URL, stable),
        correlation_id=uuid5(NAMESPACE_URL, f"{stable}:correlation"),
        tenant_id=c.tenant_id,
        subject_user_id=user.id,
        actor_user_id=user.id,
        credential_version=credential.credential_version,
        idempotency_key=f"passcode-change:expire:{c.id}",
    )


def cleanup_passcode_change_challenges(
    *, tenant: Tenant, batch_size: int | None = None
) -> CleanupResult:
    limit = batch_size if batch_size is not None else settings.PASSCODE_CHANGE_CLEANUP_BATCH_SIZE
    if not isinstance(limit, int) or not 1 <= limit <= 500:
        raise ValueError("batch_size must be between 1 and 500")
    with tenant_atomic(tenant.id), transaction.atomic():
        now = _database_now()
        expired = list(
            PasscodeChangeChallenge.objects.select_for_update(skip_locked=True)
            .filter(tenant=tenant, state=PasscodeChangeChallenge.State.ACTIVE, expires_at__lte=now)
            .order_by("expires_at", "id")[:limit]
        )
        for c in expired:
            credential = PasscodeCredential.objects.select_for_update().get(pk=c.credential_id)
            user = User.objects.get(pk=credential.user_id)
            c.state, c.secret_digest, c.expired_at = (
                PasscodeChangeChallenge.State.EXPIRED,
                None,
                now,
            )
            c.save(update_fields=["state", "secret_digest", "expired_at"])
            append_security_event(passcode_change_challenge_expired(_metadata(c, credential, user)))
        cutoff = now - timedelta(days=settings.PASSCODE_CHANGE_TERMINAL_RETENTION_DAYS)
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT codesho.delete_expired_passcode_change_challenges(%s, %s, %s)",
                    [tenant.id, cutoff, limit],
                )
                deleted = cursor.fetchone()[0]
        else:
            terminal = (
                Q(state=PasscodeChangeChallenge.State.CONSUMED, consumed_at__lte=cutoff)
                | Q(state=PasscodeChangeChallenge.State.REVOKED, revoked_at__lte=cutoff)
                | Q(state=PasscodeChangeChallenge.State.EXPIRED, expired_at__lte=cutoff)
            )
            deleted, _ = (
                PasscodeChangeChallenge.objects.filter(tenant=tenant).filter(terminal).delete()
            )
    return CleanupResult(expired=len(expired), deleted=int(deleted))


def cleanup_current_tenant(*, batch_size: int | None = None) -> CleanupResult:
    tenant_id = current_tenant_id()
    if tenant_id is None:
        raise RuntimeError("tenant context is required")
    return cleanup_passcode_change_challenges(
        tenant=Tenant.objects.get(pk=tenant_id), batch_size=batch_size
    )
