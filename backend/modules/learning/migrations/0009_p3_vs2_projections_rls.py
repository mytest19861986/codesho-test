from django.db import migrations

POSTGRES_PROJECTIONS_RLS_SQL = """
-- Force RLS on CourseProgressAggregate
ALTER TABLE learning_courseprogressaggregate ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_courseprogressaggregate FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_cpa_tenant_isolation ON learning_courseprogressaggregate
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on AssignmentSubmissionMetrics
ALTER TABLE learning_assignmentsubmissionmetrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_assignmentsubmissionmetrics FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_asm_tenant_isolation ON learning_assignmentsubmissionmetrics
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on RoleActivityFeed
ALTER TABLE learning_roleactivityfeed ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_roleactivityfeed FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_raf_tenant_isolation ON learning_roleactivityfeed
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));
"""

REVERSE_PROJECTIONS_RLS_SQL = """
DROP POLICY IF EXISTS learning_raf_tenant_isolation ON learning_roleactivityfeed;
ALTER TABLE learning_roleactivityfeed NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_roleactivityfeed DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_asm_tenant_isolation ON learning_assignmentsubmissionmetrics;
ALTER TABLE learning_assignmentsubmissionmetrics NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_assignmentsubmissionmetrics DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_cpa_tenant_isolation ON learning_courseprogressaggregate;
ALTER TABLE learning_courseprogressaggregate NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_courseprogressaggregate DISABLE ROW LEVEL SECURITY;
"""

def enable_projections_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_PROJECTIONS_RLS_SQL)

def disable_projections_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_PROJECTIONS_RLS_SQL)

class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0008_p3_vs2_projections"),
    ]

    operations = [
        migrations.RunPython(
            enable_projections_postgres_rls,
            reverse_code=disable_projections_postgres_rls,
        ),
    ]
