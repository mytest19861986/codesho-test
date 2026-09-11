# Generated for P3-MACRO-EPIC-23-25: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

POSTGRES_EPIC_23_25_RLS_SQL = r"""
-- =============================================================================
-- Phase 3 Macro Epic 23-25: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces fail-closed tenant-isolation policies on all 19 curriculum authoring,
-- assessment blueprint, rubric governance, and release readiness tables.
-- Conforms to DDL v1.1-CANONICAL-CLAUDE-HARDENED and Commander RUNTIME_UNLOCK
-- =============================================================================

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_curriculumdraftworkspace',
        'learning_contentchangeset',
        'learning_editorialreview',
        'learning_reviewcomment',
        'learning_reviewresolution',
        'learning_authorassignment',
        'learning_changeapprovalrecord',
        'learning_assessmentblueprint',
        'learning_learningobjectivemapping',
        'learning_rubricdefinition',
        'learning_rubriccriterion',
        'learning_assessmentreleasebinding',
        'learning_rubricreviewrecord',
        'learning_curriculumchangeimpact',
        'learning_releasereadinesscheck',
        'learning_releasereadinessgate',
        'learning_cohortrollforwardplan',
        'learning_curriculummigrationdecision',
        'learning_releaseexceptionrecord'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS p3_epic23_25_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY p3_epic23_25_tenant_isolation_policy ON %I ' ||
            'FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) ' ||
            'WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Ensure connection roles operate under strict NOBYPASSRLS and least privilege
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        ALTER ROLE codesho_runtime NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
        REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM codesho_runtime;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        ALTER ROLE app_role NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
        REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM app_role;
    END IF;
END $$;

-- Revoke mutation rights on append-only and immutable audit tables from PUBLIC
REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM PUBLIC;
"""

POSTGRES_EPIC_23_25_RLS_REVERSE_SQL = r"""
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_curriculumdraftworkspace',
        'learning_contentchangeset',
        'learning_editorialreview',
        'learning_reviewcomment',
        'learning_reviewresolution',
        'learning_authorassignment',
        'learning_changeapprovalrecord',
        'learning_assessmentblueprint',
        'learning_learningobjectivemapping',
        'learning_rubricdefinition',
        'learning_rubriccriterion',
        'learning_assessmentreleasebinding',
        'learning_rubricreviewrecord',
        'learning_curriculumchangeimpact',
        'learning_releasereadinesscheck',
        'learning_releasereadinessgate',
        'learning_cohortrollforwardplan',
        'learning_curriculummigrationdecision',
        'learning_releaseexceptionrecord'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('DROP POLICY IF EXISTS p3_epic23_25_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format('ALTER TABLE %I NO FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY;', tbl);
    END LOOP;
END $$;
"""


def enable_epic_23_25_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_EPIC_23_25_RLS_SQL)


def disable_epic_23_25_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_EPIC_23_25_RLS_REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0044_p3_macro_epic_23_25_models'),
    ]

    operations = [
        migrations.RunPython(
            enable_epic_23_25_postgres_rls,
            reverse_code=disable_epic_23_25_postgres_rls,
        ),
    ]
