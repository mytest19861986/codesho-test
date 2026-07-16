from django.db import migrations, models
from django.db.models.functions import Now
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
)
EVENT_OUTCOMES = ("success", "failure", "blocked", "detected")


CREATE_AUDIT_SQL = f"""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'audit') THEN
        RAISE EXCEPTION 'audit schema must be provisioned before audit migrations run';
    END IF;
END;
$$;
REVOKE ALL ON SCHEMA audit FROM PUBLIC;
CREATE TABLE audit.identity_security_event (
    event_id uuid PRIMARY KEY,
    event_type varchar(64) NOT NULL,
    outcome varchar(16) NOT NULL,
    reason_code varchar(128),
    subject_user_id uuid,
    actor_user_id uuid,
    tenant_id uuid,
    credential_version integer,
    correlation_id uuid NOT NULL,
    idempotency_key varchar(255) UNIQUE,
    occurred_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT identity_security_event_type_valid CHECK (
        event_type IN ({", ".join(repr(value) for value in EVENT_TYPES)})
    ),
    CONSTRAINT identity_security_event_outcome_valid CHECK (
        outcome IN ({", ".join(repr(value) for value in EVENT_OUTCOMES)})
    )
);
ALTER TABLE audit.identity_security_event OWNER TO CURRENT_USER;
REVOKE ALL ON TABLE audit.identity_security_event FROM PUBLIC;
GRANT USAGE ON SCHEMA audit TO codesho_runtime;
GRANT INSERT ON TABLE audit.identity_security_event TO codesho_runtime;
REVOKE SELECT, UPDATE, DELETE, TRUNCATE ON TABLE audit.identity_security_event
FROM codesho_runtime;

CREATE OR REPLACE FUNCTION audit.prevent_identity_security_event_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'identity security events are immutable';
END;
$$;
REVOKE ALL ON FUNCTION audit.prevent_identity_security_event_mutation() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION audit.prevent_identity_security_event_mutation() TO codesho_runtime;

CREATE TRIGGER identity_security_event_no_update_delete
BEFORE UPDATE OR DELETE ON audit.identity_security_event
FOR EACH ROW EXECUTE FUNCTION audit.prevent_identity_security_event_mutation();

CREATE TRIGGER identity_security_event_no_truncate
BEFORE TRUNCATE ON audit.identity_security_event
FOR EACH STATEMENT EXECUTE FUNCTION audit.prevent_identity_security_event_mutation();
"""


def create_audit_migration(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(CREATE_AUDIT_SQL)


def reverse_audit_migration(apps, schema_editor):
    raise IrreversibleError("identity security audit evidence must not be deleted")


class Migration(migrations.Migration):
    dependencies = [("platform_event", "0001_initial")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    create_audit_migration,
                    reverse_code=reverse_audit_migration,
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="IdentitySecurityEvent",
                    fields=[
                        (
                            "event_id",
                            models.UUIDField(editable=False, primary_key=True, serialize=False),
                        ),
                        ("event_type", models.CharField(max_length=64)),
                        ("outcome", models.CharField(max_length=16)),
                        ("reason_code", models.CharField(blank=True, max_length=128, null=True)),
                        ("subject_user_id", models.UUIDField(blank=True, null=True)),
                        ("actor_user_id", models.UUIDField(blank=True, null=True)),
                        ("tenant_id", models.UUIDField(blank=True, null=True)),
                        ("credential_version", models.PositiveIntegerField(blank=True, null=True)),
                        ("correlation_id", models.UUIDField()),
                        (
                            "idempotency_key",
                            models.CharField(blank=True, max_length=255, null=True, unique=True),
                        ),
                        ("occurred_at", models.DateTimeField(db_default=Now(), editable=False)),
                    ],
                    options={"db_table": "audit.identity_security_event"},
                ),
                migrations.AddConstraint(
                    model_name="identitysecurityevent",
                    constraint=models.CheckConstraint(
                        condition=models.Q(event_type__in=EVENT_TYPES),
                        name="identity_security_event_type_valid",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="identitysecurityevent",
                    constraint=models.CheckConstraint(
                        condition=models.Q(outcome__in=EVENT_OUTCOMES),
                        name="identity_security_event_outcome_valid",
                    ),
                ),
            ],
        )
    ]
