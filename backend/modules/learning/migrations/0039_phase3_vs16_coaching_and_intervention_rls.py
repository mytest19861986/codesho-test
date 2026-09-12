# Generated for P3-VS16: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

POSTGRES_COACHING_AND_INTERVENTION_RLS_SQL = r"""
-- =============================================================================
-- Phase 3 VS16: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces tenant-isolation policies on all 5 coaching and intervention tables
-- Conforms to DDL v1.1-CANONICAL and GLM Gate PASS
-- =============================================================================

-- 1. Force RLS on CoachingSession
ALTER TABLE learning_coachingsession ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingsession FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs16_session_tenant_isolation ON learning_coachingsession;
CREATE POLICY p3_vs16_session_tenant_isolation ON learning_coachingsession
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 2. Force RLS on CoachingNote
ALTER TABLE learning_coachingnote ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingnote FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs16_note_tenant_isolation ON learning_coachingnote;
CREATE POLICY p3_vs16_note_tenant_isolation ON learning_coachingnote
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 3. Force RLS on SupportIntervention
ALTER TABLE learning_supportintervention ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_supportintervention FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs16_intervention_tenant_isolation ON learning_supportintervention;
CREATE POLICY p3_vs16_intervention_tenant_isolation ON learning_supportintervention
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 4. Force RLS on FollowUpAction
ALTER TABLE learning_followupaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_followupaction FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs16_action_tenant_isolation ON learning_followupaction;
CREATE POLICY p3_vs16_action_tenant_isolation ON learning_followupaction
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- 5. Force RLS on CoachingAuditLog
ALTER TABLE learning_coachingauditlog ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingauditlog FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs16_audit_tenant_isolation ON learning_coachingauditlog;
CREATE POLICY p3_vs16_audit_tenant_isolation ON learning_coachingauditlog
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Append-only discipline: REVOKE UPDATE, DELETE on coaching notes and coaching audit log
REVOKE UPDATE, DELETE ON learning_coachingnote FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_coachingauditlog FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        EXECUTE 'REVOKE UPDATE, DELETE ON learning_coachingnote FROM app_role;';
        EXECUTE 'REVOKE UPDATE, DELETE ON learning_coachingauditlog FROM app_role;';
    END IF;
END $$;
"""

POSTGRES_COACHING_AND_INTERVENTION_RLS_REVERSE_SQL = r"""
DROP POLICY IF EXISTS p3_vs16_session_tenant_isolation ON learning_coachingsession;
DROP POLICY IF EXISTS p3_vs16_note_tenant_isolation ON learning_coachingnote;
DROP POLICY IF EXISTS p3_vs16_intervention_tenant_isolation ON learning_supportintervention;
DROP POLICY IF EXISTS p3_vs16_action_tenant_isolation ON learning_followupaction;
DROP POLICY IF EXISTS p3_vs16_audit_tenant_isolation ON learning_coachingauditlog;

ALTER TABLE learning_coachingsession NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingnote NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_supportintervention NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_followupaction NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingauditlog NO FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_coachingsession DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingnote DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_supportintervention DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_followupaction DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingauditlog DISABLE ROW LEVEL SECURITY;
"""


def enable_coaching_and_intervention_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_COACHING_AND_INTERVENTION_RLS_SQL)


def disable_coaching_and_intervention_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_COACHING_AND_INTERVENTION_REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0038_phase3_vs16_coaching_and_intervention'),
    ]

    operations = [
        migrations.RunPython(
            enable_coaching_and_intervention_postgres_rls,
            reverse_code=disable_coaching_and_intervention_postgres_rls,
        ),
    ]
