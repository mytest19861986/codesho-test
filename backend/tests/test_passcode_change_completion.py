from threading import Barrier, Thread
from unittest.mock import patch

import pytest
from django.db import DatabaseError, close_old_connections, connection
from django.test import Client

from config.passcode_change_completion import CompletionStatus, complete_forced_passcode_change
from modules.identity.abuse import AbuseDecision, AbuseReason
from modules.identity.challenge import verify_challenge_secret
from modules.identity.challenge_cookie import COOKIE_NAME, parse_challenge_cookie
from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.identity.passcodes import set_passcode, verify_passcode
from modules.platform_event.security_audit import SecurityAuditError
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


def csrf_client() -> Client:
    return Client(enforce_csrf_checks=True)


def csrf_headers(client: Client) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf/", HTTP_HOST="alpha.localhost")
    assert response.status_code == 204
    return {"HTTP_X_CSRFTOKEN": response.cookies["csrftoken"].value}


def login(client: Client, headers: dict[str, str]):
    return client.post(
        "/api/v1/auth/passcode/login/",
        {"username": "learner", "passcode": "123456"},
        content_type="application/json",
        HTTP_HOST="alpha.localhost",
        **headers,
    )


def allowed() -> AbuseDecision:
    return AbuseDecision(True, AbuseReason.ALLOWED, 0, 0, False)


@pytest.fixture(autouse=True)
def completion_abuse_available():
    with (
        patch(
            "config.passcode_change_completion.preflight_completion_attempt", return_value=allowed()
        ),
        patch(
            "config.passcode_change_completion.record_failed_completion_attempt",
            return_value=allowed(),
        ),
        patch(
            "config.passcode_change_completion.record_successful_completion_attempt",
            return_value=allowed(),
        ),
    ):
        yield


@pytest.fixture
def tenant_member(settings, db):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant = Tenant.objects.create(slug="alpha", name="Alpha")
    user = User.objects.create_user(username="learner", email="learner@example.com")
    set_passcode(user, "123456", must_change=True)
    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant, user=user, role=TenantMembership.Role.LEARNER
        )
    return tenant, user


@pytest.mark.django_db(transaction=True)
def test_completion_consumes_challenge_and_requires_a_fresh_login(tenant_member):
    tenant, user = tenant_member
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.passcode_change_issuance.append_security_event"),
    ):
        assert login(client, headers).status_code == 403
    cookie = parse_challenge_cookie(client.cookies[COOKIE_NAME].value)
    with tenant_atomic(tenant.id):
        issued = PasscodeChangeChallenge.objects.get(selector=cookie.selector)
    assert issued.secret_digest is not None
    assert verify_challenge_secret(cookie.secret, bytes(issued.secret_digest), issued.pepper_id)
    assert issued.state == PasscodeChangeChallenge.State.ACTIVE
    assert issued.credential_version == PasscodeCredential.objects.get(user=user).credential_version
    csrf_cookie = client.cookies["csrftoken"].value
    challenge_cookie = client.cookies[COOKIE_NAME].value
    client.cookies.clear()
    client.cookies["csrftoken"] = csrf_cookie
    client.cookies[COOKIE_NAME] = challenge_cookie
    epoch_before = user.session_auth_epoch
    with (
        patch("config.passcode_change_completion.append_security_event"),
        patch(
            "config.auth_views.parse_challenge_cookie",
            wraps=parse_challenge_cookie,
        ) as parser,
    ):
        response = client.post(
            "/api/v1/auth/passcode/change/complete/",
            {"newPasscode": "654321"},
            content_type="application/json",
            HTTP_HOST="alpha.localhost",
            **headers,
        )
    assert parser.called
    assert response.status_code == 204
    assert response.cookies[COOKIE_NAME]["max-age"] == 0
    assert "_auth_user_id" not in client.session
    user.refresh_from_db()
    credential = PasscodeCredential.objects.get(user=user)
    assert user.session_auth_epoch == epoch_before + 1
    assert credential.must_change is False and credential.credential_version == 2
    assert verify_passcode(user, "654321").valid
    with tenant_atomic(tenant.id):
        challenge = PasscodeChangeChallenge.objects.get(credential=credential)
    assert challenge.state == PasscodeChangeChallenge.State.CONSUMED
    assert challenge.secret_digest is None


