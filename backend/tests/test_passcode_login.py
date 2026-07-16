from unittest.mock import patch

import pytest
from django.test import Client

from modules.identity.abuse import AbuseDecision, AbuseReason
from modules.identity.models import PasscodeCredential, User
from modules.identity.passcodes import set_passcode
from modules.platform_event.security_audit import SecurityAuditError, SecurityEventType
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


def allowed() -> AbuseDecision:
    return AbuseDecision(True, AbuseReason.ALLOWED, 0, 0, False)


@pytest.fixture
def tenant_member(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant = Tenant.objects.create(slug="alpha", name="Alpha")
    user = User.objects.create_user(username="learner", email="learner@example.com")
    set_passcode(user, "123456", must_change=False)
    with tenant_atomic(tenant.id):
        membership = TenantMembership.objects.create(
            tenant=tenant, user=user, role=TenantMembership.Role.LEARNER
        )
    return tenant, user, membership


def csrf_client() -> Client:
    return Client(enforce_csrf_checks=True)


def csrf_headers(client: Client) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf/", HTTP_HOST="alpha.localhost")
    assert response.status_code == 204
    return {"HTTP_X_CSRFTOKEN": response.cookies["csrftoken"].value}


def login(client: Client, headers: dict[str, str], **payload: str):
    return client.post(
        "/api/v1/auth/passcode/login/",
        {"username": "learner", "passcode": "123456", **payload},
        content_type="application/json",
        HTTP_HOST="alpha.localhost",
        **headers,
    )


@pytest.mark.django_db(transaction=True)
def test_csrf_endpoint_sets_device_cookie_and_login_rotates_session(tenant_member):
    _, user, _ = tenant_member
    client = csrf_client()
    headers = csrf_headers(client)
    session = client.session
    session["pre_login"] = "value"
    session.save()
    pre_login_key = session.session_key

    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
    ):
        response = login(client, headers)

    assert response.status_code == 204
    assert client.cookies.get("codesho_device") is not None
    assert client.session.session_key != pre_login_key
    assert client.session["session_auth_epoch"] == user.session_auth_epoch
    session_response = client.get("/api/v1/auth/session/", HTTP_HOST="alpha.localhost")
    assert session_response.status_code == 200
    assert session_response.json()["user"] == {"id": str(user.id), "username": "learner"}
    assert session_response.json()["tenant"]["role"] == TenantMembership.Role.LEARNER


@pytest.mark.django_db(transaction=True)
def test_login_without_csrf_is_safe_json_failure(tenant_member):
    response = csrf_client().post(
        "/api/v1/auth/passcode/login/",
        {"username": "learner", "passcode": "123456"},
        content_type="application/json",
        HTTP_HOST="alpha.localhost",
    )
    assert response.status_code == 403
    assert response.json() == {"code": "csrf_failed"}


@pytest.mark.django_db(transaction=True)
def test_rate_limit_and_corrupt_device_cookie_are_handled_safely(tenant_member):
    client = csrf_client()
    client.cookies["codesho_device"] = "corrupt"
    headers = csrf_headers(client)
    limited = AbuseDecision(False, AbuseReason.ACCOUNT_LIMIT, 900, 0, False)
    with (
        patch("config.authentication.preflight_attempt", return_value=limited),
        patch("config.authentication.append_security_event"),
    ):
        response = login(client, headers)
    assert response.status_code == 429
    assert response.json() == {"code": "try_again_later"}
    assert response["Retry-After"] == "900"
    assert client.cookies["codesho_device"].value != "corrupt"


@pytest.mark.django_db(transaction=True)
def test_wrong_unknown_inactive_and_nonmember_share_invalid_credentials(tenant_member):
    tenant, user, _ = tenant_member
    inactive = User.objects.create_user(
        username="inactive", email="inactive@example.com", is_active=False
    )
    set_passcode(inactive, "123456", must_change=False)
    outsider = User.objects.create_user(username="outsider", email="outsider@example.com")
    set_passcode(outsider, "123456", must_change=False)
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_failed_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
        patch(
            "config.authentication.verify_passcode",
            return_value=type("V", (), {"valid": False})(),
        ),
    ):
        wrong = login(client, headers, passcode="000000")
        unknown = login(client, headers, username="unknown", passcode="000000")
        inactive_response = login(client, headers, username="inactive", passcode="000000")
        nonmember = login(client, headers, username="outsider", passcode="000000")
    assert [
        response.status_code for response in (wrong, unknown, inactive_response, nonmember)
    ] == [401] * 4
    assert [response.json() for response in (wrong, unknown, inactive_response, nonmember)] == [
        {"code": "invalid_credentials"}
    ] * 4


