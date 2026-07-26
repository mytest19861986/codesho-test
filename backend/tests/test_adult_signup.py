import os
import subprocess
import sys
from importlib import import_module
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError
from django.db import DatabaseError, connection
from django.test import Client
from psycopg import connect
from psycopg.errors import InsufficientPrivilege, RaiseException

from config.adult_signup import AdultSignupRateDecision, check_adult_signup_rate
from modules.identity.models import AdultAgeAttestation
from modules.platform_event.models import IdentitySecurityEvent
from modules.platform_event.security_audit import (
    AppendAuditResult,
    SecurityAuditError,
    SecurityEventType,
    append_security_event,
)
from modules.platform_tenant.models import Tenant

PATH = "/api/v1/auth/signup/adult-attestation/"
POLICY_VERSION = "adult-internal-2026-07-26"


@pytest.fixture
def adult_signup(settings, db):
    settings.ADULT_SIGNUP_MODE = "internal_test"
    settings.ADULT_SIGNUP_POLICY_VERSION = POLICY_VERSION
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    return Tenant.objects.create(slug="alpha", name="Alpha")


@pytest.fixture(autouse=True)
def allow_rate_limit():
    with patch(
        "config.adult_signup.check_adult_signup_rate",
        return_value=AdultSignupRateDecision(True, 0),
    ):
        yield


def csrf_client(host: str = "alpha.localhost") -> tuple[Client, dict[str, str]]:
    client = Client(enforce_csrf_checks=True)
    response = client.get("/api/v1/auth/csrf/", HTTP_HOST=host)
    assert response.status_code == 204
    return client, {"HTTP_X_CSRFTOKEN": response.cookies["csrftoken"].value}


def payload(subject_id=None, **overrides):
    values = {
        "adultAttestation": True,
        "policyVersion": POLICY_VERSION,
        "subjectId": str(subject_id or uuid4()),
    }
    values.update(overrides)
    return values


def post(client, headers, body, host: str = "alpha.localhost"):
    return client.post(
        PATH,
        body,
        content_type="application/json",
        HTTP_HOST=host,
        **headers,
    )


@pytest.mark.django_db
def test_feature_is_not_discoverable_when_disabled(settings):
    settings.ADULT_SIGNUP_MODE = "disabled"
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost", "localhost", "testserver"]
    Tenant.objects.create(slug="alpha", name="Alpha")
    client, headers = csrf_client()
    response = post(client, headers, payload())
    assert response.status_code == 404
    assert response.json() == {"code": "not_found"}
    assert AdultAgeAttestation.objects.count() == 0


@pytest.mark.django_db
def test_csrf_is_required(adult_signup):
    response = Client(enforce_csrf_checks=True).post(
        PATH,
        payload(),
        content_type="application/json",
        HTTP_HOST="alpha.localhost",
    )
    assert response.status_code == 403
    assert AdultAgeAttestation.objects.count() == 0


@pytest.mark.django_db
def test_explicit_adult_attestation_creates_minimal_immutable_evidence(adult_signup):
    subject_id = uuid4()
    client, headers = csrf_client()
    with patch(
        "config.adult_signup.append_security_event",
        return_value=AppendAuditResult(event_id=uuid4(), created=True),
    ) as append:
        response = post(client, headers, payload(subject_id))

    assert response.status_code == 201
    assert set(response.json()) == {
        "attestationId",
        "attestedAt",
        "policyVersion",
        "source",
        "status",
    }
    attestation = AdultAgeAttestation.objects.get()
    assert attestation.tenant_id == adult_signup.id
    assert attestation.subject_id == subject_id
    assert attestation.status == AdultAgeAttestation.Status.ADULT_ATTESTED
    assert attestation.source == AdultAgeAttestation.Source.INTERNAL_TEST_API
    assert attestation.policy_version == POLICY_VERSION
    event = append.call_args.args[0]
    assert event.event_id == attestation.audit_event_id
    assert event.event_type is SecurityEventType.ADULT_AGE_ATTESTATION_ACCEPTED
    assert event.subject_user_id == subject_id
    assert event.tenant_id == adult_signup.id
    assert not hasattr(event, "metadata")


