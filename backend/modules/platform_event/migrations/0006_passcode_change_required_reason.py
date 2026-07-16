from django.db import migrations, models
from django.db.migrations.exceptions import IrreversibleError

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
)
REASON_CODES = (*PREVIOUS_REASON_CODES, "passcode_change_required")


def add_reason_code(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        # SQLite is test-only; production and the required Compose gate use PostgreSQL.
        return
    with schema_editor.connection.cursor() as cursor:
        expected_values = ", ".join(repr(value) for value in PREVIOUS_REASON_CODES)
        cursor.execute(
            "CREATE TEMPORARY TABLE codesho_expected_audit_reason_constraint "
            "(reason_code varchar(128), CONSTRAINT expected_reason_code_valid "
            f"CHECK (reason_code IS NULL OR reason_code IN ({expected_values}))) "
            "ON COMMIT DROP"
        )
        cursor.execute(
            """
            SELECT pg_get_constraintdef(constraint.oid)
            FROM pg_constraint AS constraint
            WHERE constraint.conrelid = 'codesho_expected_audit_reason_constraint'::regclass
              AND constraint.conname = 'expected_reason_code_valid'
            """
        )
        expected_row = cursor.fetchone()
        cursor.execute(
            """
            SELECT pg_get_constraintdef(constraint.oid), constraint.convalidated
            FROM pg_constraint AS constraint
            JOIN pg_class AS relation ON relation.oid = constraint.conrelid
            JOIN pg_namespace AS namespace ON namespace.oid = relation.relnamespace
            WHERE namespace.nspname = 'audit'
              AND relation.relname = 'identity_security_event'
              AND constraint.conname = 'identity_security_event_reason_code_valid'
            """
        )
        row = cursor.fetchone()
    if expected_row is None or row is None or row[1] is not True:
        raise RuntimeError("audit reason-code constraint is missing or unvalidated")
    if row[0] != expected_row[0]:
        raise RuntimeError("audit reason-code constraint does not match the expected allow-list")
    values = ", ".join(repr(value) for value in REASON_CODES)
    # atomic=True plus PostgreSQL transactional DDL prevents a committed gap.
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "DROP CONSTRAINT identity_security_event_reason_code_valid"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_reason_code_valid "
        f"CHECK (reason_code IS NULL OR reason_code IN ({values}))"
    )


def irreversible(apps, schema_editor):
    raise IrreversibleError("immutable audit evidence allow-lists must move forward")


class Migration(migrations.Migration):
    atomic = True
    dependencies = [("platform_event", "0005_authentication_security_events")]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(add_reason_code, reverse_code=irreversible)],
            state_operations=[
                migrations.RemoveConstraint(
                    "identitysecurityevent", "identity_security_event_reason_code_valid"
                ),
                migrations.AddConstraint(
                    "identitysecurityevent",
                    models.CheckConstraint(
                        condition=models.Q(reason_code__isnull=True)
                        | models.Q(reason_code__in=REASON_CODES),
                        name="identity_security_event_reason_code_valid",
                    ),
                ),
            ],
        )
    ]
