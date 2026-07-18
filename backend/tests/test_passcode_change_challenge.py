from datetime import timedelta
from uuid import uuid4

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.db.models.deletion import RestrictedError
from django.utils import timezone

from modules.identity.challenge import (
    CHALLENGE_SECRET_BYTES,
    digest_challenge_secret,
    generate_challenge_material,
    verify_challenge_secret,
)
from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


def test_challenge_material_has_unique_selector_and_256_bit_secret():
    first = generate_challenge_material()
    second = generate_challenge_material()
    assert first.selector != second.selector
    assert len(first.secret) >= CHALLENGE_SECRET_BYTES
    assert first.secret != second.secret


def test_challenge_digest_is_deterministic_and_rejects_wrong_secret(settings):
    secret = b"x" * CHALLENGE_SECRET_BYTES
    digest = digest_challenge_secret(secret, settings.PASSCODE_ACTIVE_PEPPER_ID)
    assert digest == digest_challenge_secret(secret, settings.PASSCODE_ACTIVE_PEPPER_ID)
    assert verify_challenge_secret(secret, digest, settings.PASSCODE_ACTIVE_PEPPER_ID)
    assert not verify_challenge_secret(
        b"y" * CHALLENGE_SECRET_BYTES,
        digest,
        settings.PASSCODE_ACTIVE_PEPPER_ID,
    )


def test_challenge_digest_rejects_short_secrets(settings):
    with pytest.raises(ValueError, match="at least 32 bytes"):
        digest_challenge_secret(b"short", settings.PASSCODE_ACTIVE_PEPPER_ID)


def test_challenge_digest_fails_closed_for_unknown_pepper():
    with pytest.raises(ImproperlyConfigured, match="unknown Pepper"):
        digest_challenge_secret(b"x" * CHALLENGE_SECRET_BYTES, "retired-pepper")


def test_challenge_digest_has_sha256_length(settings):
    digest = digest_challenge_secret(
        b"x" * CHALLENGE_SECRET_BYTES,
        settings.PASSCODE_ACTIVE_PEPPER_ID,
    )
    assert len(digest) == 32


@pytest.mark.django_db
def test_active_challenge_requires_digest_and_terminal_state_requires_null_digest():
    now = timezone.now()
    challenge = challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=600))
    assert challenge.secret_digest is not None

    challenge.secret_digest = None
    with transaction.atomic(), pytest.raises(IntegrityError):
        challenge.save(update_fields=["secret_digest"])

    challenge.refresh_from_db()
    challenge.state = PasscodeChangeChallenge.State.CONSUMED
    challenge.secret_digest = None
    challenge.consumed_at = now
    challenge.save(update_fields=["state", "secret_digest", "consumed_at"])


@pytest.mark.django_db
def test_partial_unique_constraint_allows_only_one_active_challenge():
    now = timezone.now()
    first = challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=600))
    with transaction.atomic(), pytest.raises(IntegrityError):
        challenge_factory(
            credential=first.credential,
            tenant=first.tenant,
            issued_at=now,
            expires_at=now + timedelta(seconds=600),
        )

    first.state = PasscodeChangeChallenge.State.REVOKED
    first.secret_digest = None
    first.revoked_at = now
    first.save(update_fields=["state", "secret_digest", "revoked_at"])
    assert challenge_factory(
        credential=first.credential,
        tenant=first.tenant,
        issued_at=now,
        expires_at=now + timedelta(seconds=600),
    ).state == PasscodeChangeChallenge.State.ACTIVE


@pytest.mark.django_db
def test_challenge_foreign_keys_restrict_credential_and_tenant_deletion():
    now = timezone.now()
    challenge = challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=600))
    with pytest.raises(RestrictedError):
        challenge.credential.delete()
    with pytest.raises(RestrictedError):
        challenge.tenant.delete()


def challenge_factory(**overrides):
    tenant = overrides.pop("tenant", Tenant.objects.create(slug=f"tenant-{uuid4()}", name="Tenant"))
    credential = overrides.pop("credential", credential_factory())
    material = generate_challenge_material()
    values = {
        "selector": material.selector,
        "tenant": tenant,
        "credential": credential,
        "credential_version": credential.credential_version,
        "purpose": PasscodeChangeChallenge.Purpose.FORCED_PASSCODE_CHANGE,
        "secret_digest": digest_challenge_secret(material.secret, "test-v1"),
        "pepper_id": "test-v1",
        "state": PasscodeChangeChallenge.State.ACTIVE,
    }
    values.update(overrides)
    with tenant_atomic(tenant.pk):
        return PasscodeChangeChallenge.objects.create(**values)


def credential_factory() -> PasscodeCredential:
    user = User.objects.create_user(username=f"user-{uuid4()}", email=f"{uuid4()}@example.com")
    return PasscodeCredential.objects.create(
        user=user,
        encoded_hash="unused-for-challenge-foundation",
        pepper_id="test-v1",
    )