@pytest.mark.django_db
def test_false_attestation_is_audited_and_rejected(adult_signup):
    subject_id = uuid4()
    client, headers = csrf_client()
    with patch(
        "config.adult_signup.append_security_event",
        return_value=AppendAuditResult(event_id=uuid4(), created=True),
    ) as append:
        response = post(client, headers, payload(subject_id, adultAttestation=False))

    assert response.status_code == 403
    assert response.json() == {"code": "adult_attestation_required"}
    assert AdultAgeAttestation.objects.count() == 0
    event = append.call_args.args[0]
    assert (
        event.event_type
        is SecurityEventType.ADULT_SIGNUP_REJECTED_AGE_ATTESTATION_MISSING
    )
    assert event.subject_user_id == subject_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "body",
    [
        {},
        {"adultAttestation": True},
        payload(adultAttestation=1),
        payload(birthDate="1380-01-01"),
        payload(age=25),
        payload(nationalId="0012345678"),
        payload(guardianId=str(uuid4())),
        payload(subjectId=str(uuid4()).upper()),
        payload(subjectId="not-a-uuid"),
    ],
)
def test_missing_tampered_or_identity_data_is_rejected(adult_signup, body):
    client, headers = csrf_client()
    with patch("config.adult_signup.append_security_event") as append:
        response = post(client, headers, body)
    assert response.status_code == 400
    assert response.json() == {"code": "invalid_request"}
    assert AdultAgeAttestation.objects.count() == 0
    append.assert_not_called()


@pytest.mark.django_db
def test_policy_version_must_match_server_contract(adult_signup):
    client, headers = csrf_client()
    with patch("config.adult_signup.append_security_event") as append:
        response = post(client, headers, payload(policyVersion="old-policy"))
    assert response.status_code == 409
    assert response.json() == {"code": "policy_version_mismatch"}
    assert AdultAgeAttestation.objects.count() == 0
    append.assert_not_called()


@pytest.mark.django_db
def test_retry_is_idempotent_for_tenant_subject_and_policy(adult_signup):
    subject_id = uuid4()
    client, headers = csrf_client()
    with patch(
        "config.adult_signup.append_security_event",
        return_value=AppendAuditResult(event_id=uuid4(), created=True),
    ) as append:
        first = post(client, headers, payload(subject_id))
        second = post(client, headers, payload(subject_id))
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["attestationId"] == second.json()["attestationId"]
    assert AdultAgeAttestation.objects.count() == 1
    assert append.call_count == 2
    assert append.call_args_list[0].args[0].event_id == append.call_args_list[1].args[0].event_id
    assert (
        append.call_args_list[0].args[0].idempotency_key
        == append.call_args_list[1].args[0].idempotency_key
    )


@pytest.mark.django_db
def test_same_subject_is_isolated_by_tenant(adult_signup):
    subject_id = uuid4()
    Tenant.objects.create(slug="beta", name="Beta")
    first_client, first_headers = csrf_client()
    second_client, second_headers = csrf_client("beta.localhost")
    with patch(
        "config.adult_signup.append_security_event",
        return_value=AppendAuditResult(event_id=uuid4(), created=True),
    ):
        first = post(first_client, first_headers, payload(subject_id))
        second = post(
            second_client,
            second_headers,
            payload(subject_id),
            host="beta.localhost",
        )
    assert first.status_code == 201
    assert second.status_code == 201
    assert AdultAgeAttestation.objects.filter(subject_id=subject_id).count() == 2


@pytest.mark.django_db
def test_audit_failure_rolls_back_acceptance(adult_signup):
    client, headers = csrf_client()
    with patch(
        "config.adult_signup.append_security_event",
        side_effect=SecurityAuditError("audit unavailable"),
    ):
        response = post(client, headers, payload())
    assert response.status_code == 503
    assert response.json() == {"code": "temporarily_unavailable"}
    assert AdultAgeAttestation.objects.count() == 0


