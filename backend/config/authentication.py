"""Bounded authentication orchestration for the passcode/session boundary."""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpRequest

from modules.identity.abuse import (
    AbuseReason,
    AttemptSignals,
    preflight_attempt,
    record_failed_attempt,
    record_successful_attempt,
)
from modules.identity.models import PasscodeCredential, User
from modules.identity.passcodes import InvalidPasscode, verify_dummy_passcode, verify_passcode
from modules.platform_event.security_audit import (
    ReasonCode,
    SecurityAuditError,
    SecurityAuditEvent,
    SecurityEventOutcome,
    SecurityEventType,
    append_security_event,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


class LoginStatus(StrEnum):
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    PASSCODE_CHANGE_REQUIRED = "passcode_change_required"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class LoginResult:
    status: LoginStatus
    retry_after_seconds: int = 0


def _idempotency_key(
    *,
    correlation_id: UUID,
    event_type: SecurityEventType,
    tenant_id: UUID,
    user: User | None,
    credential: PasscodeCredential | None,
    deduplicate: bool,
) -> str:
    if deduplicate:
        subject = user.id if user is not None else "anonymous"
        version = credential.credential_version if credential is not None else 0
        bucket = int(time.time()) // settings.PASSCODE_ATTEMPT_WINDOW_SECONDS
        material = f"{event_type.value}:{tenant_id}:{subject}:{version}:{bucket}"
    else:
        material = f"{correlation_id}:{event_type.value}"
    digest = hashlib.sha256(material.encode()).hexdigest()
    return f"auth:{digest}"


def _append(
    *,
    event_type: SecurityEventType,
    outcome: SecurityEventOutcome,
    reason_code: ReasonCode,
    correlation_id: UUID,
    tenant_id: UUID,
    user: User | None = None,
    credential: PasscodeCredential | None = None,
    deduplicate: bool = False,
) -> None:
    append_security_event(
        SecurityAuditEvent(
            event_id=uuid4(),
            event_type=event_type,
            outcome=outcome,
            reason_code=reason_code,
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            subject_user_id=user.id if user is not None else None,
            actor_user_id=user.id if user is not None else None,
            credential_version=credential.credential_version if credential is not None else None,
            idempotency_key=_idempotency_key(
                correlation_id=correlation_id,
                event_type=event_type,
                tenant_id=tenant_id,
                user=user,
                credential=credential,
                deduplicate=deduplicate,
            ),
        )
    )


def _audit_failure(
    *,
    tenant: Tenant,
    user: User | None,
    credential: PasscodeCredential | None,
    correlation_id: UUID,
) -> bool:
    # Unknown principals deliberately do not create durable unbounded audit rows.
    if user is None:
        return True
    try:
        with tenant_atomic(tenant.id):
            _append(
                event_type=SecurityEventType.AUTHENTICATION_FAILED,
                outcome=SecurityEventOutcome.FAILURE,
                reason_code=ReasonCode.LOGIN_FAILED,
                correlation_id=correlation_id,
                tenant_id=tenant.id,
                user=user,
                credential=credential,
                # At most five failure rows are possible before the durable lock;
                # blocks are separately window-deduplicated to bound amplification.
                deduplicate=False,
            )
    except SecurityAuditError:
        return False
    return True


def _audit_block(
    *,
    tenant: Tenant,
    user: User | None,
    credential: PasscodeCredential | None,
    correlation_id: UUID,
) -> bool:
    if user is None:
        return True
    try:
        with tenant_atomic(tenant.id):
            _append(
                event_type=SecurityEventType.AUTHENTICATION_BLOCKED,
                outcome=SecurityEventOutcome.BLOCKED,
                reason_code=ReasonCode.LOGIN_BLOCKED,
                correlation_id=correlation_id,
                tenant_id=tenant.id,
                user=user,
                credential=credential,
                deduplicate=True,
            )
    except SecurityAuditError:
        return False
    return True


def _audit_global_alert(*, tenant: Tenant, correlation_id: UUID) -> bool:
    try:
        with tenant_atomic(tenant.id):
            _append(
                event_type=SecurityEventType.ABUSE_GLOBAL_ALERT,
                outcome=SecurityEventOutcome.DETECTED,
                reason_code=ReasonCode.ABUSE_THRESHOLD_REACHED,
                correlation_id=correlation_id,
                tenant_id=tenant.id,
                deduplicate=True,
            )
    except SecurityAuditError:
        return False
    return True


def authenticate_passcode(
    *,
    request: HttpRequest,
    tenant: Tenant,
    username: str,
    passcode: str,
    client_ip: str,
    device_id: str | None,
    sleeper: Callable[[float], None] = time.sleep,
) -> LoginResult:
    """Authenticate only after Redis and immutable-audit gates pass."""
    normalized_username = username.casefold()
    candidate = User.objects.filter(username=normalized_username).first()
    user = None
    if candidate is not None and candidate.is_active:
        with tenant_atomic(tenant.id):
            if TenantMembership.objects.filter(
                tenant_id=tenant.id, user_id=candidate.id, is_active=True
            ).exists():
                user = candidate
    credential = PasscodeCredential.objects.filter(user=user).first() if user is not None else None
    signals = AttemptSignals(
        account_subject=f"{tenant.id}:{normalized_username}",
        client_ip=client_ip,
        device_id=device_id,
    )
    preflight = preflight_attempt(credential=credential, signals=signals)
    correlation_id = uuid4()
    if not preflight.allowed:
        if preflight.reason is AbuseReason.BACKEND_UNAVAILABLE:
            return LoginResult(LoginStatus.UNAVAILABLE, preflight.retry_after_seconds)
        if not _audit_block(
            tenant=tenant, user=user, credential=credential, correlation_id=correlation_id
        ):
            return LoginResult(LoginStatus.UNAVAILABLE)
        return LoginResult(LoginStatus.RATE_LIMITED, preflight.retry_after_seconds)

    verified = False
    if user is not None and user.is_active and credential is not None:
        verified = verify_passcode(user, passcode).valid
    else:
        verify_dummy_passcode(passcode)

    if not verified:
        decision = record_failed_attempt(credential=credential, signals=signals)
        if decision.reason is AbuseReason.BACKEND_UNAVAILABLE:
            return LoginResult(LoginStatus.UNAVAILABLE, decision.retry_after_seconds)
        if decision.progressive_delay_ms:
            sleeper(decision.progressive_delay_ms / 1000)
        if not _audit_failure(
            tenant=tenant, user=user, credential=credential, correlation_id=correlation_id
        ):
            return LoginResult(LoginStatus.UNAVAILABLE)
        if decision.global_alert and not _audit_global_alert(
            tenant=tenant, correlation_id=correlation_id
        ):
            return LoginResult(LoginStatus.UNAVAILABLE)
        if not decision.allowed:
            return LoginResult(LoginStatus.RATE_LIMITED, decision.retry_after_seconds)
        return LoginResult(LoginStatus.INVALID_CREDENTIALS)

    if user is None or credential is None:
        return LoginResult(LoginStatus.INVALID_CREDENTIALS)

    if credential.must_change:
        success = record_successful_attempt(credential=credential, signals=signals)
        if not success.allowed:
            return LoginResult(LoginStatus.UNAVAILABLE, success.retry_after_seconds)
        if not _audit_failure(
            tenant=tenant, user=user, credential=credential, correlation_id=correlation_id
        ):
            return LoginResult(LoginStatus.UNAVAILABLE)
        return LoginResult(LoginStatus.PASSCODE_CHANGE_REQUIRED)

    success = record_successful_attempt(credential=credential, signals=signals)
    if not success.allowed:
        return LoginResult(LoginStatus.UNAVAILABLE, success.retry_after_seconds)
    try:
        with tenant_atomic(tenant.id):
            _append(
                event_type=SecurityEventType.AUTHENTICATION_SUCCEEDED,
                outcome=SecurityEventOutcome.SUCCESS,
                reason_code=ReasonCode.LOGIN_SUCCEEDED,
                correlation_id=correlation_id,
                tenant_id=tenant.id,
                user=user,
                credential=credential,
            )
    except SecurityAuditError:
        return LoginResult(LoginStatus.UNAVAILABLE)
    request.session.cycle_key()
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    request.session["session_auth_epoch"] = user.session_auth_epoch
    return LoginResult(LoginStatus.SUCCESS)


def validate_login_input(username: object, passcode: object) -> tuple[str, str]:
    if not isinstance(username, str) or not username or len(username) > 150:
        raise ValueError("invalid username")
    if not isinstance(passcode, str):
        raise ValueError("invalid passcode")
    try:
        from modules.identity.passcodes import _validate_passcode

        _validate_passcode(passcode)
    except InvalidPasscode as exc:
        raise ValueError("invalid passcode") from exc
    return username, passcode
