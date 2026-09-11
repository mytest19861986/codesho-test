# Generated for P3-MACRO-EPIC-26-28: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

POSTGRES_EPIC_26_28_RLS_SQL = r"""
-- =============================================================================
-- Phase 3 Macro Epic 26-28: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces fail-closed tenant-isolation policies on all 20 governance tables.
-- Conforms to DDL v1.2-HARDENED and Commander RUNTIME_UNLOCK
-- =============================================================================

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
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
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS p3_epic26_28_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY p3_epic26_28_tenant_isolation_policy ON %I ' ||
            'FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) ' ||
            'WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Enforce append-only immutability on audit and evidence tables
REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_readiness_evidence FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM app_role;
        REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM app_role;
        REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM app_role;
        REVOKE UPDATE, DELETE ON learning_readiness_evidence FROM app_role;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        ALTER ROLE codesho_runtime NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
        REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_readiness_evidence FROM codesho_runtime;
    END IF;
END $$;
"""

REVERSE_SQL = r"""
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
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
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('DROP POLICY IF EXISTS p3_epic26_28_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format('ALTER TABLE %I NO FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY;', tbl);
    END LOOP;
END $$;
"""


def enable_epic_26_28_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_EPIC_26_28_RLS_SQL)


def disable_epic_26_28_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SQL)


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

