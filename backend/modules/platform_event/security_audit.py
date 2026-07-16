from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from django.db import IntegrityError, transaction

from .models import IdentitySecurityEvent


class SecurityAuditError(RuntimeError):
    """Raised when a security audit event cannot be durably appended."""


class SecurityEventType(StrEnum):
    PASSCODE_CREATED = "passcode_created"
    PASSCODE_CHANGED = "passcode_changed"
    PASSCODE_VERIFICATION_FAILED = "passcode_verification_failed"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    ABUSE_GLOBAL_ALERT = "abuse_global_alert"
    TEMPORARY_PASSCODE_ISSUED = "temporary_passcode_issued"
    TEMPORARY_PASSCODE_CONSUMED = "temporary_passcode_consumed"
    GUARDIAN_RESET_STARTED = "guardian_reset_started"
    GUARDIAN_RESET_COMPLETED = "guardian_reset_completed"


class SecurityEventOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    DETECTED = "detected"


@dataclass(frozen=True, slots=True)
class SecurityAuditEvent:
    event_id: UUID
    event_type: SecurityEventType
    outcome: SecurityEventOutcome
    correlation_id: UUID
    subject_user_id: UUID | None = None
    actor_user_id: UUID | None = None
    tenant_id: UUID | None = None
    credential_version: int | None = None
    reason_code: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class AppendAuditResult:
    event_id: UUID
    created: bool


def append_security_event(event: SecurityAuditEvent) -> AppendAuditResult:
    """Append one immutable security event, returning an existing idempotent event."""
    try:
        with transaction.atomic():
            created_event = IdentitySecurityEvent.objects.create(
                event_id=event.event_id,
                event_type=event.event_type.value,
                outcome=event.outcome.value,
                reason_code=event.reason_code,
                subject_user_id=event.subject_user_id,
                actor_user_id=event.actor_user_id,
                tenant_id=event.tenant_id,
                credential_version=event.credential_version,
                correlation_id=event.correlation_id,
                idempotency_key=event.idempotency_key,
            )
    except IntegrityError as exc:
        if event.idempotency_key is None:
            raise SecurityAuditError("security audit append failed") from exc
        try:
            existing_event = IdentitySecurityEvent.objects.get(
                idempotency_key=event.idempotency_key
            )
        except IdentitySecurityEvent.DoesNotExist as lookup_exc:
            raise SecurityAuditError("security audit append failed") from lookup_exc
        return AppendAuditResult(event_id=existing_event.event_id, created=False)
    except Exception as exc:
        raise SecurityAuditError("security audit append failed") from exc
    return AppendAuditResult(event_id=created_event.event_id, created=True)
