"""Internal Redis-backed passcode abuse controls; no public API surface."""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import math
from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum

import redis
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import PasscodeCredential

logger = logging.getLogger(__name__)


class AbuseReason(StrEnum):
    ALLOWED = "allowed"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_LIMIT = "account_limit"
    IP_LIMIT = "ip_limit"
    DEVICE_LIMIT = "device_limit"
    CHALLENGE_LIMIT = "challenge_limit"
    BACKEND_UNAVAILABLE = "backend_unavailable"


@dataclass(frozen=True, slots=True)
class AttemptSignals:
    account_subject: str
    client_ip: str
    device_id: str | None = None


@dataclass(frozen=True, slots=True)
class AbuseDecision:
    allowed: bool
    reason: AbuseReason
    retry_after_seconds: int
    progressive_delay_ms: int
    global_alert: bool


@dataclass(frozen=True, slots=True)
class CompletionSignals:
    """Non-secret, HMAC-keyed dimensions for one change-completion request."""

    client_ip: str
    device_id: str | None
    account_subject: str | None = None
    challenge_subject: str | None = None
    global_subject: str | None = None


@dataclass(frozen=True, slots=True)
class CompletionDimensions:
    account: bool = False
    challenge: bool = False
    ip: bool = False
    device: bool = False
    global_detection: bool = False


_BUMP_LUA = """local out={}
for i,key in ipairs(KEYS) do
 if key=='' then out[#out+1]=-1; out[#out+1]=-1 else
  local n=redis.call('INCR',key); local t=redis.call('PTTL',key)
  if n==1 or t<0 then redis.call('PEXPIRE',key,tonumber(ARGV[i])); t=tonumber(ARGV[i]) end
  out[#out+1]=n; out[#out+1]=t
 end
end
return out"""
_READ_LUA = """local out={}
for _,key in ipairs(KEYS) do
 if key=='' then out[#out+1]=0; out[#out+1]=0 else
  local n=redis.call('GET',key); local t=redis.call('PTTL',key)
  if not n then n=0 end
  if t<0 and tonumber(n)>0 then return {-1} end
  out[#out+1]=tonumber(n); out[#out+1]=math.max(t,0)
 end
end
return out"""
_CLEAR_LUA = """local deleted=0
for _,key in ipairs(KEYS) do if key~='' then deleted=deleted+redis.call('DEL',key) end end
return {1,deleted}"""
_COMPLETION_BUMP_LUA = """local out={}
for i=1,5 do
 if ARGV[6+i]=='1' and KEYS[i]~='' then
  local n=redis.call('INCR',KEYS[i]); local t=redis.call('PTTL',KEYS[i])
  if n==1 or t<0 then redis.call('PEXPIRE',KEYS[i],tonumber(ARGV[i])); t=tonumber(ARGV[i]) end
  out[#out+1]=n; out[#out+1]=t
 else out[#out+1]=0; out[#out+1]=0 end
end
local distinct=0; local distinct_ttl=0
if ARGV[11]=='1' and KEYS[6]~='' and ARGV[12]~='' then
 redis.call('ZADD',KEYS[6],0,ARGV[12]); local t=redis.call('PTTL',KEYS[6])
 if t<0 then redis.call('PEXPIRE',KEYS[6],tonumber(ARGV[6])); t=tonumber(ARGV[6]) end
 distinct=redis.call('ZCARD',KEYS[6]); distinct_ttl=t
end
out[#out+1]=distinct; out[#out+1]=distinct_ttl
return out"""


def _digest(value: str) -> str:
    key = base64.b64decode(settings.PASSCODE_SIGNAL_HMAC_KEY, validate=True)
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()


def _client() -> redis.Redis:
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)


def _keys(signals: AttemptSignals) -> list[str]:
    prefix = settings.PASSCODE_RATE_LIMIT_REDIS_PREFIX
    account = f"{prefix}:account:{_digest(signals.account_subject)}"
    ip_key = f"{prefix}:ip:{_digest(signals.client_ip)}"
    device = _digest(signals.device_id) if signals.device_id else None
    return [
        account,
        f"{prefix}:account-device:{_digest(signals.account_subject)}:{device}" if device else "",
        ip_key,
        f"{prefix}:device:{device}" if device else "",
        f"{prefix}:global",
    ]


def _backend_failure() -> AbuseDecision:
    return AbuseDecision(
        False,
        AbuseReason.BACKEND_UNAVAILABLE,
        settings.PASSCODE_BACKEND_FAILURE_RETRY_SECONDS,
        0,
        False,
    )


