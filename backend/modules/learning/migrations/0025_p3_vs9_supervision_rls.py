from django.db import migrations

POSTGRES_SUPERVISION_RLS_SQL = """
-- Force RLS on CohortSupervision
ALTER TABLE learning_cohortsupervision ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_cohortsupervision FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_cohortsupervision_tenant_isolation ON learning_cohortsupervision
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on CohortProgressAggregate
ALTER TABLE learning_cohortprogressaggregate ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_cohortprogressaggregate FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_cohortprogressaggregate_tenant_isolation ON learning_cohortprogressaggregate
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on StudentSupervisionAlert
ALTER TABLE learning_studentsupervisionalert ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentsupervisionalert FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_studentsupervisionalert_tenant_isolation ON learning_studentsupervisionalert
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Composite Foreign Key Constraints for Cohort Isolation
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_cohortsupervision_tenant_cohort') THEN
        ALTER TABLE learning_cohortsupervision
            ADD CONSTRAINT fk_cohortsupervision_tenant_cohort
            FOREIGN KEY (tenant_id, cohort_id)
            REFERENCES learning_cohort (tenant_id, id)
            ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_cohortprogressagg_tenant_cohort') THEN
        ALTER TABLE learning_cohortprogressaggregate
            ADD CONSTRAINT fk_cohortprogressagg_tenant_cohort
            FOREIGN KEY (tenant_id, cohort_id)
            REFERENCES learning_cohort (tenant_id, id)
            ON DELETE CASCADE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_studentsupalert_tenant_cohort') THEN
        ALTER TABLE learning_studentsupervisionalert
            ADD CONSTRAINT fk_studentsupalert_tenant_cohort
            FOREIGN KEY (tenant_id, cohort_id)
            REFERENCES learning_cohort (tenant_id, id)
            ON DELETE CASCADE;
    END IF;
END;
$$;
"""

REVERSE_SUPERVISION_RLS_SQL = """
ALTER TABLE learning_studentsupervisionalert DROP CONSTRAINT IF EXISTS fk_studentsupalert_tenant_cohort;
ALTER TABLE learning_cohortprogressaggregate DROP CONSTRAINT IF EXISTS fk_cohortprogressagg_tenant_cohort;
ALTER TABLE learning_cohortsupervision DROP CONSTRAINT IF EXISTS fk_cohortsupervision_tenant_cohort;

DROP POLICY IF EXISTS learning_studentsupervisionalert_tenant_isolation ON learning_studentsupervisionalert;
ALTER TABLE learning_studentsupervisionalert NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_studentsupervisionalert DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_cohortprogressaggregate_tenant_isolation ON learning_cohortprogressaggregate;
ALTER TABLE learning_cohortprogressaggregate NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_cohortprogressaggregate DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_cohortsupervision_tenant_isolation ON learning_cohortsupervision;
ALTER TABLE learning_cohortsupervision NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_cohortsupervision DISABLE ROW LEVEL SECURITY;
"""


def enable_supervision_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_SUPERVISION_RLS_SQL)


def disable_supervision_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SUPERVISION_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0024_p3_vs9_supervision"),
    ]

    operations = [
        migrations.RunPython(
            enable_supervision_postgres_rls,
            reverse_code=disable_supervision_postgres_rls,
        ),
    ]
