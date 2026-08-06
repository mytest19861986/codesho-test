from __future__ import annotations

import ast
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client
from django.urls import get_resolver, resolve

from config import adult_signup, auth_views

CONTRACT_ROUTES = {
    "/api/v1/auth/csrf/": ("auth-csrf", auth_views.csrf, "GET"),
    "/api/v1/auth/signup/adult-attestation/": (
        "adult-age-attestation",
        adult_signup.adult_age_attestation,
        "POST",
    ),
    "/api/v1/auth/passcode/login/": ("passcode-login", auth_views.passcode_login, "POST"),
    "/api/v1/auth/passcode/change/complete/": (
        "passcode-change-complete",
        auth_views.passcode_change_complete,
        "POST",
    ),
    "/api/v1/auth/session/": ("auth-session", auth_views.session, "GET"),
    "/api/v1/auth/logout/": ("auth-logout", auth_views.logout, "POST"),
}


def _force_current_session(client: Client, user: object) -> None:
    client.force_login(user)
    session = client.session
    session["session_auth_epoch"] = user.session_auth_epoch  # type: ignore[attr-defined]
    session.save()


def _url_patterns(urlconf: str) -> dict[str, object]:
    return {
        f"/{pattern.pattern}": pattern
        for pattern in get_resolver(urlconf).url_patterns
        if hasattr(pattern, "callback")
    }


def test_projection_routes_match_runtime_route_name_and_callback_identity():
    runtime_patterns = _url_patterns("config.urls")
    projection_patterns = _url_patterns("config.openapi_urls")

    assert set(projection_patterns) == set(CONTRACT_ROUTES)
    for route, (name, callback, _method) in CONTRACT_ROUTES.items():
        runtime_pattern = runtime_patterns[route]
        projection_pattern = projection_patterns[route]
        assert runtime_pattern.name == name
        assert projection_pattern.name == name
        assert resolve(route).func is callback


@pytest.mark.parametrize(
    ("route", "method"), [(route, values[2]) for route, values in CONTRACT_ROUTES.items()]
)
def test_runtime_view_uses_the_contract_http_method(route: str, method: str):
    callback = inspect.unwrap(resolve(route).func)
    source = ast.parse(Path(callback.__code__.co_filename).read_text(encoding="utf-8"))
    function_node = next(
        node
        for node in ast.walk(source)
        if isinstance(node, ast.FunctionDef) and node.name == callback.__name__
    )
    decorator_names = {
        decorator.id
        for decorator in function_node.decorator_list
        if isinstance(decorator, ast.Name)
    }
    assert f"require_{method}" in decorator_names


def test_generated_schema_is_canonical_and_only_exposes_contract_routes():
    expected = Path(settings.BASE_DIR).parent / "docs" / "openapi.yaml"
    with TemporaryDirectory() as directory:
        generated = Path(directory) / "openapi.yaml"
        call_command(
            "spectacular",
            urlconf="config.openapi_urls",
            file=str(generated),
            validate=True,
        )
        assert generated.read_bytes() == expected.read_bytes()
        contents = generated.read_text(encoding="utf-8")
    for route in CONTRACT_ROUTES:
        assert route in contents
    assert "/admin/" not in contents
    assert "/health/" not in contents
    assert "/api/schema/" not in contents


@pytest.mark.django_db
def test_schema_and_swagger_fail_closed_for_anonymous_and_non_staff_users():
    client = Client()
    assert client.get("/api/schema/").status_code in {401, 403}
    assert client.get("/api/schema/swagger-ui/").status_code in {401, 403}

    user = get_user_model().objects.create_user(username="nonstaff", password="not-a-secret")
    _force_current_session(client, user)
    assert client.get("/api/schema/").status_code == 403
    assert client.get("/api/schema/swagger-ui/").status_code == 403


@pytest.mark.django_db
def test_schema_and_swagger_are_available_to_session_authenticated_staff():
    user = get_user_model().objects.create_user(
        username="staff", password="not-a-secret", is_staff=True
    )
    client = Client()
    _force_current_session(client, user)
    assert client.get("/api/schema/").status_code == 200
    assert client.get("/api/schema/swagger-ui/").status_code == 200