@pytest.mark.django_db
def test_audit_failure_fails_closed_for_rejection(adult_signup):
    client, headers = csrf_client()
    with patch(
        "config.adult_signup.append_security_event",
        side_effect=SecurityAuditError("audit unavailable"),
    ):
        response = post(client, headers, payload(adultAttestation=False))
    assert response.status_code == 503
    assert AdultAgeAttestation.objects.count() == 0


@pytest.mark.django_db
def test_rate_limit_blocks_before_persistence_or_audit(adult_signup):
    client, headers = csrf_client()
    with (
        patch(
            "config.adult_signup.check_adult_signup_rate",
            return_value=AdultSignupRateDecision(False, 47),
        ),
        patch("config.adult_signup.append_security_event") as append,
    ):
        response = post(client, headers, payload())
    assert response.status_code == 429
    assert response.json() == {"code": "try_again_later"}
    assert response["Retry-After"] == "47"
    assert AdultAgeAttestation.objects.count() == 0
    append.assert_not_called()


@pytest.mark.django_db
def test_rate_limit_backend_failure_is_fail_closed(adult_signup):
    client, headers = csrf_client()
    with (
        patch(
            "config.adult_signup.check_adult_signup_rate",
            return_value=AdultSignupRateDecision(False, 5, backend_available=False),
        ),
        patch("config.adult_signup.append_security_event") as append,
    ):
        response = post(client, headers, payload())
    assert response.status_code == 503
    assert response.json() == {"code": "temporarily_unavailable"}
    assert AdultAgeAttestation.objects.count() == 0
    append.assert_not_called()


def test_rate_limit_uses_only_hmac_anonymous_redis_keys(settings):
    settings.ADULT_SIGNUP_RATE_WINDOW_SECONDS = 900
    settings.ADULT_SIGNUP_SUBJECT_MAX_ATTEMPTS = 5
    settings.ADULT_SIGNUP_IP_MAX_ATTEMPTS = 30
    tenant_id = uuid4()
    subject_id = uuid4()
    raw_ip = "203.0.113.42"
    with patch("config.adult_signup.redis.Redis.from_url") as from_url:
        from_url.return_value.eval.return_value = [1, 900_000, 1, 900_000]
        decision = check_adult_signup_rate(tenant_id, subject_id, raw_ip)
    assert decision == AdultSignupRateDecision(True, 0)
    arguments = from_url.return_value.eval.call_args.args
    redis_keys = arguments[2:4]
    assert raw_ip not in " ".join(redis_keys)
    assert str(subject_id) not in " ".join(redis_keys)
    assert all(key.startswith("codesho:adult-signup:v1:") for key in redis_keys)


def test_rate_limit_rejects_malformed_redis_response(settings):
    with patch("config.adult_signup.redis.Redis.from_url") as from_url:
        from_url.return_value.eval.return_value = ["malformed"]
        decision = check_adult_signup_rate(uuid4(), uuid4(), "203.0.113.42")
    assert decision.backend_available is False
    assert decision.allowed is False


def test_rate_limit_fails_closed_when_hmac_key_is_invalid(settings):
    settings.PASSCODE_SIGNAL_HMAC_KEY = "not-base64"
    decision = check_adult_signup_rate(uuid4(), uuid4(), "203.0.113.42")
    assert decision.backend_available is False
    assert decision.allowed is False


@pytest.mark.django_db
def test_application_model_rejects_update_and_delete(adult_signup):
    attestation = AdultAgeAttestation.objects.create(
        tenant_id=adult_signup.id,
        subject_id=uuid4(),
        policy_version=POLICY_VERSION,
    )
    with pytest.raises(ValidationError, match="immutable"):
        attestation.save()
    with pytest.raises(ValidationError, match="append-only"):
        attestation.delete()