@pytest.mark.django_db(transaction=True)
def test_same_passcode_keeps_the_active_challenge_usable(tenant_member):
    tenant, user = tenant_member
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.passcode_change_issuance.append_security_event"),
    ):
        assert login(client, headers).status_code == 403
    cookie_value = client.cookies[COOKIE_NAME].value
    csrf_cookie = client.cookies["csrftoken"].value
    client.cookies.clear()
    client.cookies[COOKIE_NAME] = cookie_value
    client.cookies["csrftoken"] = csrf_cookie
    before = PasscodeCredential.objects.get(user=user)
    with patch("config.passcode_change_completion.append_security_event"):
        response = client.post(
            "/api/v1/auth/passcode/change/complete/",
            {"newPasscode": "123456"},
            content_type="application/json",
            HTTP_HOST="alpha.localhost",
            **headers,
        )
    assert response.status_code == 409
    assert COOKIE_NAME not in response.cookies
    after = PasscodeCredential.objects.get(user=user)
    assert after.credential_version == before.credential_version
    with tenant_atomic(tenant.id):
        assert PasscodeChangeChallenge.objects.get(credential=after).state == "active"


@pytest.mark.django_db(transaction=True)
def test_replay_cannot_replace_the_credential_twice(tenant_member):
    tenant, user = tenant_member
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.passcode_change_issuance.append_security_event"),
    ):
        assert login(client, headers).status_code == 403
    csrf_cookie = client.cookies["csrftoken"].value
    challenge_cookie = client.cookies[COOKIE_NAME].value
    client.cookies.clear()
    client.cookies["csrftoken"] = csrf_cookie
    client.cookies[COOKIE_NAME] = challenge_cookie
    with patch("config.passcode_change_completion.append_security_event"):
        assert (
            client.post(
                "/api/v1/auth/passcode/change/complete/",
                {"newPasscode": "654321"},
                content_type="application/json",
                HTTP_HOST="alpha.localhost",
                **headers,
            ).status_code
            == 204
        )
    credential = PasscodeCredential.objects.get(user=user)
    assert credential.credential_version == 2
    replay = client.post(
        "/api/v1/auth/passcode/change/complete/",
        {"newPasscode": "000000"},
        content_type="application/json",
        HTTP_HOST="alpha.localhost",
        HTTP_COOKIE=f"csrftoken={csrf_cookie}; {COOKIE_NAME}={challenge_cookie}",
        **headers,
    )
    assert replay.status_code == 401
    assert PasscodeCredential.objects.get(user=user).credential_version == 2


@pytest.mark.django_db
def test_completion_csrf_failure_records_only_public_abuse_signals(tenant_member):
    client = csrf_client()
    with patch(
        "config.auth_views.record_failed_completion_attempt", return_value=allowed()
    ) as recorded:
        response = client.post(
            "/api/v1/auth/passcode/change/complete/",
            {"newPasscode": "654321"},
            content_type="application/json",
            HTTP_HOST="alpha.localhost",
        )
    assert response.status_code == 403
    signals = recorded.call_args.args[0]
    assert signals.account_subject is None
    assert signals.challenge_subject is None


