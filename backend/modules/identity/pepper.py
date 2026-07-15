"""Pepper parsing and production configuration validation without model imports."""

from __future__ import annotations

import base64
import binascii
from typing import Any

from django.core.exceptions import ImproperlyConfigured

MIN_PEPPER_BYTES = 32


def decode_pepper(value: Any) -> bytes:
    if not isinstance(value, str):
        raise ImproperlyConfigured("PASSCODE_PEPPERS values must be Base64 strings")
    try:
        pepper = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ImproperlyConfigured("PASSCODE_PEPPERS contains invalid Base64") from exc
    if len(pepper) < MIN_PEPPER_BYTES:
        raise ImproperlyConfigured("PASSCODE peppers must contain at least 32 bytes")
    return pepper


def validate_pepper_settings(active_id: str, peppers: dict[str, Any]) -> None:
    if not active_id or active_id not in peppers:
        raise ImproperlyConfigured("PASSCODE_ACTIVE_PEPPER_ID must identify a configured Pepper")
    for pepper in peppers.values():
        decode_pepper(pepper)