@pytest.mark.django_db(transaction=True)
def test_must_change_and_audit_failure_never_create_a_session(tenant_member):
    _, user, _ = tenant_member
    credential = PasscodeCredential.objects.get(user=user)
    credential.must_change = True
    credential.save(update_fields=["must_change"])
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
    ):
        response = login(client, headers)
    assert response.status_code == 403
    assert response.json() == {"code": "passcode_change_required"}
    assert "_auth_user_id" not in client.session

    credential.must_change = False
    credential.save(update_fields=["must_change"])
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch(
            "config.authentication.append_security_event",
            side_effect=SecurityAuditError(),
        ),
    ):
        response = login(client, headers)
    assert response.status_code == 503
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db(transaction=True)
def test_session_epoch_invalidates_prior_session_after_passcode_change(tenant_member):
    _, user, _ = tenant_member
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
    ):
        assert login(client, headers).status_code == 204
    old_epoch = client.session["session_auth_epoch"]
    set_passcode(user, "654321", must_change=False)
    assert user.session_auth_epoch > old_epoch
    response = client.get("/api/v1/auth/session/", HTTP_HOST="alpha.localhost")
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_redis_failure_and_exact_pre_auth_paths_fail_closed(tenant_member):
    client = csrf_client()
    headers = csrf_headers(client)
    unavailable = AbuseDecision(False, AbuseReason.BACKEND_UNAVAILABLE, 5, 0, False)
    with patch("config.authentication.preflight_attempt", return_value=unavailable):
        response = login(client, headers)
    assert response.status_code == 503
    assert response.json() == {"code": "authentication_temporarily_unavailable"}
    response = client.get("/api/v1/auth/csrf/extra", HTTP_HOST="alpha.localhost")
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_global_alert_audit_is_typed_and_failure_events_are_bounded(tenant_member):
    client = csrf_client()
    headers = csrf_headers(client)
    global_alert = AbuseDecision(True, AbuseReason.ALLOWED, 0, 0, True)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_failed_attempt", return_value=global_alert),
        patch(
            "config.authentication.verify_passcode",
            return_value=type("V", (), {"valid": False})(),
        ),
        patch("config.authentication.append_security_event") as append,
    ):
        response = login(client, headers, passcode="000000")
    assert response.status_code == 401
    assert [call.args[0].event_type for call in append.call_args_list] == [
        SecurityEventType.AUTHENTICATION_FAILED,
        SecurityEventType.ABUSE_GLOBAL_ALERT,
    ]


@pytest.mark.django_db(transaction=True)
def test_logout_flushes_session_when_audit_is_unavailable(tenant_member):
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
    ):
        assert login(client, headers).status_code == 204
    with patch("config.auth_views.append_security_event", side_effect=SecurityAuditError()):
        response = client.post(
            "/api/v1/auth/logout/",
            HTTP_HOST="alpha.localhost",
            **csrf_headers(client),
        )
    assert response.status_code == 204
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db(transaction=True)
def test_logout_without_csrf_is_rejected_and_production_cookie_flags_hold(tenant_member, settings):
    settings.SESSION_COOKIE_SECURE = True
    settings.CSRF_COOKIE_SECURE = True
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
    ):
        response = login(client, headers)
    session_cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    device_cookie = client.cookies[settings.PASSCODE_DEVICE_COOKIE_NAME]
    assert session_cookie["secure"] and session_cookie["httponly"]
    assert session_cookie["samesite"] == "Lax"
    assert device_cookie["secure"] and device_cookie["httponly"]
    response = client.post("/api/v1/auth/logout/", HTTP_HOST="alpha.localhost")
    assert response.status_code == 403
    assert response.json() == {"code": "csrf_failed"}