def _decision(
    counts: list[int], ttls: list[int], credential: PasscodeCredential | None
) -> AbuseDecision:
    now = timezone.now()
    if credential and credential.locked_until and credential.locked_until > now:
        retry = max(0, math.ceil((credential.locked_until - now).total_seconds()))
        return AbuseDecision(
            False,
            AbuseReason.ACCOUNT_LOCKED,
            retry,
            0,
            counts[4] >= settings.PASSCODE_GLOBAL_ALERT_THRESHOLD,
        )
    global_alert = counts[4] >= settings.PASSCODE_GLOBAL_ALERT_THRESHOLD
    for idx, limit, reason in (
        (0, settings.PASSCODE_ACCOUNT_MAX_FAILURES, AbuseReason.ACCOUNT_LIMIT),
        (2, settings.PASSCODE_IP_MAX_FAILURES, AbuseReason.IP_LIMIT),
        (3, settings.PASSCODE_DEVICE_MAX_FAILURES, AbuseReason.DEVICE_LIMIT),
    ):
        if counts[idx] >= limit:
            return AbuseDecision(
                False, reason, max(0, math.ceil(ttls[idx] / 1000)), 0, global_alert
            )
    delay = settings.PASSCODE_PROGRESSIVE_DELAYS_MS[counts[0] - 1] if 1 <= counts[0] < 5 else 0
    return AbuseDecision(True, AbuseReason.ALLOWED, 0, delay, global_alert)


def _run(script: str, signals: AttemptSignals, *, bump: bool) -> tuple[list[int], list[int]]:
    client = _client()
    keys = _keys(signals)
    args = (
        (
            [settings.PASSCODE_ATTEMPT_WINDOW_SECONDS * 1000] * 4
            + [settings.PASSCODE_GLOBAL_WINDOW_SECONDS * 1000]
        )
        if bump
        else []
    )
    result = client.eval(script, len(keys), *keys, *args)
    if not isinstance(result, list) or (len(result) != 10 and result != [-1]):
        raise ValueError("malformed abuse backend response")
    if result == [-1]:
        raise ValueError("invalid abuse backend ttl")
    nums = [int(v) for v in result]
    counts, ttls = nums[0::2], nums[1::2]
    if any(v < 0 for v in counts + ttls):
        raise ValueError("invalid abuse backend values")
    return counts, ttls


def preflight_attempt(
    *, credential: PasscodeCredential | None, signals: AttemptSignals
) -> AbuseDecision:
    try:
        counts, ttls = _run(_READ_LUA, signals, bump=False)
        return _decision(counts, ttls, credential)
    except Exception:
        logger.warning(
            "passcode_abuse_backend_failure",
            extra={"event_name": "passcode_abuse", "error_code": "backend_unavailable"},
        )
        return _backend_failure()


def record_failed_attempt(
    *, credential: PasscodeCredential | None, signals: AttemptSignals
) -> AbuseDecision:
    try:
        counts, ttls = _run(_BUMP_LUA, signals, bump=True)
        decision = _decision(counts, ttls, credential)
        if counts[0] >= settings.PASSCODE_ACCOUNT_MAX_FAILURES and credential:
            candidate = timezone.now() + timedelta(seconds=settings.PASSCODE_LOCKOUT_SECONDS)
            try:
                with transaction.atomic():
                    locked = PasscodeCredential.objects.select_for_update().get(pk=credential.pk)
                    locked.locked_until = max(locked.locked_until or candidate, candidate)
                    locked.save(update_fields=["locked_until", "changed_at"])
            except Exception:
                return _backend_failure()
        return decision
    except Exception:
        return _backend_failure()


def record_successful_attempt(
    *, credential: PasscodeCredential, signals: AttemptSignals
) -> AbuseDecision:
    if credential.locked_until and credential.locked_until > timezone.now():
        return _decision([0, 0, 0, 0, 0], [0, 0, 0, 0, 0], credential)
    try:
        client = _client()
        # Never clear IP/device-wide counters from one account's success.
        # Redis EVAL executes this account/account-device clear atomically.
        keys = _keys(signals)[:2]
        result = client.eval(_CLEAR_LUA, len(keys), *keys)
        if not isinstance(result, list) or len(result) != 2 or int(result[0]) != 1:
            raise ValueError("malformed abuse backend response")
        return AbuseDecision(True, AbuseReason.ALLOWED, 0, 0, False)
    except Exception:
        return _backend_failure()


def _completion_keys(signals: CompletionSignals) -> list[str]:
    prefix = f"{settings.PASSCODE_RATE_LIMIT_REDIS_PREFIX}:completion"
    # The selector is never retained: challenge_subject is an internal UUID and
    # only its keyed digest is used in Redis.
    return [
        (
            f"{prefix}:account:{_digest(signals.account_subject)}"
            if signals.account_subject
            else ""
        ),
        f"{prefix}:challenge:{_digest(signals.challenge_subject)}"
        if signals.challenge_subject
        else "",
        f"{prefix}:ip:{_digest(signals.client_ip)}",
        f"{prefix}:device:{_digest(signals.device_id)}" if signals.device_id else "",
        f"{prefix}:global",
    ]


