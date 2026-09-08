from django.db import migrations

POSTGRES_ASSESSMENTS_RLS_SQL = """
-- Force RLS on CodeAssessment
ALTER TABLE learning_codeassessment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_codeassessment FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_codeassessment_tenant_isolation ON learning_codeassessment
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on CodeExecutionRun
ALTER TABLE learning_codeexecutionrun ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_codeexecutionrun FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_codeexecutionrun_tenant_isolation ON learning_codeexecutionrun
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on AssessmentResult
ALTER TABLE learning_assessmentresult ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_assessmentresult FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_assessmentresult_tenant_isolation ON learning_assessmentresult
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));
"""

REVERSE_ASSESSMENTS_RLS_SQL = """
DROP POLICY IF EXISTS learning_assessmentresult_tenant_isolation ON learning_assessmentresult;
ALTER TABLE learning_assessmentresult NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_assessmentresult DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_codeexecutionrun_tenant_isolation ON learning_codeexecutionrun;
ALTER TABLE learning_codeexecutionrun NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_codeexecutionrun DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_codeassessment_tenant_isolation ON learning_codeassessment;
ALTER TABLE learning_codeassessment NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_codeassessment DISABLE ROW LEVEL SECURITY;
"""


def enable_assessments_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_ASSESSMENTS_RLS_SQL)


def disable_assessments_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_ASSESSMENTS_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0020_p3_vs7_assessments"),
    ]

    operations = [
        migrations.RunPython(
            enable_assessments_postgres_rls,
            reverse_code=disable_assessments_postgres_rls,
        ),
    ]
