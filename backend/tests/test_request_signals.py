from types import SimpleNamespace

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
