from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from django.db import DatabaseError, connection, transaction


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
    AUTHENTICATION_SUCCEEDED = "authentication_succeeded"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHENTICATION_BLOCKED = "authentication_blocked"
    SESSION_LOGGED_OUT = "session_logged_out"
    PASSCODE_CHANGE_CHALLENGE_ISSUED = "passcode_change_challenge_issued"
    PASSCODE_CHANGE_CHALLENGE_REVOKED = "passcode_change_challenge_revoked"
    PASSCODE_CHANGE_CHALLENGE_CONSUMED = "passcode_change_challenge_consumed"
    PASSCODE_CHANGE_CHALLENGE_EXPIRED = "passcode_change_challenge_expired"
    PASSCODE_CHANGE_REJECTED = "passcode_change_rejected"


class SecurityEventOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    DETECTED = "detected"


class ReasonCode(StrEnum):
    """Approved, non-sensitive classifications for a security audit event."""

    CREDENTIAL_CREATED = "credential_created"
    CREDENTIAL_CHANGED = "credential_changed"
    VERIFICATION_MISMATCH = "verification_mismatch"
    LOCK_THRESHOLD_REACHED = "lock_threshold_reached"
    LOCK_CLEARED = "lock_cleared"
    ABUSE_THRESHOLD_REACHED = "abuse_threshold_reached"
    TEMPORARY_CREDENTIAL_ISSUED = "temporary_credential_issued"
    TEMPORARY_CREDENTIAL_CONSUMED = "temporary_credential_consumed"
    GUARDIAN_RESET_REQUESTED = "guardian_reset_requested"
    GUARDIAN_RESET_CONFIRMED = "guardian_reset_confirmed"
    LOGIN_SUCCEEDED = "login_succeeded"
    LOGIN_FAILED = "login_failed"
    LOGIN_BLOCKED = "login_blocked"
    SESSION_LOGGED_OUT = "session_logged_out"
    PASSCODE_CHANGE_REQUIRED = "passcode_change_required"
    CHALLENGE_ISSUED = "challenge_issued"
    CHALLENGE_SUPERSEDED = "challenge_superseded"
    CHALLENGE_CONSUMED = "challenge_consumed"
    CHALLENGE_EXPIRED = "challenge_expired"
    CHALLENGE_INVALID = "challenge_invalid"
    PASSCODE_SAME_AS_CURRENT = "passcode_same_as_current"
    CHALLENGE_REVOKED_PEPPER_ROTATION = "challenge_revoked_pepper_rotation"


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
    reason_code: ReasonCode | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class AppendAuditResult:
    event_id: UUID | None
    created: bool


@dataclass(frozen=True, slots=True)
class PasscodeChangeAuditMetadata:
    """The sole permitted metadata surface for dormant challenge producers."""

    event_id: UUID
    correlation_id: UUID
    tenant_id: UUID
    subject_user_id: UUID
    credential_version: int
    actor_user_id: UUID | None = None
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, UUID)
            for value in (
                self.event_id,
                self.correlation_id,
                self.tenant_id,
                self.subject_user_id,
            )
        ) or (self.actor_user_id is not None and not isinstance(self.actor_user_id, UUID)):
            raise ValueError("invalid passcode change audit metadata")
        if not isinstance(self.credential_version, int) or self.credential_version < 1:
            raise ValueError("invalid passcode change audit metadata")
        if self.idempotency_key is not None and (
            not isinstance(self.idempotency_key, str)
            or not self.idempotency_key
            or len(self.idempotency_key) > 255
        ):
            raise ValueError("invalid passcode change audit metadata")


def _passcode_change_event(
    metadata: PasscodeChangeAuditMetadata,
    event_type: SecurityEventType,
    outcome: SecurityEventOutcome,
    reason_code: ReasonCode,
) -> SecurityAuditEvent:
    if not isinstance(metadata, PasscodeChangeAuditMetadata):
        raise ValueError("invalid passcode change audit metadata")
    return SecurityAuditEvent(
        event_id=metadata.event_id,
        event_type=event_type,
        outcome=outcome,
        reason_code=reason_code,
        correlation_id=metadata.correlation_id,
        tenant_id=metadata.tenant_id,
        subject_user_id=metadata.subject_user_id,
        actor_user_id=metadata.actor_user_id,
        credential_version=metadata.credential_version,
        idempotency_key=metadata.idempotency_key,
    )


def passcode_change_challenge_issued(metadata: PasscodeChangeAuditMetadata) -> SecurityAuditEvent:
    return _passcode_change_event(
        metadata,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_ISSUED,
        SecurityEventOutcome.SUCCESS,
        ReasonCode.CHALLENGE_ISSUED,
    )


def passcode_change_challenge_superseded(
    metadata: PasscodeChangeAuditMetadata,
) -> SecurityAuditEvent:
    return _passcode_change_event(
        metadata,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_REVOKED,
        SecurityEventOutcome.DETECTED,
        ReasonCode.CHALLENGE_SUPERSEDED,
    )


def passcode_change_challenge_consumed(metadata: PasscodeChangeAuditMetadata) -> SecurityAuditEvent:
    return _passcode_change_event(
        metadata,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_CONSUMED,
        SecurityEventOutcome.SUCCESS,
        ReasonCode.CHALLENGE_CONSUMED,
    )


def passcode_change_challenge_expired(metadata: PasscodeChangeAuditMetadata) -> SecurityAuditEvent:
    return _passcode_change_event(
        metadata,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_EXPIRED,
        SecurityEventOutcome.DETECTED,
        ReasonCode.CHALLENGE_EXPIRED,
    )


def passcode_change_rejected(
    metadata: PasscodeChangeAuditMetadata, reason: ReasonCode
) -> SecurityAuditEvent:
    if reason not in {ReasonCode.CHALLENGE_INVALID, ReasonCode.PASSCODE_SAME_AS_CURRENT}:
        raise ValueError("invalid passcode change audit reason")
    return _passcode_change_event(
        metadata,
        SecurityEventType.PASSCODE_CHANGE_REJECTED,
        SecurityEventOutcome.FAILURE,
        reason,
    )


def passcode_change_challenge_revoked_for_pepper_rotation(
    metadata: PasscodeChangeAuditMetadata,
) -> SecurityAuditEvent:
    return _passcode_change_event(
        metadata,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_REVOKED,
        SecurityEventOutcome.DETECTED,
        ReasonCode.CHALLENGE_REVOKED_PEPPER_ROTATION,
    )


def append_security_event(event: SecurityAuditEvent) -> AppendAuditResult:
    """Append one immutable security event without requiring runtime read access."""
    if event.reason_code is not None and not isinstance(event.reason_code, ReasonCode):
        raise ValueError("reason_code must be an approved ReasonCode")

    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT audit.append_identity_security_event(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    event.event_id,
                    event.event_type.value,
                    event.outcome.value,
                    event.reason_code.value if event.reason_code is not None else None,
                    event.subject_user_id,
                    event.actor_user_id,
                    event.tenant_id,
                    event.credential_version,
                    event.correlation_id,
                    event.idempotency_key,
                ),
            )
            created = cursor.fetchone()[0]
    except DatabaseError as exc:
        raise SecurityAuditError("security audit append failed") from exc
    return AppendAuditResult(event_id=event.event_id if created else None, created=created)
