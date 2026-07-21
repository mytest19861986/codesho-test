"""Real PostgreSQL/Redis HTTP release gate for forced passcode change."""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.core.signing import TimestampSigner
from django.db import connection
from django.test import Client

from modules.identity.abuse import _client as _redis_client
from modules.identity.challenge_cookie import COOKIE_NAME
from modules.identity.models import PasscodeChangeChallenge, User
from modules.identity.passcodes import set_passcode
from modules.platform_event.security_audit import SecurityEventType
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


def _client() -> Client:
    return Client(enforce_csrf_checks=True)


def _csrf(client: Client, host: str) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf/", HTTP_HOST=host)
    assert response.status_code == 204
    return {"HTTP_X_CSRFTOKEN": response.cookies["csrftoken"].value}


def _login(client: Client, headers: dict[str, str], passcode: str, host: str):
    return client.post(
        "/api/v1/auth/passcode/login/",
        {"username": "learner", "passcode": passcode},
        content_type="application/json",
        HTTP_HOST=host,
        **headers,
    )


def _audit_rows(*, tenant_id, user_id):
    columns = (
        "event_id",
        "event_type",
        "outcome",
        "reason_code",
        "tenant_id",
        "subject_user_id",
        "actor_user_id",
        "credential_version",
        "correlation_id",
        "idempotency_key",
    )
    # HTTP requests append through their own transaction boundary; reset any
    # stale test-thread snapshot before reading committed audit evidence.
    connection.commit()
    connection.close()
    with tenant_atomic(tenant_id), connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT event_id, event_type, outcome, reason_code, tenant_id,
                   subject_user_id, actor_user_id, credential_version,
                   correlation_id, idempotency_key
            FROM audit.identity_security_event
            WHERE tenant_id = %s OR subject_user_id = %s
            ORDER BY occurred_at, event_id
            """,
            (tenant_id, user_id),
        )
        rows = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
    assert all(
        row["tenant_id"] == tenant_id and row["subject_user_id"] == user_id
        for row in rows
    )
    return rows


def _event_count(rows, event_type: SecurityEventType) -> int:
    return sum(row["event_type"] == event_type.value for row in rows)


def _audit_event_type_counts() -> dict[str, object]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT event_type, COUNT(*)
            FROM audit.identity_security_event
            GROUP BY event_type
            ORDER BY event_type
            """
        )
        return {event_type: count for event_type, count in cursor.fetchall()}


def _device_signal(client: Client, settings) -> str:
    signed = client.cookies[settings.PASSCODE_DEVICE_COOKIE_NAME].value
    return TimestampSigner(salt="codesho.passcode.device").unsign(signed)


def _challenge_cookie_parts(cookie_value: str) -> tuple[str, str, str]:
    version, selector, secret = cookie_value.split(".")
    assert version == "v1"
    assert selector and secret
    return version, selector, secret


def _assert_bounded_audit_rows(rows, *, forbidden_values=()):
    allowed = {
        "event_id",
        "event_type",
        "outcome",
        "reason_code",
        "tenant_id",
        "subject_user_id",
        "actor_user_id",
        "credential_version",
        "correlation_id",
        "idempotency_key",
    }
    assert all(set(row) == allowed for row in rows)
    rendered = repr(rows)
    assert all(value not in rendered for value in forbidden_values)


