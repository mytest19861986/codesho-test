"""Internal passcode credential primitives; deliberately not an API surface."""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction

from .models import PasscodeCredential, User
from .pepper import decode_pepper
from .pepper import validate_pepper_settings as _validate_pepper_settings

_PASSCODE_PATTERN = re.compile(r"\A[0-9]{6}\Z")
_PASSWORD_HASHER = PasswordHasher()


def validate_pepper_settings(active_id: str, peppers: dict[str, object]) -> None:
    _validate_pepper_settings(active_id, peppers)


class PasscodeError(ValueError):
    """Safe public error for invalid passcode operations."""


class InvalidPasscode(PasscodeError):
    """The supplied passcode does not meet the internal credential contract."""


@dataclass(frozen=True, slots=True)
class PasscodeVerification:
    valid: bool
    needs_rehash: bool = False


def _pepper(pepper_id: str) -> bytes:
    peppers = settings.PASSCODE_PEPPERS
    if pepper_id not in peppers:
        raise ImproperlyConfigured("Passcode credential references an unknown Pepper")
    return decode_pepper(peppers[pepper_id])


def _validate_passcode(passcode: str) -> None:
    if not isinstance(passcode, str) or _PASSCODE_PATTERN.fullmatch(passcode) is None:
        raise InvalidPasscode("Passcode must contain exactly six ASCII digits")


def _hmac_input(passcode: str, pepper_id: str) -> str:
    _validate_passcode(passcode)
    digest = hmac.digest(_pepper(pepper_id), passcode.encode("ascii"), hashlib.sha256)
    return digest.hex()


@transaction.atomic
def set_passcode(user: User, passcode: str, *, must_change: bool = True) -> PasscodeCredential:
    """Create or replace a user's credential inside one transaction."""

    active_id = settings.PASSCODE_ACTIVE_PEPPER_ID
    _validate_passcode(passcode)
    encoded_hash = _PASSWORD_HASHER.hash(_hmac_input(passcode, active_id))
    credential, created = PasscodeCredential.objects.select_for_update().get_or_create(
        user=user,
        defaults={
            "encoded_hash": encoded_hash,
            "pepper_id": active_id,
            "must_change": must_change,
            "credential_version": 1,
        },
    )
    if not created:
        credential.encoded_hash = encoded_hash
        credential.pepper_id = active_id
        credential.must_change = must_change
        credential.credential_version += 1
        credential.save(
            update_fields=[
                "encoded_hash",
                "pepper_id",
                "must_change",
                "credential_version",
                "changed_at",
            ]
        )
    return credential


def verify_passcode(user: User, passcode: str) -> PasscodeVerification:
    """Verify a credential and report whether its Pepper is stale."""

    try:
        credential = PasscodeCredential.objects.get(user=user)
    except PasscodeCredential.DoesNotExist:
        return PasscodeVerification(valid=False)
    try:
        candidate = _hmac_input(passcode, credential.pepper_id)
        valid = _PASSWORD_HASHER.verify(credential.encoded_hash, candidate)
    except (
        ImproperlyConfigured,
        InvalidPasscode,
        InvalidHashError,
        VerificationError,
        VerifyMismatchError,
    ):
        return PasscodeVerification(valid=False)
    return PasscodeVerification(
        valid=valid,
        needs_rehash=valid and credential.pepper_id != settings.PASSCODE_ACTIVE_PEPPER_ID,
    )
