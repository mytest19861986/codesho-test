import importlib

import pytest
from django.core.exceptions import ImproperlyConfigured

import modules.identity.challenge_cookie as challenge_cookie
from config.settings import base


def test_production_settings_fail_fast_for_unsafe_passcode_change_cookie(monkeypatch):
    monkeypatch.setattr(base, "SECRET_KEY", "test-secret")
    monkeypatch.setattr(base, "PASSCODE_ACTIVE_PEPPER_ID", "v1")
    monkeypatch.setattr(base, "PASSCODE_PEPPERS", {"v1": "a2" * 32})
    monkeypatch.setattr(base, "PASSCODE_SIGNAL_HMAC_KEY", "a2" * 32)
    monkeypatch.setattr(challenge_cookie, "COOKIE_SECURE", False)
    with pytest.raises(ImproperlyConfigured, match="passcode-change cookie policy is unsafe"):
        importlib.reload(importlib.import_module("config.settings.production"))
