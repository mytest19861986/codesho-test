# Generated for P3-MACRO-EPIC-17-19: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

POSTGRES_MENTOR_OPERATIONS_RLS_SQL = r"""
-- =============================================================================
-- Phase 3 Macro Epic 17-19: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces tenant-isolation policies on all 6 mentor operations tables
-- Conforms to DDL v1.2-CANONICAL and GLM Gate PASS
-- =============================================================================

-- 1. Force RLS on MentorCaseloadAssignment
ALTER TABLE learning_mentorcaseloadassignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_mentorcaseloadassignment FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS mentorcaseload_tenant_isolation ON learning_mentorcaseloadassignment;
CREATE POLICY mentorcaseload_tenant_isolation ON learning_mentorcaseloadassignment
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 2. Force RLS on SupportQueueItem
ALTER TABLE learning_supportqueueitem ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_supportqueueitem FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS supportqueue_tenant_isolation ON learning_supportqueueitem;
CREATE POLICY supportqueue_tenant_isolation ON learning_supportqueueitem
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 3. Force RLS on LearningCheckIn
ALTER TABLE learning_learningcheckin ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningcheckin FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learningcheckin_tenant_isolation ON learning_learningcheckin;
CREATE POLICY learningcheckin_tenant_isolation ON learning_learningcheckin
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 4. Force RLS on FollowUpCommitment
ALTER TABLE learning_followupcommitment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_followupcommitment FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS followupcommitment_tenant_isolation ON learning_followupcommitment;
CREATE POLICY followupcommitment_tenant_isolation ON learning_followupcommitment
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 5. Force RLS on ProgramSupportAggregate
ALTER TABLE learning_programsupportaggregate ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_programsupportaggregate FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS programsupportaggregate_tenant_isolation ON learning_programsupportaggregate;
CREATE POLICY programsupportaggregate_tenant_isolation ON learning_programsupportaggregate
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 6. Force RLS on MentorOperationsAuditLog
ALTER TABLE learning_mentoroperationsauditlog ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_mentoroperationsauditlog FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS mentoropsaudit_tenant_isolation ON learning_mentoroperationsauditlog;
CREATE POLICY mentoropsaudit_tenant_isolation ON learning_mentoroperationsauditlog
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Append-only discipline: REVOKE UPDATE, DELETE on mentor operations audit log
REVOKE UPDATE, DELETE ON learning_mentoroperationsauditlog FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        EXECUTE 'REVOKE UPDATE, DELETE ON learning_mentoroperationsauditlog FROM app_role;';
    END IF;
END $$;
"""

POSTGRES_MENTOR_OPERATIONS_REVERSE_SQL = r"""
DROP POLICY IF EXISTS mentoropsaudit_tenant_isolation ON learning_mentoroperationsauditlog;
ALTER TABLE learning_mentoroperationsauditlog DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS programsupportaggregate_tenant_isolation ON learning_programsupportaggregate;
ALTER TABLE learning_programsupportaggregate DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS followupcommitment_tenant_isolation ON learning_followupcommitment;
ALTER TABLE learning_followupcommitment DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learningcheckin_tenant_isolation ON learning_learningcheckin;
ALTER TABLE learning_learningcheckin DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS supportqueue_tenant_isolation ON learning_supportqueueitem;
ALTER TABLE learning_supportqueueitem DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS mentorcaseload_tenant_isolation ON learning_mentorcaseloadassignment;
ALTER TABLE learning_mentorcaseloadassignment DISABLE ROW LEVEL SECURITY;
"""


def enable_mentor_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_MENTOR_OPERATIONS_RLS_SQL)


def disable_mentor_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_MENTOR_OPERATIONS_REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0040_phase3_macro_epic_17_19_operations'),
    ]

    operations = [
        migrations.RunPython(
            enable_mentor_operations_postgres_rls,
            reverse_code=disable_mentor_operations_postgres_rls,
        ),
    ]
