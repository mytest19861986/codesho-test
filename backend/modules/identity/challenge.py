"""Internal challenge-secret primitives; deliberately not an API surface."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from uuid import UUID, uuid4

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .pepper import decode_pepper

CHALLENGE_SECRET_BYTES = 32


@dataclass(frozen=True, slots=True)
class ChallengeMaterial:
    selector: UUID
    secret: bytes


def generate_challenge_material() -> ChallengeMaterial:
    """Generate an opaque selector and at least 256 bits of secret entropy."""

    return ChallengeMaterial(selector=uuid4(), secret=secrets.token_bytes(CHALLENGE_SECRET_BYTES))


def _pepper(pepper_id: str) -> bytes:
    peppers = settings.PASSCODE_PEPPERS
    if pepper_id not in peppers:
        raise ImproperlyConfigured("Passcode challenge references an unknown Pepper")
    return decode_pepper(peppers[pepper_id])


def digest_challenge_secret(secret: bytes, pepper_id: str) -> bytes:
    """Return the only verifier persisted for a challenge secret."""

    if not isinstance(secret, bytes) or len(secret) < CHALLENGE_SECRET_BYTES:
        raise ValueError("Challenge secret must contain at least 32 bytes")
    return hmac.digest(_pepper(pepper_id), secret, hashlib.sha256)


def verify_challenge_secret(secret: bytes, expected_digest: bytes, pepper_id: str) -> bool:
    """Verify well-formed internal material without exposing either value.

    Invalid secret material intentionally raises ``ValueError`` through the
    digest primitive; an eventual boundary must normalize that to failure.
    """

    if not isinstance(expected_digest, bytes):
        return False
    return hmac.compare_digest(digest_challenge_secret(secret, pepper_id), expected_digest)
