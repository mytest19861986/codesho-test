import base64
from types import SimpleNamespace

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.signing import TimestampSigner
from django.test import override_settings

from modules.identity.request_signals import extract_client_ip, extract_device_id


def request(remote="10.0.0.1", real=None, cookie=None):
    meta = {"REMOTE_ADDR": remote}
    if real is not None:
        meta["HTTP_X_REAL_IP"] = real
    return SimpleNamespace(META=meta, COOKIES={"codesho_device": cookie} if cookie else {})


def test_untrusted_proxy_ignores_real_ip():
    with override_settings(TRUSTED_PROXY_CIDRS=()):
        assert extract_client_ip(request(real="203.0.113.4")) == "10.0.0.1"


def test_trusted_proxy_requires_single_valid_real_ip():
    with override_settings(TRUSTED_PROXY_CIDRS=("10.0.0.0/8",)):
        assert extract_client_ip(request(real="203.0.113.4")) == "203.0.113.4"
        assert extract_client_ip(request(real="203.0.113.4, 198.51.100.2")) is None


def test_tampered_device_is_ignored():
    with override_settings(PASSCODE_DEVICE_COOKIE_NAME="codesho_device"):
        assert extract_device_id(request(cookie="not-a-signed-token")) is None


def test_signed_malformed_and_expired_devices_are_ignored(settings):
    signer = TimestampSigner(salt="codesho.passcode.device")
    malformed = signer.sign("f" * 64)
    expired = signer.sign("a" * 32)
    with override_settings(
        PASSCODE_DEVICE_COOKIE_NAME="codesho_device", PASSCODE_DEVICE_MAX_AGE_SECONDS=-1
    ):
        assert extract_device_id(request(cookie=malformed)) is None
        assert extract_device_id(request(cookie=expired)) is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"redis_url": "http://redis"},
        {"hmac_key": "bad"},
        {"account_max": 4},
        {"lockout_seconds": 899},
        {"ip_max": 0},
        {"delays": (1, 2, 3)},
    ],
)
def test_abuse_settings_validation_fails_closed(kwargs):
    values = dict(
        redis_url="redis://redis:6379/0",
        hmac_key=base64.b64encode(b"k" * 32).decode(),
        attempt_window=900,
        account_max=5,
        lockout_seconds=900,
        ip_max=30,
        device_max=20,
        global_threshold=1000,
        global_window=300,
        delays=(250, 500, 1000, 2000),
    )
    values.update(kwargs)
    with pytest.raises(ImproperlyConfigured):
        from modules.identity.request_signals import validate_abuse_settings

        validate_abuse_settings(**values)
