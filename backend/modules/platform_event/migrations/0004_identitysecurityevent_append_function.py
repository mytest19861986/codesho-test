from django.db import migrations
from django.db.migrations.exceptions import IrreversibleError


CREATE_APPEND_FUNCTION_SQL = """
CREATE FUNCTION audit.append_identity_security_event(
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
    ON CONFLICT (idempotency_key) DO NOTHING;

    RETURN FOUND;
END;
$$;
ALTER FUNCTION audit.append_identity_security_event(
    uuid, varchar, varchar, varchar, uuid, uuid, uuid, integer, uuid, varchar
) OWNER TO CURRENT_USER;
REVOKE ALL ON FUNCTION audit.append_identity_security_event(
    uuid, varchar, varchar, varchar, uuid, uuid, uuid, integer, uuid, varchar
) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION audit.append_identity_security_event(
    uuid, varchar, varchar, varchar, uuid, uuid, uuid, integer, uuid, varchar
) TO codesho_runtime;
REVOKE INSERT ON TABLE audit.identity_security_event FROM codesho_runtime;
"""


def create_append_function(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(CREATE_APPEND_FUNCTION_SQL)


def reverse_append_function(apps, schema_editor):
    raise IrreversibleError("identity security audit append capability must not be removed")


class Migration(migrations.Migration):
    dependencies = [("platform_event", "0003_identitysecurityevent_reason_code")]

    operations = [
        migrations.RunPython(
            create_append_function,
            reverse_code=reverse_append_function,
        )
    ]
