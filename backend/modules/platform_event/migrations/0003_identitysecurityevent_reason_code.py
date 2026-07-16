from django.db import migrations, models
from django.db.migrations.exceptions import IrreversibleError


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
)


def add_reason_code_constraint(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    values = ", ".join(repr(value) for value in REASON_CODES)
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_reason_code_valid "
        f"CHECK (reason_code IS NULL OR reason_code IN ({values}))"
    )


def reverse_reason_code_constraint(apps, schema_editor):
    raise IrreversibleError("identity security audit evidence must not be altered")


class Migration(migrations.Migration):
    dependencies = [("platform_event", "0002_identitysecurityevent")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    add_reason_code_constraint,
                    reverse_code=reverse_reason_code_constraint,
                )
            ],
            state_operations=[
                migrations.AddConstraint(
                    model_name="identitysecurityevent",
                    constraint=models.CheckConstraint(
                        condition=models.Q(reason_code__isnull=True)
                        | models.Q(reason_code__in=REASON_CODES),
                        name="identity_security_event_reason_code_valid",
                    ),
                )
            ],
        )
    ]