def test_model_has_no_prohibited_age_or_identity_fields():
    field_names = {field.name for field in AdultAgeAttestation._meta.get_fields()}
    assert field_names == {
        "id",
        "tenant_id",
        "subject_id",
        "status",
        "policy_version",
        "source",
        "audit_event_id",
        "attested_at",
    }
    assert field_names.isdisjoint(
        {
            "age",
            "birth_date",
            "birth_year",
            "identity_document",
            "national_id",
            "guardian_id",
            "ip_address",
            "payload",
        }
    )


def test_production_settings_reject_internal_mode():
    environment = os.environ.copy()
    environment.update(
        {
            "ADULT_SIGNUP_MODE": "internal_test",
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
            "DJANGO_SECRET_KEY": "production-test-secret",
            "PASSCODE_ACTIVE_PEPPER_ID": "test-v1",
            "PASSCODE_PEPPERS": (
                '{"test-v1":"dGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3Q="}'
            ),
            "PASSCODE_SIGNAL_HMAC_KEY": (
                "dGVzdC1zaWduYWwtaG1hYy1rZXktdGVzdC1zaWduYWwtaG1hYy1rZXk="
            ),
        }
    )
    result = subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "adult signup must remain disabled in production" in result.stderr


def test_audit_allow_list_migration_is_forward_only_and_preserves_prior_values():
    previous = import_module(
        "modules.platform_event.migrations.0009_platform_operator_admin_events"
    )
    current = import_module("modules.platform_event.migrations.0010_adult_signup_events")
    assert set(previous.EVENT_TYPES_AFTER) < set(current.SECURITY_EVENT_TYPES)
    assert set(previous.REASON_CODES_AFTER) < set(current.SECURITY_EVENT_REASON_CODES)
    with pytest.raises(Exception, match="must move forward"):
        current.irreversible(None, None)


def require_postgres():
    if connection.vendor != "postgresql":
        pytest.skip("requires PostgreSQL")


@pytest.mark.django_db(transaction=True)
def test_postgres_trigger_and_runtime_privileges_are_append_only(adult_signup):
    require_postgres()
    migrator_url = os.environ.get("DATABASE_MIGRATOR_TEST_URL")
    runtime_url = os.environ.get("DATABASE_RUNTIME_TEST_URL")
    if not migrator_url or not runtime_url:
        pytest.skip("database role URLs are not configured")

    attestation = AdultAgeAttestation.objects.create(
        tenant_id=adult_signup.id,
        subject_id=uuid4(),
        policy_version=POLICY_VERSION,
    )
    with connect(migrator_url, autocommit=True) as migrator, migrator.cursor() as cursor:
        with pytest.raises(RaiseException):
            cursor.execute(
                "UPDATE codesho.identity_adultageattestation "
                "SET policy_version = 'tampered' WHERE id = %s",
                (str(attestation.id),),
            )
        with pytest.raises(RaiseException):
            cursor.execute(
                "DELETE FROM codesho.identity_adultageattestation WHERE id = %s",
                (str(attestation.id),),
            )

    for statement in (
        "UPDATE codesho.identity_adultageattestation SET policy_version = 'tampered'",
        "DELETE FROM codesho.identity_adultageattestation",
        "TRUNCATE codesho.identity_adultageattestation",
    ):
        with (
            connect(runtime_url, autocommit=True) as runtime,
            runtime.cursor() as cursor,
            pytest.raises((InsufficientPrivilege, RaiseException, DatabaseError)),
        ):
            cursor.execute(statement)


@pytest.mark.django_db(transaction=True)
def test_postgres_endpoint_commits_attestation_and_audit_atomically(adult_signup):
    require_postgres()
    subject_id = uuid4()
    client, headers = csrf_client()
    with patch(
        "config.adult_signup.append_security_event",
        wraps=append_security_event,
    ):
        response = post(client, headers, payload(subject_id))
    assert response.status_code == 201
    attestation = AdultAgeAttestation.objects.get(subject_id=subject_id)
    event = IdentitySecurityEvent.objects.get(event_id=attestation.audit_event_id)
    assert event.event_type == "adult_age_attestation_accepted"
    assert event.reason_code == "adult_attested"
    assert event.subject_user_id == subject_id
    assert event.tenant_id == adult_signup.id
