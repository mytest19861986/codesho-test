from datetime import timedelta
from unittest.mock import patch

import pytest
from django.test import Client
from django.utils import timezone

from config.authentication import LoginResult, LoginStatus
from modules.identity.abuse import AbuseDecision, AbuseReason
from modules.identity.challenge import digest_challenge_secret, generate_challenge_material
from modules.identity.challenge_cookie import COOKIE_NAME, parse_challenge_cookie
from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
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
def test_must_change_login_issues_only_a_committed_secure_challenge(tenant_member):
    tenant, user, _ = tenant_member
    credential = PasscodeCredential.objects.get(user=user)
    credential.must_change = True
    credential.save(update_fields=["must_change"])
    client = csrf_client()
    headers = csrf_headers(client)

    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.passcode_change_issuance.append_security_event") as append,
    ):
        response = login(client, headers)

    assert response.status_code == 403
    assert response.json() == {"code": "passcode_change_required"}
    assert "_auth_user_id" not in client.session
    cookie = response.cookies[COOKIE_NAME]
    parsed = parse_challenge_cookie(cookie.value)
    assert cookie["secure"] and cookie["httponly"]
    assert cookie["samesite"] == "Lax" and cookie["path"] == "/"
    assert cookie["domain"] == "" and int(cookie["max-age"]) == 600
    assert cookie.value not in response.content.decode()
    with tenant_atomic(tenant.id):
        challenge = PasscodeChangeChallenge.objects.get(selector=parsed.selector)
    assert challenge.state == PasscodeChangeChallenge.State.ACTIVE
    assert challenge.secret_digest == digest_challenge_secret(parsed.secret, challenge.pepper_id)
    assert challenge.expires_at - challenge.issued_at == timedelta(seconds=600)
    assert [call.args[0].event_type for call in append.call_args_list] == [
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_ISSUED
    ]


@pytest.mark.django_db(transaction=True)
def test_must_change_login_supersedes_old_challenge_and_records_bounded_audit(tenant_member):
    tenant, user, _ = tenant_member
    credential = PasscodeCredential.objects.get(user=user)
    credential.must_change = True
    credential.save(update_fields=["must_change"])
    material = generate_challenge_material()
    now = timezone.now()
    with tenant_atomic(tenant.id):
        old = PasscodeChangeChallenge.objects.create(
            selector=material.selector,
            tenant=tenant,
            credential=credential,
            credential_version=credential.credential_version,
            secret_digest=digest_challenge_secret(material.secret, credential.pepper_id),
            pepper_id=credential.pepper_id,
            issued_at=now,
            expires_at=now + timedelta(seconds=600),
        )
    client = csrf_client()
    headers = csrf_headers(client)

    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.passcode_change_issuance.append_security_event") as append,
    ):
        assert login(client, headers).status_code == 403

    with tenant_atomic(tenant.id):
        old.refresh_from_db()
        active = PasscodeChangeChallenge.objects.get(state=PasscodeChangeChallenge.State.ACTIVE)
    assert old.state == PasscodeChangeChallenge.State.REVOKED
    assert old.secret_digest is None and old.revoked_at is not None
    assert active.pk != old.pk
    assert [call.args[0].event_type for call in append.call_args_list] == [
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_REVOKED,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_ISSUED,
    ]