def _completion_distinct_key() -> str:
    return f"{settings.PASSCODE_RATE_LIMIT_REDIS_PREFIX}:completion:global-distinct"


def _completion_run(
    script: str, signals: CompletionSignals, *, bump: bool
) -> tuple[list[int], list[int]]:
    keys = _completion_keys(signals)
    args = (
        [settings.PASSCODE_CHANGE_COMPLETION_WINDOW_SECONDS * 1000] * len(keys)
        if bump
        else []
    )
    result = _client().eval(script, len(keys), *keys, *args)
    if not isinstance(result, list) or (len(result) != 10 and result != [-1]):
        raise ValueError("malformed completion abuse backend response")
    if result == [-1]:
        raise ValueError("invalid completion abuse backend ttl")
    values = [int(value) for value in result]
    counts, ttls = values[0::2], values[1::2]
    if any(value < 0 for value in counts + ttls):
        raise ValueError("invalid completion abuse backend values")
    return counts, ttls


def _completion_decision(
    counts: list[int], ttls: list[int], *, distinct_subjects: int = 0
) -> AbuseDecision:
    global_alert = (
        counts[4] >= settings.PASSCODE_CHANGE_COMPLETION_GLOBAL_ALERT_THRESHOLD
        or distinct_subjects >= 20
    )
    for index, limit, reason in (
        (
            0,
            settings.PASSCODE_CHANGE_COMPLETION_ACCOUNT_MAX_FAILURES,
            AbuseReason.ACCOUNT_LIMIT,
        ),
        (
            1,
            settings.PASSCODE_CHANGE_COMPLETION_CHALLENGE_MAX_FAILURES,
            AbuseReason.CHALLENGE_LIMIT,
        ),
        (
            2,
            settings.PASSCODE_CHANGE_COMPLETION_IP_MAX_FAILURES,
            AbuseReason.IP_LIMIT,
        ),
        (
            3,
            settings.PASSCODE_CHANGE_COMPLETION_DEVICE_MAX_FAILURES,
            AbuseReason.DEVICE_LIMIT,
        ),
    ):
        if counts[index] >= limit:
            return AbuseDecision(
                False, reason, max(0, math.ceil(ttls[index] / 1000)), 0, global_alert
            )
    return AbuseDecision(True, AbuseReason.ALLOWED, 0, 0, global_alert)


def preflight_completion_attempt(signals: CompletionSignals) -> AbuseDecision:
    try:
        counts, ttls = _completion_run(_READ_LUA, signals, bump=False)
        return _completion_decision(counts, ttls)
    except Exception:
        logger.warning(
            "passcode_completion_abuse_backend_failure",
            extra={
                "event_name": "passcode_completion_abuse",
                "error_code": "backend_unavailable",
            },
        )
        return _backend_failure()


def record_failed_completion_attempt(
    signals: CompletionSignals, dimensions: CompletionDimensions
) -> AbuseDecision:
    try:
        keys = _completion_keys(signals) + [_completion_distinct_key()]
        flags = [
            dimensions.account,
            dimensions.challenge,
            dimensions.ip,
            dimensions.device,
            dimensions.global_detection,
        ]
        subject = _digest(signals.global_subject) if signals.global_subject else ""
        ttl = settings.PASSCODE_CHANGE_COMPLETION_WINDOW_SECONDS * 1000
        result = _client().eval(
            _COMPLETION_BUMP_LUA,
            len(keys),
            *keys,
            *([ttl] * 6),
            *("1" if flag else "0" for flag in flags),
            subject,
        )
        if not isinstance(result, list) or len(result) != 12:
            raise ValueError("malformed completion abuse backend response")
        values = [int(value) for value in result]
        if any(value < 0 for value in values):
            raise ValueError("invalid completion abuse backend values")
        counts, ttls = values[:10:2], values[1:10:2]
        return _completion_decision(counts, ttls, distinct_subjects=values[10])
    except Exception:
        return _backend_failure()


def record_successful_completion_attempt(signals: CompletionSignals) -> AbuseDecision:
    try:
        # A successful forced change clears only the account and single
        # challenge counters.  IP and device counters are intentionally shared
        # across principals and must never be reset by a successful request.
        result = _client().eval(_CLEAR_LUA, 2, *_completion_keys(signals)[:2])
        if not isinstance(result, list) or len(result) != 2 or int(result[0]) != 1:
            raise ValueError("malformed completion clear response")
        return AbuseDecision(True, AbuseReason.ALLOWED, 0, 0, False)
    except Exception:
        return _backend_failure()
