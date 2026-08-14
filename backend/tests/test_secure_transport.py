import importlib

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings


def test_local_compose_defaults_are_http_only():
    assert settings.SECURE_TRANSPORT_ENABLED is False
    assert settings.SECURE_PROXY_SSL_HEADER is None
    assert settings.SESSION_COOKIE_SECURE is False
    assert settings.CSRF_COOKIE_SECURE is False
    assert settings.SECURE_SSL_REDIRECT is False
    assert settings.SECURE_HSTS_SECONDS == 0


@override_settings(
    SECURE_TRANSPORT_ENABLED=True,
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
    SECURE_SSL_REDIRECT=True,
)
def test_trusted_proxy_https_request_is_not_redirected(client):
    response = client.get("/health/live/", HTTP_X_FORWARDED_PROTO="https")
    assert response.status_code == 200


@override_settings(
    SECURE_TRANSPORT_ENABLED=False,
    SECURE_PROXY_SSL_HEADER=None,
    SECURE_SSL_REDIRECT=False,
)
def test_plain_local_http_does_not_consume_forwarded_protocol(client):
    response = client.get("/health/live/", HTTP_X_FORWARDED_PROTO="https")
    assert response.status_code == 200
    assert response.wsgi_request.is_secure() is False


def test_production_requires_explicit_secure_transport(monkeypatch):
    from config.settings import base

    monkeypatch.setattr(base, "SECRET_KEY", "test-secret")
    monkeypatch.setattr(base, "SECURE_TRANSPORT_ENABLED", False)
    monkeypatch.setattr(base, "PASSCODE_ACTIVE_PEPPER_ID", "v1")
    monkeypatch.setattr(base, "PASSCODE_PEPPERS", {"v1": "a2" * 32})
    monkeypatch.setattr(base, "PASSCODE_SIGNAL_HMAC_KEY", "a2" * 32)
    with pytest.raises(ImproperlyConfigured, match="CODESHO_SECURE_TRANSPORT"):
        importlib.reload(importlib.import_module("config.settings.production"))
