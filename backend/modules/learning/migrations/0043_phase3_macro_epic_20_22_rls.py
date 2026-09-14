# Generated for P3-MACRO-EPIC-20-22: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

POSTGRES_CURRICULUM_OPERATIONS_RLS_SQL = r"""
-- =============================================================================
-- Phase 3 Macro Epic 20-22: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces tenant-isolation policies on all 15 curriculum & program operations tables
-- Conforms to DDL v1.1-CANONICAL, GLM Gate PASS, and Commander RUNTIME_UNLOCK
-- =============================================================================

DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'learning_curriculumversion',
        'learning_courserelease',
        'learning_modulereleasesnapshot',
        'learning_lessonreleasesnapshot',
        'learning_releaseapprovalrecord',
        'learning_curriculumreleaseauditlog',
        'learning_cohortschedule',
        'learning_learningsession',
        'learning_sessionoccurrence',
        'learning_sessionattendancestate',
        'learning_sessionchangerecord',
        'learning_programdeliveryaggregate',
        'learning_curriculumreleasecoverage',
        'learning_cohortschedulehealth',
        'learning_deliveryexceptionqueue'
    ];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', t);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', t);
        EXECUTE format('DROP POLICY IF EXISTS p3_tenant_isolation_policy ON %I;', t);
        EXECUTE format(
            'CREATE POLICY p3_tenant_isolation_policy ON %I ' ||
            'FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) ' ||
            'WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            t
        );
    END LOOP;
END $$;

-- STRICT APPEND-ONLY DISCIPLINE: REVOKE MUTATION PERMISSIONS
REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_sessionchangerecord FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM app_role;
        REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM app_role;
        REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM app_role;
        REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_sessionchangerecord FROM app_role;
    END IF;
END $$;
"""

POSTGRES_CURRICULUM_OPERATIONS_RLS_REVERSE_SQL = r"""
DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'learning_curriculumversion',
        'learning_courserelease',
        'learning_modulereleasesnapshot',
        'learning_lessonreleasesnapshot',
        'learning_releaseapprovalrecord',
        'learning_curriculumreleaseauditlog',
        'learning_cohortschedule',
        'learning_learningsession',
        'learning_sessionoccurrence',
        'learning_sessionattendancestate',
        'learning_sessionchangerecord',
        'learning_programdeliveryaggregate',
        'learning_curriculumreleasecoverage',
        'learning_cohortschedulehealth',
        'learning_deliveryexceptionqueue'
    ];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        EXECUTE format('DROP POLICY IF EXISTS p3_tenant_isolation_policy ON %I;', t);
        EXECUTE format('ALTER TABLE %I NO FORCE ROW LEVEL SECURITY;', t);
        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY;', t);
    END LOOP;
END $$;
"""


def enable_curriculum_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_CURRICULUM_OPERATIONS_RLS_SQL)


def disable_curriculum_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_CURRICULUM_OPERATIONS_RLS_REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0042_phase3_macro_epic_20_22_models'),
    ]

    operations = [
        migrations.RunPython(
            enable_curriculum_operations_postgres_rls,
            reverse_code=disable_curriculum_operations_postgres_rls,
        ),
    ]
