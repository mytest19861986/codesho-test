from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from django.db import IntegrityError, connection, transaction


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
    """Append one immutable security event without requiring runtime read access."""
    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO audit.identity_security_event (
                    event_id, event_type, outcome, reason_code,
                    subject_user_id, actor_user_id, tenant_id,
                    credential_version, correlation_id, idempotency_key
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (idempotency_key) DO NOTHING
                """,
                (
                    event.event_id,
                    event.event_type.value,
                    event.outcome.value,
                    event.reason_code,
                    event.subject_user_id,
                    event.actor_user_id,
                    event.tenant_id,
                    event.credential_version,
                    event.correlation_id,
                    event.idempotency_key,
                ),
            )
            created = cursor.rowcount == 1
    except IntegrityError as exc:
        raise SecurityAuditError("security audit append failed") from exc
    except Exception as exc:
        raise SecurityAuditError("security audit append failed") from exc
    return AppendAuditResult(event_id=event.event_id, created=created)
