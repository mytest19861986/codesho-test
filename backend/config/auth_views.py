from __future__ import annotations

import json
from contextlib import suppress
from typing import cast
from uuid import uuid4

from django.conf import settings
from django.core.signing import TimestampSigner
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from config.authentication import LoginStatus, authenticate_passcode, validate_login_input
from modules.identity.request_signals import extract_client_ip, extract_device_id, new_device_id
from modules.platform_event.security_audit import (
    ReasonCode,
    SecurityAuditError,
    SecurityAuditEvent,
    SecurityEventOutcome,
    SecurityEventType,
    append_security_event,
)
from modules.platform_tenant.middleware import TenantRequest


def _error(code: str, status: int, *, retry_after: int | None = None) -> JsonResponse:
    response = JsonResponse({"code": code}, status=status)
    if retry_after is not None:
        response["Retry-After"] = str(retry_after)
    return response


def _set_device_cookie(response: HttpResponse, device_id: str) -> None:
    signed = TimestampSigner(salt="codesho.passcode.device").sign(device_id)
    response.set_cookie(
        settings.PASSCODE_DEVICE_COOKIE_NAME,
        signed,
        max_age=settings.PASSCODE_DEVICE_MAX_AGE_SECONDS,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=True,
        samesite="Lax",
    )


@require_GET
@ensure_csrf_cookie
def csrf(request: HttpRequest) -> HttpResponse:
    get_token(request)
    response = HttpResponse(status=204)
    if extract_device_id(request) is None:
        _set_device_cookie(response, new_device_id())
    return response


@require_POST
@csrf_protect
def passcode_login(request: HttpRequest) -> HttpResponse:
    tenant_request = cast(TenantRequest, request)
    try:
        payload = json.loads(request.body)
        username, passcode = validate_login_input(payload.get("username"), payload.get("passcode"))
    except (json.JSONDecodeError, AttributeError, ValueError):
        return _error("invalid_request", 400)
    client_ip = extract_client_ip(request)
    if client_ip is None:
        return _error("invalid_request", 400)
    device_id = extract_device_id(request)
    issued_device_id = device_id is None
    if device_id is None:
        device_id = new_device_id()
    result = authenticate_passcode(
        request=request,
        tenant=tenant_request.tenant,
        username=username,
        passcode=passcode,
        client_ip=client_ip,
        device_id=device_id,
    )
    if result.status is LoginStatus.SUCCESS:
        response = HttpResponse(status=204)
    elif result.status is LoginStatus.PASSCODE_CHANGE_REQUIRED:
        response = _error("passcode_change_required", 403)
    elif result.status is LoginStatus.RATE_LIMITED:
        response = _error("try_again_later", 429, retry_after=result.retry_after_seconds)
    elif result.status is LoginStatus.UNAVAILABLE:
        response = _error("authentication_temporarily_unavailable", 503)
    else:
        response = _error("invalid_credentials", 401)
    if issued_device_id:
        _set_device_cookie(response, device_id)
    return response


@require_GET
def session(request: HttpRequest) -> JsonResponse:
    tenant_request = cast(TenantRequest, request)
    membership = tenant_request.tenant_membership
    return JsonResponse(
        {
            "authenticated": True,
            "user": {"id": str(request.user.id), "username": request.user.username},
            "tenant": {
                "id": str(tenant_request.tenant.id),
                "slug": tenant_request.tenant.slug,
                "role": membership.role,
            },
        }
    )


@require_POST
@csrf_protect
def logout(request: HttpRequest) -> HttpResponse:
    tenant_request = cast(TenantRequest, request)
    user = request.user
    tenant = tenant_request.tenant
    request.session.flush()
    with suppress(SecurityAuditError):
        append_security_event(
            SecurityAuditEvent(
                event_id=uuid4(),
                event_type=SecurityEventType.SESSION_LOGGED_OUT,
                outcome=SecurityEventOutcome.SUCCESS,
                reason_code=ReasonCode.SESSION_LOGGED_OUT,
                correlation_id=uuid4(),
                tenant_id=tenant.id,
                subject_user_id=user.id,
                actor_user_id=user.id,
            )
        )
    return HttpResponse(status=204)


def csrf_failure(request: HttpRequest, reason: str = "") -> JsonResponse:
    return _error("csrf_failed", 403)
