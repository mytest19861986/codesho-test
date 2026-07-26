from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import math
from dataclasses import dataclass
from typing import cast
from uuid import UUID, uuid4

import redis
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from modules.identity.models import AdultAgeAttestation, AdultAttestationProvenance
from modules.identity.request_signals import extract_client_ip
from modules.platform_event.security_audit import (
    SecurityAuditError,
    adult_age_attestation_accepted,
    adult_signup_rejected_age_attestation_missing,
    append_security_event,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.middleware import TenantRequest

EXPECTED_FIELDS = {"adultAttestation", "policyVersion", "subjectId"}
logger = logging.getLogger(__name__)
_RATE_BUMP_LUA = """
local out = {}
for index,key in ipairs(KEYS) do
  local count = redis.call('INCR', key)
  local ttl = redis.call('PTTL', key)
  if count == 1 or ttl < 0 then
    redis.call('PEXPIRE', key, tonumber(ARGV[1]))
    ttl = tonumber(ARGV[1])
  end
  out[#out + 1] = count
  out[#out + 1] = ttl
end
return out
"""


@dataclass(frozen=True, slots=True)
class AdultSignupRateDecision:
    allowed: bool
    retry_after_seconds: int
    backend_available: bool = True


def _digest(value: str) -> str:
    key = base64.b64decode(settings.PASSCODE_SIGNAL_HMAC_KEY, validate=True)
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()


def check_adult_signup_rate(
    tenant_id: UUID,
    subject_id: UUID,
    client_ip: str,
) -> AdultSignupRateDecision:
    prefix = "codesho:adult-signup:v1"
    try:
        keys = (
            f"{prefix}:subject:{_digest(f'{tenant_id}:{subject_id}')}",
            f"{prefix}:ip:{_digest(client_ip)}",
        )
        result = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False).eval(
            _RATE_BUMP_LUA,
            len(keys),
            *keys,
            settings.ADULT_SIGNUP_RATE_WINDOW_SECONDS * 1000,
        )
        if not isinstance(result, list) or len(result) != 4:
            raise ValueError("malformed rate-limit response")
        values = [int(value) for value in result]
        if any(value < 0 for value in values):
            raise ValueError("invalid rate-limit response")
    except Exception:
        logger.warning(
            "adult_signup_rate_backend_failure",
            extra={
                "event_name": "adult_signup_rate",
                "error_code": "backend_unavailable",
            },
        )
        return AdultSignupRateDecision(
            False,
            settings.PASSCODE_BACKEND_FAILURE_RETRY_SECONDS,
            backend_available=False,
        )

    subject_count, subject_ttl, ip_count, ip_ttl = values
    retry_after = 0
    if subject_count > settings.ADULT_SIGNUP_SUBJECT_MAX_ATTEMPTS:
        retry_after = max(retry_after, math.ceil(subject_ttl / 1000))
    if ip_count > settings.ADULT_SIGNUP_IP_MAX_ATTEMPTS:
        retry_after = max(retry_after, math.ceil(ip_ttl / 1000))
    return AdultSignupRateDecision(retry_after == 0, retry_after)


def _error(code: str, status: int, *, retry_after: int | None = None) -> JsonResponse:
    response = JsonResponse({"code": code}, status=status)
    if retry_after is not None:
        response["Retry-After"] = str(retry_after)
    return response


def _synthetic_subject(value: object) -> UUID:
    if not isinstance(value, str):
        raise ValueError("subject must be a UUID string")
    subject_id = UUID(value)
    if subject_id.version != 4 or str(subject_id) != value:
        raise ValueError("subject must be a canonical UUIDv4")
    return subject_id


def _audit_idempotency_key(
    outcome: str,
    tenant_id: UUID,
    subject_id: UUID,
    policy_version: str,
) -> str:
    return f"adult-signup:{outcome}:{tenant_id}:{subject_id}:{policy_version}"


@require_POST
@csrf_protect
def adult_age_attestation(request: HttpRequest) -> HttpResponse:
    if settings.ADULT_SIGNUP_MODE != "internal_test":
        return _error("not_found", 404)

    try:
        payload = json.loads(request.body)
        if not isinstance(payload, dict) or set(payload) != EXPECTED_FIELDS:
            raise ValueError("request fields do not match the contract")
        if not isinstance(payload["adultAttestation"], bool):
            raise ValueError("adult attestation must be a boolean")
        subject_id = _synthetic_subject(payload["subjectId"])
        policy_version = payload["policyVersion"]
        if not isinstance(policy_version, str):
            raise ValueError("policy version must be a string")
    except (json.JSONDecodeError, TypeError, ValueError):
        return _error("invalid_request", 400)

    if policy_version != settings.ADULT_SIGNUP_POLICY_VERSION:
        return _error("policy_version_mismatch", 409)

    tenant_request = cast(TenantRequest, request)
    tenant_id = tenant_request.tenant.id
    correlation_id = uuid4()
    client_ip = extract_client_ip(request)
    if client_ip is None:
        return _error("invalid_request", 400)
    rate_decision = check_adult_signup_rate(tenant_id, subject_id, client_ip)
    if not rate_decision.allowed:
        if not rate_decision.backend_available:
            return _error("temporarily_unavailable", 503)
        return _error(
            "try_again_later",
            429,
            retry_after=rate_decision.retry_after_seconds,
        )

    if payload["adultAttestation"] is not True:
        event_id = uuid4()
        try:
            append_security_event(
                adult_signup_rejected_age_attestation_missing(
                    event_id,
                    correlation_id,
                    tenant_id,
                    subject_id,
                    _audit_idempotency_key(
                        "rejected",
                        tenant_id,
                        subject_id,
                        policy_version,
                    ),
                )
            )
        except SecurityAuditError:
            return _error("temporarily_unavailable", 503)
        return _error("adult_attestation_required", 403)

    try:
        with tenant_atomic(tenant_id):
            attestation, created = AdultAgeAttestation.objects.get_or_create(
                tenant_id=tenant_id,
                subject_id=subject_id,
                policy_version=policy_version,
            )
            if created:
                AdultAttestationProvenance.objects.create(
                    tenant_id=tenant_id,
                    attestation=attestation,
                )
            append_security_event(
                adult_age_attestation_accepted(
                    attestation.audit_event_id,
                    correlation_id,
                    tenant_id,
                    subject_id,
                    _audit_idempotency_key(
                        "accepted",
                        tenant_id,
                        subject_id,
                        policy_version,
                    ),
                )
            )
    except SecurityAuditError:
        return _error("temporarily_unavailable", 503)

    return JsonResponse(
        {
            "attestationId": str(attestation.id),
            "attestedAt": attestation.attested_at.isoformat(),
            "policyVersion": attestation.policy_version,
            "source": attestation.source,
            "status": attestation.status,
        },
        status=201 if created else 200,
    )
