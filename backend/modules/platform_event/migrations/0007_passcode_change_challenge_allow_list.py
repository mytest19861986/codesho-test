from django.db import migrations
from django.db.migrations.exceptions import IrreversibleError

PREVIOUS_EVENT_TYPES = (
    "passcode_created",
    "passcode_changed",
    "passcode_verification_failed",
    "account_locked",
    "account_unlocked",
    "abuse_global_alert",
    "temporary_passcode_issued",
    "temporary_passcode_consumed",
    "guardian_reset_started",
    "guardian_reset_completed",
    "authentication_succeeded",
    "authentication_failed",
    "authentication_blocked",
    "session_logged_out",
)
PREVIOUS_REASON_CODES = (
    "credential_created",
    "credential_changed",
    "verification_mismatch",
    "lock_threshold_reached",
    "lock_cleared",
    "abuse_threshold_reached",
    "temporary_credential_issued",
    "temporary_credential_consumed",
    "guardian_reset_requested",
    "guardian_reset_confirmed",
    "login_succeeded",
    "login_failed",
    "login_blocked",
    "session_logged_out",
    "passcode_change_required",
)
EVENT_TYPES = (
    *PREVIOUS_EVENT_TYPES,
    "passcode_change_challenge_issued",
    "passcode_change_challenge_revoked",
    "passcode_change_challenge_consumed",
    "passcode_change_challenge_expired",
    "passcode_change_rejected",
)
REASON_CODES = (
    *PREVIOUS_REASON_CODES,
    "challenge_issued",
    "challenge_superseded",
    "challenge_consumed",
    "challenge_expired",
    "challenge_invalid",
    "passcode_same_as_current",
    "challenge_revoked_pepper_rotation",
)


def _values(values):
    return ", ".join(repr(value) for value in values)


def _expected_constraint(cursor, column, nullable):
    table_name = f"codesho_expected_{column}"
    constraint_name = f"expected_{column}_valid"
    previous_values = (
        PREVIOUS_REASON_CODES if column == "reason_code" else PREVIOUS_EVENT_TYPES
    )
    condition = f"{column} IS NULL OR {column} IN" if nullable else f"{column} IN"
    cursor.execute(
        f"CREATE TEMPORARY TABLE {table_name} ({column} varchar(128), "
        f"CONSTRAINT {constraint_name} CHECK ({condition} ({_values(previous_values)}))) "
        "ON COMMIT DROP"
    )
    cursor.execute(
        "SELECT pg_get_constraintdef(audit_constraint.oid) "
        "FROM pg_constraint AS audit_constraint "
        "WHERE audit_constraint.conrelid = %s::regclass "
        "AND audit_constraint.conname = %s",
        [table_name, constraint_name],
    )
    return cursor.fetchone()


def _current_constraint(cursor, constraint_name):
    cursor.execute(
        "SELECT pg_get_constraintdef(audit_constraint.oid), "
        "audit_constraint.convalidated "
        "FROM pg_constraint AS audit_constraint "
        "JOIN pg_class AS relation ON relation.oid = audit_constraint.conrelid "
        "JOIN pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "WHERE namespace.nspname = 'audit' "
        "AND relation.relname = 'identity_security_event' "
        "AND audit_constraint.conname = %s",
        [constraint_name],
    )
    return cursor.fetchone()


def extend_passcode_change_allow_lists(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        for column, constraint_name, nullable in (
            ("event_type", "identity_security_event_type_valid", False),
            ("reason_code", "identity_security_event_reason_code_valid", True),
        ):
            expected = _expected_constraint(cursor, column, nullable)
            current = _current_constraint(cursor, constraint_name)
            if expected is None or current is None or current[1] is not True:
                raise RuntimeError(f"audit {column} constraint is missing or unvalidated")
            if current[0] != expected[0]:
                raise RuntimeError(
                    f"audit {column} constraint does not match the expected allow-list"
                )

    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "DROP CONSTRAINT identity_security_event_type_valid"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_type_valid "
        f"CHECK (event_type IN ({_values(EVENT_TYPES)}))"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "DROP CONSTRAINT identity_security_event_reason_code_valid"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_reason_code_valid "
        f"CHECK (reason_code IS NULL OR reason_code IN ({_values(REASON_CODES)}))"
    )


def irreversible(apps, schema_editor):
    raise IrreversibleError("immutable audit evidence allow-lists must move forward")


class Migration(migrations.Migration):
    atomic = True
    dependencies = [("platform_event", "0006_passcode_change_required_reason")]
    operations = [
        migrations.RunPython(
            extend_passcode_change_allow_lists,
            reverse_code=irreversible,
        )
    ]
