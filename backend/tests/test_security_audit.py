import os
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.db import DatabaseError, IntegrityError, connection
from psycopg import connect
from psycopg.errors import CheckViolation, InsufficientPrivilege, RaiseException

from modules.platform_event.security_audit import (
    AppendAuditResult,
    ReasonCode,
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
    event = make_event(reason_code=ReasonCode.CREDENTIAL_CREATED)
    assert event.event_type is SecurityEventType.PASSCODE_CREATED
    assert event.outcome is SecurityEventOutcome.SUCCESS
    assert not hasattr(event, "metadata")


@pytest.mark.django_db
def test_audit_failure_does_not_expose_connection_details():
    with patch(
        "modules.platform_event.security_audit.connection.cursor",
        side_effect=DatabaseError("postgresql://username:password@database/audit"),
    ), pytest.raises(SecurityAuditError, match="security audit append failed") as exc_info:
        append_security_event(make_event())
    assert "postgresql" not in str(exc_info.value)
    assert "password" not in str(exc_info.value)


@pytest.mark.django_db
def test_programming_error_is_not_misclassified_as_audit_failure():
    with patch(
        "modules.platform_event.security_audit.connection.cursor",
        side_effect=RuntimeError("programming error"),
    ), pytest.raises(RuntimeError, match="programming error"):
        append_security_event(make_event())


def test_reason_code_requires_an_approved_enum_value():
    with pytest.raises(ValueError, match="approved ReasonCode"):
        append_security_event(make_event(reason_code="raw-secret-not-allowed"))


@pytest.mark.django_db(transaction=True)
def test_runtime_can_append_only_through_the_security_definer_function():
    require_postgres()
    result = append_security_event(make_event())
    assert isinstance(result, AppendAuditResult)
    assert result.created is True
    with runtime_connection() as runtime, runtime.cursor() as cursor, pytest.raises(
        InsufficientPrivilege
    ):
        cursor.execute("SELECT event_id FROM audit.identity_security_event")
    with runtime_connection() as runtime, runtime.cursor() as cursor, pytest.raises(
        InsufficientPrivilege
    ):
        cursor.execute(
            """
            INSERT INTO audit.identity_security_event
              (event_id, event_type, outcome, correlation_id)
            VALUES (%s, %s, %s, %s)
            """,
            (str(uuid4()), "passcode_created", "success", str(uuid4())),
        )


@pytest.mark.django_db(transaction=True)
def test_idempotency_conflict_does_not_claim_the_existing_event_id():
    require_postgres()
    event = make_event(idempotency_key="audit-idempotency-1")
    first = append_security_event(event)
    second = append_security_event(make_event(idempotency_key=event.idempotency_key))
    assert first == AppendAuditResult(event_id=event.event_id, created=True)
    assert second == AppendAuditResult(event_id=None, created=False)


@pytest.mark.django_db(transaction=True)
def test_events_without_idempotency_keys_are_both_inserted():
    require_postgres()
    assert append_security_event(make_event()).created is True
    assert append_security_event(make_event()).created is True


@pytest.mark.django_db(transaction=True)
def test_duplicate_event_id_with_different_idempotency_key_is_safely_wrapped():
    require_postgres()
    event = make_event(idempotency_key="audit-event-id-1")
    assert append_security_event(event).created is True
    with pytest.raises(SecurityAuditError, match="security audit append failed"):
        append_security_event(
            make_event(event_id=event.event_id, idempotency_key="audit-event-id-2")
        )


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
    with connection.cursor() as cursor, pytest.raises((CheckViolation, IntegrityError)):
        cursor.execute(
            """
            INSERT INTO audit.identity_security_event
              (event_id, event_type, outcome, correlation_id)
            VALUES (%s, %s, %s, %s)
            """,
            (str(uuid4()), "unsupported", "success", str(uuid4())),
        )


@pytest.mark.django_db(transaction=True)
def test_invalid_reason_code_is_rejected_by_database():
    require_postgres()
    with connection.cursor() as cursor, pytest.raises((CheckViolation, IntegrityError)):
        cursor.execute(
            """
            INSERT INTO audit.identity_security_event
              (event_id, event_type, outcome, reason_code, correlation_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (str(uuid4()), "passcode_created", "success", "raw-secret", str(uuid4())),
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


@pytest.mark.django_db(transaction=True)
def test_audit_schema_has_no_runtime_default_read_or_mutation_privileges():
    require_postgres()
    migrator_url = os.environ.get("DATABASE_MIGRATOR_TEST_URL")
    if not migrator_url:
        pytest.skip("migrator connection is not configured")
    with connect(migrator_url, autocommit=True) as migrator, migrator.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_default_acl AS default_acl
                JOIN pg_namespace AS namespace
                  ON namespace.oid = default_acl.defaclnamespace
                CROSS JOIN LATERAL aclexplode(default_acl.defaclacl) AS privilege
                JOIN pg_roles AS grantee ON grantee.oid = privilege.grantee
                WHERE namespace.nspname = 'audit'
                  AND default_acl.defaclobjtype = 'r'
                  AND grantee.rolname = 'codesho_runtime'
                  AND privilege.privilege_type IN ('SELECT', 'UPDATE', 'DELETE', 'TRUNCATE')
            )
            """
        )
        assert cursor.fetchone()[0] is False


@pytest.mark.django_db(transaction=True)
def test_append_function_has_only_the_required_runtime_capability():
    require_postgres()
    migrator_url = os.environ.get("DATABASE_MIGRATOR_TEST_URL")
    if not migrator_url:
        pytest.skip("migrator connection is not configured")
    with connect(migrator_url, autocommit=True) as migrator, migrator.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                owner.rolname,
                function.prosecdef,
                COALESCE(array_to_string(function.proconfig, ','), ''),
                has_function_privilege('codesho_runtime', function.oid, 'EXECUTE'),
                EXISTS (
                    SELECT 1
                    FROM aclexplode(COALESCE(function.proacl, acldefault('f', function.proowner)))
                      AS privilege
                    WHERE privilege.grantee = 0
                      AND privilege.privilege_type = 'EXECUTE'
                )
            FROM pg_proc AS function
            JOIN pg_namespace AS namespace ON namespace.oid = function.pronamespace
            JOIN pg_roles AS owner ON owner.oid = function.proowner
            WHERE namespace.nspname = 'audit'
              AND function.proname = 'append_identity_security_event'
            """
        )
        owner, security_definer, config, runtime_execute, public_execute = cursor.fetchone()
    assert owner == "codesho_migrator"
    assert security_definer is True
    assert "search_path=pg_catalog, pg_temp" in config
    assert runtime_execute is True
    assert public_execute is False


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
