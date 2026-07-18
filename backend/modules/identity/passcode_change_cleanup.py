"""Tenant-scoped, retry-safe lifecycle maintenance for passcode challenges."""

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
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@dataclass(frozen=True, slots=True)
class CleanupResult:
    expired: int
    deleted: int


def _database_now() -> datetime:
    """Read PostgreSQL's transaction timestamp inside the tenant transaction."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT CURRENT_TIMESTAMP")
        value = cursor.fetchone()[0]
    if isinstance(value, str):  # SQLite test backend only.
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timezone.is_naive(value):
        return timezone.make_aware(value, UTC)
    return cast(datetime, value)


def _expiry_metadata(
    challenge: PasscodeChangeChallenge, credential: PasscodeCredential, user: User
) -> PasscodeChangeAuditMetadata:
    stable = f"codesho:passcode-change-expiry:{challenge.id}"
    return PasscodeChangeAuditMetadata(
        event_id=uuid5(NAMESPACE_URL, stable),
        correlation_id=uuid5(NAMESPACE_URL, f"{stable}:correlation"),
        tenant_id=challenge.tenant_id,
        subject_user_id=user.id,
        actor_user_id=user.id,
        credential_version=credential.credential_version,
        idempotency_key=f"passcode-change:expire:{challenge.id}",
    )


def cleanup_passcode_change_challenges(
    *, tenant: Tenant, batch_size: int | None = None
) -> CleanupResult:
    """Expire at most one locked batch, then remove only aged terminal metadata.

    The caller must supply one tenant; there is intentionally no global task or
    schedule. Retrying is safe because an expired row is never selected again
    and audit insertion uses a stable idempotency key.
    """
    limit = batch_size if batch_size is not None else settings.PASSCODE_CHANGE_CLEANUP_BATCH_SIZE
    if not isinstance(limit, int) or not 1 <= limit <= 500:
        raise ValueError("batch_size must be between 1 and 500")

    with tenant_atomic(tenant.id), transaction.atomic():
        now = _database_now()
        expired = list(
            PasscodeChangeChallenge.objects.select_for_update(skip_locked=True)
            .filter(
                tenant=tenant,
                state=PasscodeChangeChallenge.State.ACTIVE,
                expires_at__lte=now,
            )
            .order_by("expires_at", "id")[:limit]
        )
        for challenge in expired:
            credential = PasscodeCredential.objects.select_for_update().get(
                pk=challenge.credential_id
            )
            user = User.objects.get(pk=credential.user_id)
            challenge.state = PasscodeChangeChallenge.State.EXPIRED
            challenge.secret_digest = None
            challenge.expired_at = now
            challenge.save(update_fields=["state", "secret_digest", "expired_at"])
            append_security_event(
                passcode_change_challenge_expired(_expiry_metadata(challenge, credential, user))
            )

        cutoff = now - timedelta(days=settings.PASSCODE_CHANGE_TERMINAL_RETENTION_DAYS)
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT codesho.delete_expired_passcode_change_challenges(%s, %s, %s)",
                    [tenant.id, cutoff, limit],
                )
                deleted = cursor.fetchone()[0]
        else:  # SQLite test backend mirrors the restricted PostgreSQL function.
            terminal = Q(
                state=PasscodeChangeChallenge.State.CONSUMED, consumed_at__lte=cutoff
            ) | Q(
                state=PasscodeChangeChallenge.State.REVOKED, revoked_at__lte=cutoff
            ) | Q(
                state=PasscodeChangeChallenge.State.EXPIRED, expired_at__lte=cutoff
            )
            deleted, _ = (
                PasscodeChangeChallenge.objects.filter(tenant=tenant).filter(terminal).delete()
            )
    return CleanupResult(expired=len(expired), deleted=int(deleted))
