from django.db import migrations


POSTGRES_PHASE2_RLS_SQL = """
-- Force RLS on all Phase 2 Learning Core tables
ALTER TABLE learning_learningpath ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningpath FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_module ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_module FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_assignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_assignment FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_submission ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_submission FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_feedback FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_progress FORCE ROW LEVEL SECURITY;

-- Tenant isolation policies (Fail-Closed)
CREATE POLICY learning_path_tenant_isolation ON learning_learningpath
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

CREATE POLICY learning_module_tenant_isolation ON learning_module
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

CREATE POLICY learning_assignment_tenant_isolation ON learning_assignment
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

CREATE POLICY learning_submission_tenant_isolation ON learning_submission
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

CREATE POLICY learning_feedback_tenant_isolation ON learning_feedback
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

CREATE POLICY learning_progress_tenant_isolation ON learning_progress
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Restrict dangerous DML from runtime role
REVOKE DELETE, TRUNCATE ON TABLE 
    learning_learningpath,
    learning_module,
    learning_assignment,
    learning_submission,
    learning_feedback,
    learning_progress 
FROM codesho_runtime;
"""

REVERSE_PHASE2_RLS_SQL = """
DROP POLICY IF EXISTS learning_progress_tenant_isolation ON learning_progress;
DROP POLICY IF EXISTS learning_feedback_tenant_isolation ON learning_feedback;
DROP POLICY IF EXISTS learning_submission_tenant_isolation ON learning_submission;
DROP POLICY IF EXISTS learning_assignment_tenant_isolation ON learning_assignment;
DROP POLICY IF EXISTS learning_module_tenant_isolation ON learning_module;
DROP POLICY IF EXISTS learning_path_tenant_isolation ON learning_learningpath;

ALTER TABLE learning_progress NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_feedback NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_feedback DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_submission NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_submission DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_assignment NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_assignment DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_module NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_module DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningpath NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_learningpath DISABLE ROW LEVEL SECURITY;
"""


def enable_phase2_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_PHASE2_RLS_SQL)


def disable_phase2_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_PHASE2_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0004_phase2_learning_core"),
    ]

    operations = [
        migrations.RunPython(
            enable_phase2_postgres_rls,
            reverse_code=disable_phase2_postgres_rls,
        ),
    ]
