from django.db import migrations, models
from django.db.migrations.exceptions import IrreversibleError

EVENT_TYPES = (
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
REASON_CODES = (
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


def extend_authentication_allow_lists(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    event_values = ", ".join(repr(value) for value in EVENT_TYPES)
    reason_values = ", ".join(repr(value) for value in REASON_CODES)
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "DROP CONSTRAINT identity_security_event_type_valid"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_type_valid "
        f"CHECK (event_type IN ({event_values}))"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "DROP CONSTRAINT identity_security_event_reason_code_valid"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_reason_code_valid "
        f"CHECK (reason_code IS NULL OR reason_code IN ({reason_values}))"
    )


def irreversible(apps, schema_editor):
    raise IrreversibleError("immutable audit evidence allow-lists must move forward")


class Migration(migrations.Migration):
    # Keep DROP/ADD pairs in one transaction; PostgreSQL's ACCESS EXCLUSIVE
    # lock then covers the entire allow-list replacement.
    atomic = True
    dependencies = [("platform_event", "0004_identitysecurityevent_append_function")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    extend_authentication_allow_lists,
                    reverse_code=irreversible,
                )
            ],
            state_operations=[
                migrations.RemoveConstraint(
                    "identitysecurityevent", "identity_security_event_type_valid"
                ),
                migrations.RemoveConstraint(
                    "identitysecurityevent", "identity_security_event_reason_code_valid"
                ),
                migrations.AddConstraint(
                    "identitysecurityevent",
                    models.CheckConstraint(
                        condition=models.Q(event_type__in=EVENT_TYPES),
                        name="identity_security_event_type_valid",
                    ),
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