@pytest.mark.django_db(transaction=True)
def test_issuance_audit_failure_rolls_back_existing_and_new_challenge(tenant_member):
    tenant, user, _ = tenant_member
    credential = PasscodeCredential.objects.get(user=user)
    credential.must_change = True
    credential.save(update_fields=["must_change"])
    material = generate_challenge_material()
    now = timezone.now()
    with tenant_atomic(tenant.id):
        old = PasscodeChangeChallenge.objects.create(
            selector=material.selector,
            tenant=tenant,
            credential=credential,
            credential_version=credential.credential_version,
            secret_digest=digest_challenge_secret(material.secret, credential.pepper_id),
            pepper_id=credential.pepper_id,
            issued_at=now,
            expires_at=now + timedelta(seconds=600),
        )
    client = csrf_client()
    headers = csrf_headers(client)

    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch(
            "config.passcode_change_issuance.append_security_event",
            side_effect=SecurityAuditError(),
        ),
    ):
        response = login(client, headers)

    assert response.status_code == 503
    cleared = response.cookies[COOKIE_NAME]
    assert cleared["max-age"] == 0 and cleared["path"] == "/"
    with tenant_atomic(tenant.id):
        old.refresh_from_db()
        assert old.state == PasscodeChangeChallenge.State.ACTIVE
        assert PasscodeChangeChallenge.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_challenge_material_failure_is_fail_closed_without_challenge_state(tenant_member):
    tenant, user, _ = tenant_member
    credential = PasscodeCredential.objects.get(user=user)
    credential.must_change = True
    credential.save(update_fields=["must_change"])
    client = csrf_client()
    headers = csrf_headers(client)

    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch(
            "config.passcode_change_issuance.generate_challenge_material",
            side_effect=RuntimeError(),
        ),
    ):
        response = login(client, headers)

    assert response.status_code == 503
    with tenant_atomic(tenant.id):
        assert PasscodeChangeChallenge.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_material_failure_keeps_an_existing_active_challenge_usable(tenant_member):
    tenant, user, _ = tenant_member
    credential = PasscodeCredential.objects.get(user=user)
    credential.must_change = True
    credential.save(update_fields=["must_change"])
    material = generate_challenge_material()
    now = timezone.now()
    with tenant_atomic(tenant.id):
        old = PasscodeChangeChallenge.objects.create(
            selector=material.selector,
            tenant=tenant,
            credential=credential,
            credential_version=credential.credential_version,
            secret_digest=digest_challenge_secret(material.secret, credential.pepper_id),
            pepper_id=credential.pepper_id,
            issued_at=now,
            expires_at=now + timedelta(seconds=600),
        )
    client = csrf_client()
    headers = csrf_headers(client)

    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch(
            "config.passcode_change_issuance.generate_challenge_material",
            side_effect=RuntimeError(),
        ),
    ):
        response = login(client, headers)

    assert response.status_code == 503
    with tenant_atomic(tenant.id):
        old.refresh_from_db()
        assert old.state == PasscodeChangeChallenge.State.ACTIVE
        assert old.secret_digest == digest_challenge_secret(material.secret, old.pepper_id)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "payload, expected_status",
    [({"passcode": "000000"}, 401), ({"passcode": "not-a-passcode"}, 400)],
)
def test_non_issuing_login_paths_clear_a_stale_challenge_cookie(
    tenant_member, payload, expected_status
):
    client = csrf_client()
    headers = csrf_headers(client)
    client.cookies[COOKIE_NAME] = "stale"
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_failed_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
    ):
        response = login(client, headers, **payload)
    assert response.status_code == expected_status
    cleared = response.cookies[COOKIE_NAME]
    assert cleared["max-age"] == 0 and cleared["path"] == "/"
    assert cleared["secure"] and cleared["httponly"] and cleared["samesite"] == "Lax"


@pytest.mark.django_db(transaction=True)
def test_normal_login_clears_a_stale_challenge_cookie(tenant_member):
    client = csrf_client()
    headers = csrf_headers(client)
    client.cookies[COOKIE_NAME] = "stale"
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.authentication.append_security_event"),
    ):
        response = login(client, headers)
    assert response.status_code == 204
    cleared = response.cookies[COOKIE_NAME]
    assert cleared["max-age"] == 0 and cleared["path"] == "/"
    assert cleared["secure"] and cleared["httponly"] and cleared["samesite"] == "Lax"


@pytest.mark.django_db(transaction=True)
def test_inconsistent_required_status_fails_closed_and_clears_stale_cookie(tenant_member):
    client = csrf_client()
    headers = csrf_headers(client)
    client.cookies[COOKIE_NAME] = "stale"
    client.cookies.pop("codesho_device", None)
    with patch(
        "config.auth_views.authenticate_passcode",
        return_value=LoginResult(LoginStatus.PASSCODE_CHANGE_REQUIRED),
    ):
        response = login(client, headers)
    assert response.status_code == 503
    assert response.json() == {"code": "authentication_temporarily_unavailable"}
    cleared = response.cookies[COOKIE_NAME]
    assert cleared["max-age"] == 0 and cleared["path"] == "/"
    assert cleared["secure"] and cleared["httponly"] and cleared["samesite"] == "Lax"
    assert response.cookies["codesho_device"]
