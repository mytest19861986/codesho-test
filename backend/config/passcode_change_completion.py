"""Atomic completion of an issued forced-passcode-change challenge."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from django.db import DatabaseError
from django.utils import timezone

from modules.identity.abuse import (
    AbuseReason,
    CompletionDimensions,
    CompletionSignals,
    preflight_completion_attempt,
    record_failed_completion_attempt,
    record_successful_completion_attempt,
)
from modules.identity.challenge import verify_challenge_secret
from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.identity.passcodes import replace_locked_passcode, verify_passcode
from modules.platform_event.security_audit import (
    PasscodeChangeAuditMetadata,
    ReasonCode,
    SecurityAuditError,
    SecurityAuditEvent,
    SecurityEventOutcome,
    SecurityEventType,
    append_security_event,
    passcode_change_challenge_consumed,
    passcode_change_challenge_expired,
    passcode_change_rejected,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


class CompletionStatus(StrEnum):
    SUCCESS = "success"
    INVALID = "invalid"
    EXPIRED = "expired"
    SAME_AS_CURRENT = "same_as_current"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"


@dataclass(frozen=True, slots=True)
class CompletionResult:
    status: CompletionStatus
    retry_after_seconds: int = 0


def _metadata(
    tenant: Tenant,
    user: User,
    credential: PasscodeCredential,
    correlation_id: UUID,
    challenge_id: UUID,
    event_type: SecurityEventType,
) -> PasscodeChangeAuditMetadata:
    return PasscodeChangeAuditMetadata(
        event_id=uuid4(),
        correlation_id=correlation_id,
        tenant_id=tenant.id,
        subject_user_id=user.id,
        actor_user_id=user.id,
        credential_version=credential.credential_version,
        idempotency_key=f"passcode-change:{event_type.value}:{challenge_id}",
    )


def complete_forced_passcode_change(
    *,
    tenant: Tenant,
    selector: UUID,
    secret: bytes,
    new_passcode: str,
    client_ip: str,
    device_id: str | None,
) -> CompletionResult:
    """Consume exactly one valid challenge; no session is created here."""
    correlation_id = uuid4()
    try:
        with tenant_atomic(tenant.id):
            candidate = PasscodeChangeChallenge.objects.filter(
                tenant=tenant,
                selector=selector,
                purpose=PasscodeChangeChallenge.Purpose.FORCED_PASSCODE_CHANGE,
            ).first()
            if candidate is None:
                decision = record_failed_completion_attempt(
                    CompletionSignals(client_ip, device_id, global_subject=str(selector)),
                    CompletionDimensions(ip=True, device=True, global_detection=True),
                )
                if decision.reason is AbuseReason.BACKEND_UNAVAILABLE:
                    return CompletionResult(CompletionStatus.UNAVAILABLE)
                if not decision.allowed:
                    return CompletionResult(
                        CompletionStatus.RATE_LIMITED, decision.retry_after_seconds
                    )
                return CompletionResult(CompletionStatus.INVALID)
            credential = PasscodeCredential.objects.select_for_update().get(
                pk=candidate.credential_id
            )
            challenge = PasscodeChangeChallenge.objects.select_for_update().get(pk=candidate.pk)
            user = User.objects.get(pk=credential.user_id)
            public_signals = CompletionSignals(client_ip, device_id, global_subject=str(selector))
            scoped_signals = CompletionSignals(
                client_ip,
                device_id,
                account_subject=f"{tenant.id}:{user.id}",
                challenge_subject=str(challenge.id),
            )
            preflight = preflight_completion_attempt(public_signals)
            if preflight.reason is AbuseReason.BACKEND_UNAVAILABLE:
                return CompletionResult(CompletionStatus.UNAVAILABLE)
            if not preflight.allowed:
                return CompletionResult(
                    CompletionStatus.RATE_LIMITED, preflight.retry_after_seconds
                )
            now = timezone.now()
            if (
                challenge.state == PasscodeChangeChallenge.State.ACTIVE
                and challenge.expires_at <= now
            ):
                decision = record_failed_completion_attempt(
                    public_signals,
                    CompletionDimensions(ip=True, device=True, global_detection=True),
                )
                if decision.reason is AbuseReason.BACKEND_UNAVAILABLE:
                    return CompletionResult(CompletionStatus.UNAVAILABLE)
                if not decision.allowed:
                    return CompletionResult(
                        CompletionStatus.RATE_LIMITED, decision.retry_after_seconds
                    )
                challenge.state = PasscodeChangeChallenge.State.EXPIRED
                challenge.secret_digest = None
                challenge.expired_at = now
                challenge.save(update_fields=["state", "secret_digest", "expired_at"])
                append_security_event(
                    passcode_change_challenge_expired(
                        _metadata(
                            tenant,
                            user,
                            credential,
                            correlation_id,
                            challenge.id,
                            SecurityEventType.PASSCODE_CHANGE_CHALLENGE_EXPIRED,
                        )
                    )
                )
                return CompletionResult(CompletionStatus.EXPIRED)
            if (
                challenge.state != PasscodeChangeChallenge.State.ACTIVE
                or challenge.credential_version != credential.credential_version
                or challenge.secret_digest is None
            ):
                decision = record_failed_completion_attempt(
                    public_signals,
                    CompletionDimensions(ip=True, device=True, global_detection=True),
                )
                if decision.reason is AbuseReason.BACKEND_UNAVAILABLE:
                    return CompletionResult(CompletionStatus.UNAVAILABLE)
                if not decision.allowed:
                    return CompletionResult(
                        CompletionStatus.RATE_LIMITED, decision.retry_after_seconds
                    )
                return CompletionResult(CompletionStatus.INVALID)
            if not verify_challenge_secret(
                secret, bytes(challenge.secret_digest), challenge.pepper_id
            ):
                decision = record_failed_completion_attempt(
                    public_signals,
                    CompletionDimensions(ip=True, device=True, global_detection=True),
                )
                if decision.reason is AbuseReason.BACKEND_UNAVAILABLE:
                    return CompletionResult(CompletionStatus.UNAVAILABLE)
                if not decision.allowed:
                    return CompletionResult(
                        CompletionStatus.RATE_LIMITED, decision.retry_after_seconds
                    )
                return CompletionResult(CompletionStatus.INVALID)
            scoped_preflight = preflight_completion_attempt(scoped_signals)
            if scoped_preflight.reason is AbuseReason.BACKEND_UNAVAILABLE:
                return CompletionResult(CompletionStatus.UNAVAILABLE)
            if not scoped_preflight.allowed:
                return CompletionResult(
                    CompletionStatus.RATE_LIMITED, scoped_preflight.retry_after_seconds
                )
            if verify_passcode(user, new_passcode).valid:
                append_security_event(
                    passcode_change_rejected(
                        _metadata(
                            tenant,
                            user,
                            credential,
                            correlation_id,
                            challenge.id,
                            SecurityEventType.PASSCODE_CHANGE_REJECTED,
                        ),
                        ReasonCode.PASSCODE_SAME_AS_CURRENT,
                    )
                )
                decision = record_failed_completion_attempt(
                    scoped_signals, CompletionDimensions(account=True, challenge=True)
                )
                if decision.reason is AbuseReason.BACKEND_UNAVAILABLE:
                    raise ValueError("completion abuse unavailable")
                if not decision.allowed:
                    return CompletionResult(
                        CompletionStatus.RATE_LIMITED, decision.retry_after_seconds
                    )
                return CompletionResult(CompletionStatus.SAME_AS_CURRENT)
            replace_locked_passcode(credential, new_passcode)
            append_security_event(
                SecurityAuditEvent(
                    event_id=uuid4(),
                    event_type=SecurityEventType.PASSCODE_CHANGED,
                    outcome=SecurityEventOutcome.SUCCESS,
                    reason_code=ReasonCode.CREDENTIAL_CHANGED,
                    correlation_id=correlation_id,
                    tenant_id=tenant.id,
                    subject_user_id=user.id,
                    actor_user_id=user.id,
                    credential_version=credential.credential_version,
                    idempotency_key=(
                        f"passcode-change:{SecurityEventType.PASSCODE_CHANGED.value}:"
                        f"{challenge.id}"
                    ),
                )
            )
            cleared = record_successful_completion_attempt(scoped_signals)
            if cleared.reason is AbuseReason.BACKEND_UNAVAILABLE:
                raise ValueError("completion abuse unavailable")
            challenge.state = PasscodeChangeChallenge.State.CONSUMED
            challenge.secret_digest = None
            challenge.consumed_at = now
            challenge.save(update_fields=["state", "secret_digest", "consumed_at"])
            append_security_event(
                passcode_change_challenge_consumed(
                    _metadata(
                        tenant,
                        user,
                        credential,
                        correlation_id,
                        challenge.id,
                        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_CONSUMED,
                    )
                )
            )
    except (DatabaseError, SecurityAuditError, ValueError):
        return CompletionResult(CompletionStatus.UNAVAILABLE)
    return CompletionResult(CompletionStatus.SUCCESS)
