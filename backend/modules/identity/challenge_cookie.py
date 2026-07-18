"""Strict codec and policy for forced-passcode-change cookies."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from typing import Final
from uuid import UUID

COOKIE_NAME: Final = "__Host-codesho-passcode-change"
COOKIE_SECURE: Final = True
COOKIE_HTTPONLY: Final = True
COOKIE_SAMESITE: Final = "Lax"
COOKIE_PATH: Final = "/"
COOKIE_DOMAIN: Final = None
COOKIE_TTL_SECONDS: Final = 600
COOKIE_VERSION: Final = "v1"
CHALLENGE_SECRET_MIN_BYTES: Final = 32
MAX_COOKIE_VALUE_LENGTH: Final = 512
_BASE64URL = re.compile(r"[A-Za-z0-9_-]+\Z")


@dataclass(frozen=True, slots=True)
class ChallengeCookieValue:
    selector: UUID
    secret: bytes


def _invalid() -> ValueError:
    return ValueError("invalid passcode change cookie")


def serialize_challenge_cookie(value: ChallengeCookieValue) -> str:
    """Serialize opaque internal material without emitting an HTTP cookie."""
    if (
        not isinstance(value, ChallengeCookieValue)
        or not isinstance(value.selector, UUID)
        or not isinstance(value.secret, bytes)
    ):
        raise _invalid()
    if len(value.secret) < CHALLENGE_SECRET_MIN_BYTES:
        raise _invalid()
    secret = base64.urlsafe_b64encode(value.secret).rstrip(b"=").decode("ascii")
    result = f"{COOKIE_VERSION}.{value.selector}.{secret}"
    if len(result) > MAX_COOKIE_VALUE_LENGTH:
        raise _invalid()
    return result


def parse_challenge_cookie(raw_value: object) -> ChallengeCookieValue:
    """Parse the exact cookie grammar, exposing no cookie material in failures."""
    if not isinstance(raw_value, str) or len(raw_value) > MAX_COOKIE_VALUE_LENGTH:
        raise _invalid()
    parts = raw_value.split(".")
    if len(parts) != 3 or parts[0] != COOKIE_VERSION:
        raise _invalid()
    selector_text, secret_text = parts[1:]
    try:
        selector = UUID(selector_text)
    except (AttributeError, ValueError):
        raise _invalid() from None
    if str(selector) != selector_text or not _BASE64URL.fullmatch(secret_text):
        raise _invalid()
    try:
        secret = base64.b64decode(
            secret_text + "=" * (-len(secret_text) % 4), altchars=b"-_", validate=True
        )
    except ValueError:
        raise _invalid() from None
    if len(secret) < CHALLENGE_SECRET_MIN_BYTES:
        raise _invalid()
    return ChallengeCookieValue(selector=selector, secret=secret)
