from django.db import migrations
from django.db.migrations.exceptions import IrreversibleError

REPLACE_APPEND_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION audit.append_identity_security_event(
    p_event_id uuid,
    p_event_type varchar,
    p_outcome varchar,
    p_reason_code varchar,
    p_subject_user_id uuid,
    p_actor_user_id uuid,
    p_tenant_id uuid,
    p_credential_version integer,
    p_correlation_id uuid,
    p_idempotency_key varchar
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, pg_temp
AS $$
DECLARE
    inserted boolean := false;
BEGIN
    INSERT INTO audit.identity_security_event (
        event_id, event_type, outcome, reason_code,
        subject_user_id, actor_user_id, tenant_id,
        credential_version, correlation_id, idempotency_key
    ) VALUES (
        p_event_id, p_event_type, p_outcome, p_reason_code,
        p_subject_user_id, p_actor_user_id, p_tenant_id,
        p_credential_version, p_correlation_id, p_idempotency_key
    )
    ON CONFLICT (idempotency_key) DO NOTHING
    RETURNING true INTO inserted;

    RETURN inserted;
END;
$$;
"""


def replace_append_function(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REPLACE_APPEND_FUNCTION_SQL)


def irreversible(apps, schema_editor):
    raise IrreversibleError("identity security audit append capability must not be removed")


class Migration(migrations.Migration):
    dependencies = [("platform_event", "0007_passcode_change_challenge_allow_list")]

    operations = [
        migrations.RunPython(replace_append_function, reverse_code=irreversible),
    ]
