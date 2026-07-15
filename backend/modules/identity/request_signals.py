"""Fail-closed extraction and validation of passcode abuse request signals."""

from __future__ import annotations

import base64
import binascii
import ipaddress
import secrets
from typing import Any

from django.conf import settings
from django.core import signing
from django.core.exceptions import ImproperlyConfigured


def validate_abuse_settings(
    redis_url: str,
    hmac_key: str,
    attempt_window: int,
    account_max: int,
    lockout_seconds: int,
    ip_max: int,
    device_max: int,
    global_threshold: int,
    global_window: int,
    delays: tuple[int, ...],
) -> None:
    if not isinstance(redis_url, str) or not redis_url.startswith(("redis://", "rediss://")):
        raise ImproperlyConfigured("REDIS_URL must be a Redis URL")
    try:
        decoded = base64.b64decode(hmac_key, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ImproperlyConfigured("PASSCODE_SIGNAL_HMAC_KEY must be valid Base64") from exc
    if len(decoded) < 32:
        raise ImproperlyConfigured("PASSCODE_SIGNAL_HMAC_KEY must contain at least 32 bytes")
    if attempt_window <= 0 or account_max != 5 or lockout_seconds < 900:
        raise ImproperlyConfigured("invalid passcode abuse account policy")
    if ip_max <= 0 or device_max <= 0 or global_threshold <= 0 or global_window <= 0:
        raise ImproperlyConfigured("invalid passcode abuse thresholds")
    if len(delays) != 4 or any(value <= 0 for value in delays):
        raise ImproperlyConfigured(
            "PASSCODE_PROGRESSIVE_DELAYS_MS must contain four positive values"
        )


def extract_client_ip(request: Any) -> str | None:
    """Resolve one IP from REMOTE_ADDR; deployment assumes one trusted proxy hop."""
    remote = request.META.get("REMOTE_ADDR")
    try:
        remote_ip = ipaddress.ip_address(str(remote))
    except ValueError:
        return None
    trusted = any(
        remote_ip in ipaddress.ip_network(cidr, strict=False)
        for cidr in settings.TRUSTED_PROXY_CIDRS
    )
    candidate = request.META.get("HTTP_X_REAL_IP") if trusted else str(remote_ip)
    if candidate is None or "," in candidate:
        return None
    try:
        return ipaddress.ip_address(str(candidate).strip()).compressed
    except ValueError:
        return None


def extract_device_id(request: Any) -> str | None:
    raw = request.COOKIES.get(settings.PASSCODE_DEVICE_COOKIE_NAME)
    if not raw:
        return None
    try:
        value = signing.TimestampSigner(salt="codesho.passcode.device").unsign(
            raw, max_age=settings.PASSCODE_DEVICE_MAX_AGE_SECONDS
        )
    except (signing.BadSignature, signing.SignatureExpired):
        return None
    if len(value) != 32 or any(ch not in "0123456789abcdefABCDEF" for ch in value):
        return None
    return value.lower()


def new_device_id() -> str:
    return secrets.token_hex(16)
