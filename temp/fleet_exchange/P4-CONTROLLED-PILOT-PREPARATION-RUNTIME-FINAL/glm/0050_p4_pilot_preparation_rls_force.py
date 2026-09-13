# Generated for Phase 4 Controlled Pilot Preparation: PostgreSQL 17 FORCE RLS & Immutability

from django.db import migrations

POSTGRES_P4_RLS_SQL = r"""
-- =============================================================================
-- Phase 4: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces fail-closed tenant-isolation policies on Phase 4 models
-- =============================================================================

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_release_candidate',
        'learning_incident_record',
        'learning_pilot_tenant_provisioning_plan'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS p4_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY p4_tenant_isolation_policy ON %I ' ||
            'FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) ' ||
            'WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Enforce append-only immutability on incident records and release candidates
REVOKE DELETE ON learning_incident_record FROM PUBLIC;
REVOKE DELETE ON learning_release_candidate FROM PUBLIC;
REVOKE DELETE ON learning_pilot_tenant_provisioning_plan FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_app') THEN
        REVOKE DELETE ON learning_incident_record FROM codesho_app;
        REVOKE DELETE ON learning_release_candidate FROM codesho_app;
        REVOKE DELETE ON learning_pilot_tenant_provisioning_plan FROM codesho_app;
    END IF;
END $$;
"""

REVERSE_POSTGRES_P4_RLS_SQL = r"""
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_release_candidate',
        'learning_incident_record',
        'learning_pilot_tenant_provisioning_plan'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('DROP POLICY IF EXISTS p4_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format('ALTER TABLE %I NO FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY;', tbl);
    END LOOP;
END $$;
"""


def enable_p4_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_P4_RLS_SQL)


def disable_p4_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_POSTGRES_P4_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0049_incidentrecord_pilottenantprovisioningplan_and_more"),
    ]

    operations = [
        migrations.RunPython(
            enable_p4_postgres_rls,
            reverse_code=disable_p4_postgres_rls,
        ),
    ]
