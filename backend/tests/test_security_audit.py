import os
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.db import connection
from psycopg import connect
from psycopg.errors import CheckViolation, InsufficientPrivilege, RaiseException

from modules.platform_event.security_audit import (
    AppendAuditResult,
    SecurityAuditError,
    SecurityAuditEvent,
    SecurityEventOutcome,
    SecurityEventType,
    append_security_event,
)


def make_event(**overrides) -> SecurityAuditEvent:
    values = {
        "event_id": uuid4(),
        "event_type": SecurityEventType.PASSCODE_CREATED,
        "outcome": SecurityEventOutcome.SUCCESS,
        "correlation_id": uuid4(),
    }
    values.update(overrides)
    return SecurityAuditEvent(**values)


def test_security_audit_event_is_typed_and_has_no_metadata_field():
    event = make_event(reason_code="credential_created")
    assert event.event_type is SecurityEventType.PASSCODE_CREATED
    assert event.outcome is SecurityEventOutcome.SUCCESS
    assert not hasattr(event, "metadata")


def test_audit_failure_does_not_expose_connection_details():
    with patch(
        "modules.platform_event.security_audit.connection.cursor",
        side_effect=RuntimeError("postgresql://username:password@database/audit"),
    ), pytest.raises(SecurityAuditError, match="security audit append failed") as exc_info:
        append_security_event(make_event())
    assert "postgresql" not in str(exc_info.value)
    assert "password" not in str(exc_info.value)


@pytest.mark.django_db(transaction=True)
def test_runtime_can_append_without_selecting_event():
    require_postgres()
    result = append_security_event(make_event())
    assert isinstance(result, AppendAuditResult)
    assert result.created is True
    with runtime_connection() as runtime, runtime.cursor() as cursor, pytest.raises(
        InsufficientPrivilege
    ):
        cursor.execute("SELECT event_id FROM audit.identity_security_event")


@pytest.mark.django_db(transaction=True)
def test_idempotency_returns_original_event_without_duplicate():
    require_postgres()
    event = make_event(idempotency_key="audit-idempotency-1")
    first = append_security_event(event)
    second = append_security_event(event)
    assert first == AppendAuditResult(event_id=event.event_id, created=True)
    assert second == AppendAuditResult(event_id=event.event_id, created=False)


@pytest.mark.django_db(transaction=True)
def test_runtime_cannot_mutate_or_truncate_audit_table():
    require_postgres()
    event = make_event()
    append_security_event(event)
    for statement in (
        "UPDATE audit.identity_security_event SET reason_code = 'changed'",
        "DELETE FROM audit.identity_security_event",
        "TRUNCATE audit.identity_security_event",
    ):
        with (
            runtime_connection() as runtime,
            runtime.cursor() as cursor,
            pytest.raises((InsufficientPrivilege, RaiseException)),
        ):
            cursor.execute(statement)


@pytest.mark.django_db(transaction=True)
def test_invalid_event_type_is_rejected_by_database():
    require_postgres()
    with connection.cursor() as cursor, pytest.raises(CheckViolation):
        cursor.execute(
            """
            INSERT INTO audit.identity_security_event
              (event_id, event_type, outcome, correlation_id)
            VALUES (%s, %s, %s, %s)
            """,
            (str(uuid4()), "unsupported", "success", str(uuid4())),
        )


@pytest.mark.django_db(transaction=True)
def test_migrator_owns_table_and_trigger_rejects_mutation():
    require_postgres()
    migrator_url = os.environ.get("DATABASE_MIGRATOR_TEST_URL")
    if not migrator_url:
        pytest.skip("migrator connection is not configured")
    event = make_event()
    with connect(migrator_url, autocommit=True) as migrator, migrator.cursor() as cursor:
        cursor.execute(
            "SELECT tableowner FROM pg_tables "
            "WHERE schemaname = 'audit' AND tablename = 'identity_security_event'"
        )
        assert cursor.fetchone()[0] == "codesho_migrator"
        cursor.execute(
            """
            INSERT INTO audit.identity_security_event
              (event_id, event_type, outcome, correlation_id)
            VALUES (%s, %s, %s, %s)
            """,
            (
                str(event.event_id),
                event.event_type.value,
                event.outcome.value,
                str(event.correlation_id),
            ),
        )
        with pytest.raises(RaiseException):
            cursor.execute(
                "UPDATE audit.identity_security_event SET reason_code = 'changed' "
                "WHERE event_id = %s",
                (str(event.event_id),),
            )
        with pytest.raises(RaiseException):
            cursor.execute("TRUNCATE audit.identity_security_event")


def require_postgres():
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific security audit contract")


def runtime_connection():
    runtime_url = os.environ.get("DATABASE_RUNTIME_TEST_URL") or os.environ.get("DATABASE_URL")
    if not runtime_url:
        settings = connection.settings_dict
        runtime_url = " ".join(
            f"{key}={value!s}"
            for key, value in {
                "dbname": settings["NAME"],
                "user": settings["USER"],
                "password": settings["PASSWORD"],
                "host": settings["HOST"],
                "port": settings["PORT"],
            }.items()
            if value
        )
    return connect(runtime_url, autocommit=True)
