from django.db import migrations

CREATE_CLEANUP_FUNCTION_SQL = """
CREATE FUNCTION codesho.delete_expired_passcode_change_challenges(
    p_tenant_id uuid,
    p_cutoff timestamptz,
    p_batch_size integer
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, codesho, pg_temp
AS $$
DECLARE
    deleted_count integer;
BEGIN
    -- tenant_atomic uses SET LOCAL; IS DISTINCT FROM deliberately fails closed
    -- when the transaction-scoped app.tenant_id GUC is absent or stale.
    IF p_tenant_id IS NULL OR p_cutoff IS NULL OR p_batch_size NOT BETWEEN 1 AND 500
       OR current_setting('app.tenant_id', true) IS DISTINCT FROM p_tenant_id::text THEN
        RAISE EXCEPTION 'tenant context is required';
    END IF;

    WITH candidates AS (
        SELECT id
        FROM codesho.identity_passcodechangechallenge
        WHERE tenant_id = p_tenant_id
          AND state IN ('consumed', 'revoked', 'expired')
          AND COALESCE(consumed_at, revoked_at, expired_at) <= p_cutoff
        ORDER BY COALESCE(consumed_at, revoked_at, expired_at), id
        FOR UPDATE SKIP LOCKED
        LIMIT p_batch_size
    )
    DELETE FROM codesho.identity_passcodechangechallenge AS challenge
    USING candidates
    WHERE challenge.id = candidates.id;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

ALTER FUNCTION codesho.delete_expired_passcode_change_challenges(uuid, timestamptz, integer)
    OWNER TO codesho_migrator;
REVOKE ALL ON FUNCTION
    codesho.delete_expired_passcode_change_challenges(uuid, timestamptz, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION
    codesho.delete_expired_passcode_change_challenges(uuid, timestamptz, integer)
    TO codesho_runtime;
"""

DROP_CLEANUP_FUNCTION_SQL = """
DROP FUNCTION IF EXISTS
    codesho.delete_expired_passcode_change_challenges(uuid, timestamptz, integer);
"""


def create_cleanup_function(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(CREATE_CLEANUP_FUNCTION_SQL)


def drop_cleanup_function(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(DROP_CLEANUP_FUNCTION_SQL)


class Migration(migrations.Migration):
    dependencies = [
        ("identity", "0005_challenge_runtime_column_grants"),
        ("platform_event", "0007_passcode_change_challenge_allow_list"),
    ]

    operations = [migrations.RunPython(create_cleanup_function, reverse_code=drop_cleanup_function)]
