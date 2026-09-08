from django.db import migrations

POSTGRES_ENROLLMENT_RLS_SQL = """
-- Force RLS on Cohort
ALTER TABLE learning_cohort ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_cohort FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_cohort_tenant_isolation ON learning_cohort
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on CourseEnrollment
ALTER TABLE learning_courseenrollment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_courseenrollment FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_courseenrollment_tenant_isolation ON learning_courseenrollment
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on CoursePrerequisite
ALTER TABLE learning_courseprerequisite ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_courseprerequisite FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_courseprerequisite_tenant_isolation ON learning_courseprerequisite
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));
"""

REVERSE_ENROLLMENT_RLS_SQL = """
DROP POLICY IF EXISTS learning_courseprerequisite_tenant_isolation ON learning_courseprerequisite;
ALTER TABLE learning_courseprerequisite NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_courseprerequisite DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_courseenrollment_tenant_isolation ON learning_courseenrollment;
ALTER TABLE learning_courseenrollment NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_courseenrollment DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_cohort_tenant_isolation ON learning_cohort;
ALTER TABLE learning_cohort NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_cohort DISABLE ROW LEVEL SECURITY;
"""


def enable_enrollment_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_ENROLLMENT_RLS_SQL)


def disable_enrollment_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_ENROLLMENT_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0016_p3_vs5_enrollment"),
    ]

    operations = [
        migrations.RunPython(
            enable_enrollment_postgres_rls,
            reverse_code=disable_enrollment_postgres_rls,
        ),
    ]
