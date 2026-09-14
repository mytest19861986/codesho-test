# Generated for P3-MACRO-EPIC-26-28: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

EPIC_26_28_TABLES = [
    'learning_staff_access_assignment',
    'learning_delegated_admin_scope',
    'learning_privileged_permission_grant',
    'learning_access_review_campaign',
    'learning_access_review_decision',
    'learning_privileged_action_audit',
    'learning_data_retention_policy',
    'learning_retention_policy_version',
    'learning_legal_hold',
    'learning_legal_hold_scope',
    'learning_retention_evaluation',
    'learning_data_disposition_record',
    'learning_disposition_audit_log',
    'learning_readiness_control',
    'learning_readiness_evidence',
    'learning_readiness_assessment_run',
    'learning_readiness_finding',
    'learning_readiness_exception',
    'learning_pilot_readiness_gate',
    'learning_control_attestation_audit'
]

def enable_epic_26_28_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for tbl in EPIC_26_28_TABLES:
            cursor.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"DROP POLICY IF EXISTS p3_epic26_28_tenant_isolation_policy ON {tbl};")
            cursor.execute(
                f"CREATE POLICY p3_epic26_28_tenant_isolation_policy ON {tbl} "
                f"FOR ALL USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) "
                f"WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);"
            )

        cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
                BEGIN
                    ALTER ROLE codesho_runtime NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
                EXCEPTION WHEN insufficient_privilege THEN
                    NULL;
                END;
                REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM codesho_runtime;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_app') THEN
                BEGIN
                    ALTER ROLE codesho_app NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
                EXCEPTION WHEN insufficient_privilege THEN
                    NULL;
                END;
                REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM codesho_app;
                REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM codesho_app;
                REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM codesho_app;
            END IF;
        END $$;
        """)

def disable_epic_26_28_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for tbl in EPIC_26_28_TABLES:
            cursor.execute(f"DROP POLICY IF EXISTS p3_epic26_28_tenant_isolation_policy ON {tbl};")
            cursor.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;")

class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0047_p3_macro_epic_26_28_models'),
    ]

    operations = [
        migrations.RunPython(
            enable_epic_26_28_postgres_rls,
            reverse_code=disable_epic_26_28_postgres_rls,
        ),
    ]
