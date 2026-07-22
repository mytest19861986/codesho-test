import importlib

import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings import base, local


def reload_compose_settings():
    return importlib.reload(importlib.import_module("config.settings.compose"))


def set_pepper_settings(monkeypatch, active_id, peppers):
    monkeypatch.setattr(base, "PASSCODE_ACTIVE_PEPPER_ID", active_id)
    monkeypatch.setattr(base, "PASSCODE_PEPPERS", peppers)
    monkeypatch.setattr(local, "PASSCODE_ACTIVE_PEPPER_ID", active_id)
    monkeypatch.setattr(local, "PASSCODE_PEPPERS", peppers)


@pytest.mark.parametrize(
    ("active_id", "peppers"),
    [
        ("", {}),
        ("missing", {"configured": "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ=="}),
        ("configured", {"configured": "not-base64"}),
    ],
)
def test_compose_settings_fail_fast_for_invalid_pepper_configuration(
    monkeypatch, active_id, peppers
):
    set_pepper_settings(monkeypatch, active_id, peppers)

    with pytest.raises(ImproperlyConfigured):
        reload_compose_settings()


def test_compose_settings_accept_valid_synthetic_pepper_configuration(monkeypatch):
    set_pepper_settings(
        monkeypatch,
        "configured",
        {"configured": "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ=="},
    )

    settings = reload_compose_settings()

    assert settings.PASSCODE_ACTIVE_PEPPER_ID == "configured"
    assert set(settings.PASSCODE_PEPPERS) == {"configured"}


def test_compose_services_use_compose_settings():
    with open("../compose.yaml", encoding="utf-8") as compose_file:
        compose = compose_file.read()
    assert compose.count("DJANGO_SETTINGS_MODULE: config.settings.compose") == 4