@pytest.mark.django_db(transaction=True)
def test_forced_passcode_change_http_release_gate(settings):
    if connection.vendor != "postgresql":
        pytest.skip("real PostgreSQL/Redis release gate")
    _redis_client().ping()
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant = Tenant.objects.create(slug=f"alpha-{uuid4()}", name="Alpha")
    alpha_host = f"{tenant.slug}.localhost"
    user = User.objects.create_user(username="learner", email=f"{uuid4()}@example.com")
    credential = set_passcode(user, "123456", must_change=False)
    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant, user=user, role=TenantMembership.Role.LEARNER
        )

    prior = _client()
    assert _login(prior, _csrf(prior, alpha_host), "123456", alpha_host).status_code == 204
    prior_session = prior.session.session_key
    credential.must_change = True
    credential.save(update_fields=["must_change"])

    flow = _client()
    headers = _csrf(flow, alpha_host)
    issued_audit_baseline = _audit_rows(tenant_id=tenant.id, user_id=user.id)
    issued = _login(flow, headers, "123456", alpha_host)
    assert issued.status_code == 403 and issued.json() == {"code": "passcode_change_required"}
    challenge_cookie = issued.cookies[COOKIE_NAME]
    assert challenge_cookie["secure"] and challenge_cookie["httponly"]
    assert "_auth_user_id" not in flow.session
    cookie_value = challenge_cookie.value
    cookie_version, cookie_selector, cookie_secret = _challenge_cookie_parts(cookie_value)
    user.refresh_from_db()
    version_before, epoch_before = credential.credential_version, user.session_auth_epoch
    with tenant_atomic(tenant.id):
        issued_challenge = PasscodeChangeChallenge.objects.get(credential=credential)
    sensitive_issue_values = (
        "123456",
        "654321",
        "000000",
        cookie_value,
        cookie_version,
        cookie_selector,
        cookie_secret,
        str(issued_challenge.selector),
        bytes(issued_challenge.secret_digest).hex(),
        "127.0.0.1",
        "learner",
        _device_signal(flow, settings),
    )
    issued_audits = _audit_rows(tenant_id=tenant.id, user_id=user.id)
    assert len(issued_audits) == len(issued_audit_baseline) + 1
    assert _event_count(issued_audits, SecurityEventType.PASSCODE_CHANGE_CHALLENGE_ISSUED) == 1
    _assert_bounded_audit_rows(issued_audits, forbidden_values=sensitive_issue_values)

    completed = flow.post(
        "/api/v1/auth/passcode/change/complete/",
        {"newPasscode": "654321"},
        content_type="application/json",
        HTTP_HOST=alpha_host,
        **headers,
    )
    assert completed.status_code == 204 and completed.cookies[COOKIE_NAME]["max-age"] == 0
    assert "_auth_user_id" not in flow.session
    credential.refresh_from_db()
    user.refresh_from_db()
    assert (
        credential.credential_version == version_before + 1
        and user.session_auth_epoch == epoch_before + 1
    )
    with tenant_atomic(tenant.id):
        challenge = PasscodeChangeChallenge.objects.get(credential=credential)
    assert (
        challenge.state == PasscodeChangeChallenge.State.CONSUMED
        and challenge.secret_digest is None
    )
    assert prior.get("/api/v1/auth/session/", HTTP_HOST=alpha_host).status_code == 401

    completed_audits = _audit_rows(tenant_id=tenant.id, user_id=user.id)
    assert _event_count(completed_audits, SecurityEventType.PASSCODE_CHANGED) == 1, (
        _audit_event_type_counts()
    )
    assert (
        _event_count(completed_audits, SecurityEventType.PASSCODE_CHANGE_CHALLENGE_CONSUMED)
        == 1
    ), _audit_event_type_counts()
    _assert_bounded_audit_rows(completed_audits, forbidden_values=sensitive_issue_values)

    replay = flow.post(
        "/api/v1/auth/passcode/change/complete/",
        {"newPasscode": "000000"},
        content_type="application/json",
        HTTP_HOST=alpha_host,
        HTTP_COOKIE=f"csrftoken={flow.cookies['csrftoken'].value}; {COOKIE_NAME}={cookie_value}",
        **headers,
    )
    assert replay.status_code == 401
    replay_audits = _audit_rows(tenant_id=tenant.id, user_id=user.id)
    assert _event_count(replay_audits, SecurityEventType.PASSCODE_CHANGED) == 1
    assert _event_count(replay_audits, SecurityEventType.PASSCODE_CHANGE_CHALLENGE_CONSUMED) == 1
    _assert_bounded_audit_rows(replay_audits, forbidden_values=sensitive_issue_values)
    assert _login(flow, _csrf(flow, alpha_host), "123456", alpha_host).status_code == 401
    fresh = _login(flow, _csrf(flow, alpha_host), "654321", alpha_host)
    assert fresh.status_code == 204 and flow.session.session_key != prior_session


@pytest.mark.django_db(transaction=True)
def test_same_as_current_and_cross_tenant_cookie_fail_closed(settings):
    if connection.vendor != "postgresql":
        pytest.skip("real PostgreSQL/Redis release gate")
    _redis_client().ping()
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    tenant = Tenant.objects.create(slug=f"alpha-{uuid4()}", name="Alpha")
    second_tenant = Tenant.objects.create(slug=f"beta-{uuid4()}", name="Beta")
    alpha_host = f"{tenant.slug}.localhost"
    user = User.objects.create_user(username="learner", email=f"{uuid4()}@example.com")
    credential = set_passcode(user, "123456", must_change=True)
    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant, user=user, role=TenantMembership.Role.LEARNER
        )

    client = _client()
    headers = _csrf(client, alpha_host)
    assert _login(client, headers, "123456", alpha_host).status_code == 403
    cookie_value = client.cookies[COOKIE_NAME].value
    cookie_version, cookie_selector, cookie_secret = _challenge_cookie_parts(cookie_value)
    audit_baseline = _audit_rows(tenant_id=tenant.id, user_id=user.id)
    same = client.post(
        "/api/v1/auth/passcode/change/complete/",
        {"newPasscode": "123456"},
        content_type="application/json",
        HTTP_HOST=alpha_host,
        **headers,
    )
    assert same.status_code == 409 and COOKIE_NAME not in same.cookies
    same_audits = _audit_rows(tenant_id=tenant.id, user_id=user.id)
    rejected = [
        row
        for row in same_audits
        if row["event_type"] == SecurityEventType.PASSCODE_CHANGE_REJECTED.value
    ]
    assert len(rejected) == 1, _audit_event_type_counts()
    assert rejected[0]["reason_code"] == "passcode_same_as_current"
    assert len(same_audits) == len(audit_baseline) + 1
    with tenant_atomic(tenant.id):
        same_challenge = PasscodeChangeChallenge.objects.get(credential=credential)
    _assert_bounded_audit_rows(
        same_audits,
        forbidden_values=(
            "123456",
            "654321",
            cookie_value,
            cookie_version,
            cookie_selector,
            cookie_secret,
            str(same_challenge.selector),
            bytes(same_challenge.secret_digest).hex(),
            "127.0.0.1",
            "learner",
            _device_signal(client, settings),
        ),
    )
    with tenant_atomic(tenant.id):
        assert PasscodeChangeChallenge.objects.get(credential=credential).state == "active"
    cross = client.post(
        "/api/v1/auth/passcode/change/complete/",
        {"newPasscode": "654321"},
        content_type="application/json",
        HTTP_HOST=f"{second_tenant.slug}.localhost",
        HTTP_COOKIE=f"csrftoken={client.cookies['csrftoken'].value}; {COOKIE_NAME}={cookie_value}",
        **headers,
    )
    assert cross.status_code == 401
    replacement = client.post(
        "/api/v1/auth/passcode/change/complete/",
        {"newPasscode": "654321"},
        content_type="application/json",
        HTTP_HOST=alpha_host,
        HTTP_COOKIE=f"csrftoken={client.cookies['csrftoken'].value}; {COOKIE_NAME}={cookie_value}",
        **headers,
    )
    assert replacement.status_code == 204
