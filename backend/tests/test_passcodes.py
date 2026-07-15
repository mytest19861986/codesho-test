import base64
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from modules.identity.models import PasscodeCredential, User
from modules.identity.passcodes import (
    InvalidPasscode,
    PasscodeVerification,
    set_passcode,
    validate_pepper_settings,
    verify_passcode,
)

TEST_PEPPER = base64.b64encode(b"test-pepper-" + b"x" * 21).decode()
OLD_PEPPER = base64.b64encode(b"old-pepper-" + b"x" * 21).decode()
NEW_PEPPER = base64.b64encode(b"new-pepper-" + b"x" * 21).decode()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="passcode-user", email="passcode@example.com")


@pytest.mark.parametrize("value", ["۱۲۳۴۵۶", "12345", "1234567", "12 4567", "12a456", "١٢٣٤٥٦"])
def test_only_six_ascii_digits_are_accepted(user, value):
    with pytest.raises(InvalidPasscode):
        set_passcode(user, value)


@pytest.mark.django_db
def test_hash_verifies_without_persisting_raw_or_hmac(user):
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="test-v1", PASSCODE_PEPPERS={"test-v1": TEST_PEPPER}
    ):
        credential = set_passcode(user, "123456", must_change=False)
        result = verify_passcode(user, "123456")

    assert result == PasscodeVerification(valid=True, needs_rehash=False)
    assert "123456" not in credential.encoded_hash
    assert "passcode-user" not in repr(credential)
    assert verify_passcode(user, "654321").valid is False


@pytest.mark.django_db
def test_salts_make_hashes_different(user):
    other = User.objects.create_user(username="passcode-user-2", email="passcode2@example.com")
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="test-v1", PASSCODE_PEPPERS={"test-v1": TEST_PEPPER}
    ):
        first = set_passcode(user, "123456")
        second = set_passcode(other, "123456")
    assert first.encoded_hash != second.encoded_hash


@pytest.mark.django_db
def test_old_pepper_is_detected_for_rotation(user):
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="old-v1", PASSCODE_PEPPERS={"old-v1": OLD_PEPPER}
    ):
        set_passcode(user, "123456")
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="new-v1",
        PASSCODE_PEPPERS={"old-v1": OLD_PEPPER, "new-v1": NEW_PEPPER},
    ):
        result = verify_passcode(user, "123456")
    assert result == PasscodeVerification(valid=True, needs_rehash=True)


@pytest.mark.django_db
def test_wrong_pepper_fails_verification(user):
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="test-v1", PASSCODE_PEPPERS={"test-v1": TEST_PEPPER}
    ):
        set_passcode(user, "123456")
    wrong = base64.b64encode(b"wrong-pepper-" + b"x" * 20).decode()
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="wrong-v1", PASSCODE_PEPPERS={"wrong-v1": wrong}
    ):
        assert verify_passcode(user, "123456").valid is False


@pytest.mark.django_db
def test_failed_update_rolls_back_existing_credential(user):
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="test-v1", PASSCODE_PEPPERS={"test-v1": TEST_PEPPER}
    ):
        credential = set_passcode(user, "123456")
        previous_hash = credential.encoded_hash
        with (
            mock.patch.object(
                PasscodeCredential, "save", side_effect=RuntimeError("storage failure")
            ),
            pytest.raises(RuntimeError, match="storage failure"),
        ):
            set_passcode(user, "654321")
        credential.refresh_from_db()
    assert credential.encoded_hash == previous_hash
    with override_settings(
        PASSCODE_ACTIVE_PEPPER_ID="test-v1", PASSCODE_PEPPERS={"test-v1": TEST_PEPPER}
    ):
        assert verify_passcode(user, "123456").valid is True


def test_pepper_validation_is_fail_fast():
    with pytest.raises(ImproperlyConfigured, match="configured Pepper"):
        validate_pepper_settings("missing", {})
    with pytest.raises(ImproperlyConfigured, match="at least 32 bytes"):
        validate_pepper_settings("v1", {"v1": base64.b64encode(b"short").decode()})