@pytest.mark.django_db
def test_malformed_completion_cookie_uses_public_abuse_signals(tenant_member):
    client = csrf_client()
    headers = csrf_headers(client)
    client.cookies[COOKIE_NAME] = "invalid"
    with patch(
        "config.auth_views.record_failed_completion_attempt", return_value=allowed()
    ) as recorded:
        response = client.post(
            "/api/v1/auth/passcode/change/complete/",
            {"newPasscode": "654321"},
            content_type="application/json",
            HTTP_HOST="alpha.localhost",
            **headers,
        )
    assert response.status_code == 401
    assert response.cookies[COOKIE_NAME]["max-age"] == 0
    signals = recorded.call_args.args[0]
    assert signals.account_subject is None
    assert signals.challenge_subject is None


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "failure",
    [SecurityAuditError("audit unavailable"), DatabaseError("database unavailable")],
)
def test_failure_after_credential_mutation_rolls_back_completion(tenant_member, failure):
    tenant, user = tenant_member
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.passcode_change_issuance.append_security_event"),
    ):
        assert login(client, headers).status_code == 403
    challenge_cookie = client.cookies[COOKIE_NAME].value
    csrf_cookie = client.cookies["csrftoken"].value
    client.cookies.clear()
    client.cookies[COOKIE_NAME] = challenge_cookie
    client.cookies["csrftoken"] = csrf_cookie
    before_credential = PasscodeCredential.objects.get(user=user)
    with tenant_atomic(tenant.id):
        before_challenge = PasscodeChangeChallenge.objects.get(
            selector=parse_challenge_cookie(challenge_cookie).selector
        )
    with patch(
        "config.passcode_change_completion.append_security_event",
        side_effect=failure,
    ):
        response = client.post(
            "/api/v1/auth/passcode/change/complete/",
            {"newPasscode": "654321"},
            content_type="application/json",
            HTTP_HOST="alpha.localhost",
            **headers,
        )
    assert response.status_code == 503
    assert COOKIE_NAME not in response.cookies
    user.refresh_from_db()
    after_credential = PasscodeCredential.objects.get(user=user)
    assert after_credential.encoded_hash == before_credential.encoded_hash
    assert after_credential.credential_version == before_credential.credential_version
    assert after_credential.must_change is True
    assert user.session_auth_epoch == 1
    with tenant_atomic(tenant.id):
        after_challenge = PasscodeChangeChallenge.objects.get(pk=before_challenge.pk)
    assert after_challenge.state == PasscodeChangeChallenge.State.ACTIVE
    assert after_challenge.secret_digest == before_challenge.secret_digest


@pytest.mark.django_db(transaction=True)
def test_postgres_parallel_completion_consumes_a_challenge_once(tenant_member):
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific completion concurrency contract")
    tenant, user = tenant_member
    client = csrf_client()
    headers = csrf_headers(client)
    with (
        patch("config.authentication.preflight_attempt", return_value=allowed()),
        patch("config.authentication.record_successful_attempt", return_value=allowed()),
        patch("config.passcode_change_issuance.append_security_event"),
    ):
        assert login(client, headers).status_code == 403
    cookie = parse_challenge_cookie(client.cookies[COOKIE_NAME].value)
    start = Barrier(2)
    results = []
    audit_events = []
    def submit() -> None:
        close_old_connections()
        try:
            start.wait(timeout=10)
            with (
                patch(
                    "config.passcode_change_completion.preflight_completion_attempt",
                    return_value=allowed(),
                ),
                patch(
                    "config.passcode_change_completion.record_successful_completion_attempt",
                    return_value=allowed(),
                ),
            ):
                results.append(
                    complete_forced_passcode_change(
                        tenant=tenant, selector=cookie.selector, secret=cookie.secret,
                        new_passcode="654321", client_ip="127.0.0.1", device_id=None,
                    ).status
                )
        finally:
            close_old_connections()
    threads = [Thread(target=submit), Thread(target=submit)]
    with patch(
        "config.passcode_change_completion.append_security_event",
        side_effect=lambda event: audit_events.append(event),
    ):
        [thread.start() for thread in threads]
        [thread.join(timeout=20) for thread in threads]
    assert all(not thread.is_alive() for thread in threads)
    assert sorted(results) == [CompletionStatus.INVALID, CompletionStatus.SUCCESS]
    user.refresh_from_db()
    credential = PasscodeCredential.objects.get(user=user)
    assert credential.credential_version == 2
    assert credential.must_change is False
    assert user.session_auth_epoch == 2
    with tenant_atomic(tenant.id):
        challenge = PasscodeChangeChallenge.objects.get(selector=cookie.selector)
    assert challenge.state == PasscodeChangeChallenge.State.CONSUMED
    assert challenge.secret_digest is None
    assert [event.event_type.value for event in audit_events].count("passcode_changed") == 1
    assert [event.event_type.value for event in audit_events].count(
        "passcode_change_challenge_consumed"
    ) == 1
    successful_keys = {
        event.event_type.value: event.idempotency_key
        for event in audit_events
        if event.event_type.value in {
            "passcode_changed",
            "passcode_change_challenge_consumed",
        }
    }
    assert set(successful_keys) == {
        "passcode_changed",
        "passcode_change_challenge_consumed",
    }
    assert len(set(successful_keys.values())) == 2
    assert all(str(challenge.id) in key for key in successful_keys.values())
    replay = complete_forced_passcode_change(
        tenant=tenant, selector=cookie.selector, secret=cookie.secret,
        new_passcode="000000", client_ip="127.0.0.1", device_id=None,
    )
    assert replay.status is CompletionStatus.INVALID
