# Generated for P3-VS15: PostgreSQL 17 FORCE RLS & NOBYPASSRLS for Learning Continuity & Student Success Planning

from django.db import migrations

POSTGRES_LEARNING_SUCCESS_PLANNING_RLS_SQL = r"""
-- =============================================================================
-- Phase 3 VS15: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces tenant-isolation policies on all 4 success planning tables
-- Conforms to DDL v1.2-CANONICAL and GLM Gate PASS
-- =============================================================================

-- Force RLS on LearningStudentSuccessPlan
ALTER TABLE learning_studentsuccessplan ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentsuccessplan FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs15_successplan_tenant_isolation ON learning_studentsuccessplan;
CREATE POLICY p3_vs15_successplan_tenant_isolation ON learning_studentsuccessplan
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on SuccessActionStep
ALTER TABLE learning_successactionstep ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_successactionstep FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs15_actionstep_tenant_isolation ON learning_successactionstep;
CREATE POLICY p3_vs15_actionstep_tenant_isolation ON learning_successactionstep
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on SuccessTimelineEvent
ALTER TABLE learning_successtimelineevent ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_successtimelineevent FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs15_timeline_tenant_isolation ON learning_successtimelineevent;
CREATE POLICY p3_vs15_timeline_tenant_isolation ON learning_successtimelineevent
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on SuccessAuditLog
ALTER TABLE learning_successauditlog ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_successauditlog FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs15_audit_tenant_isolation ON learning_successauditlog;
CREATE POLICY p3_vs15_audit_tenant_isolation ON learning_successauditlog
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Append-only discipline: REVOKE UPDATE, DELETE on timeline events and audit log
REVOKE UPDATE, DELETE ON learning_successtimelineevent FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_successauditlog FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        EXECUTE 'REVOKE UPDATE, DELETE ON learning_successtimelineevent FROM app_role;';
        EXECUTE 'REVOKE UPDATE, DELETE ON learning_successauditlog FROM app_role;';
    END IF;
END $$;

-- =============================================================================
-- Composite Foreign Keys, Deferrable FK Topology & Check Constraints
-- =============================================================================
DO $$
BEGIN
    -- Composite FK: LearningStudentSuccessPlan -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_studentsuccessplan_student') THEN
        ALTER TABLE learning_studentsuccessplan
            ADD CONSTRAINT fk_studentsuccessplan_student
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: SuccessActionStep -> LearningStudentSuccessPlan
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_successactionstep_plan') THEN
        ALTER TABLE learning_successactionstep
            ADD CONSTRAINT fk_successactionstep_plan
            FOREIGN KEY (tenant_id, plan_id)
            REFERENCES learning_studentsuccessplan (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- SuccessTimelineEvent: Deferrable FK to LearningStudentSuccessPlan
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_plan') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_plan
            FOREIGN KEY (tenant_id, plan_id)
            REFERENCES learning_studentsuccessplan (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    -- SuccessTimelineEvent: Actor FK to Tenant Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_actor') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_actor
            FOREIGN KEY (tenant_id, actor_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE RESTRICT;
    END IF;

    -- SuccessTimelineEvent: Deferrable FKs to targets (Goal, Insight, Reflection, Action, Milestone, Replaces)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_target_goal') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_target_goal
            FOREIGN KEY (tenant_id, target_goal_id)
            REFERENCES learning_studentlearninggoal (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_target_insight') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_target_insight
            FOREIGN KEY (tenant_id, target_insight_id)
            REFERENCES learning_learninginsight (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_target_reflection') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_target_reflection
            FOREIGN KEY (tenant_id, target_reflection_id)
            REFERENCES learning_learningreflection (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_target_action') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_target_action
            FOREIGN KEY (tenant_id, target_action_step_id)
            REFERENCES learning_successactionstep (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_target_milestone') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_target_milestone
            FOREIGN KEY (tenant_id, target_milestone_id)
            REFERENCES learning_learningmilestone (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_timelineevent_replaces') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT fk_timelineevent_replaces
            FOREIGN KEY (tenant_id, replaces_event_id)
            REFERENCES learning_successtimelineevent (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    -- 5-way XOR Continuity Check Constraint
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_timeline_target_xor') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT chk_timeline_target_xor
            CHECK (num_nonnulls(target_goal_id, target_insight_id, target_reflection_id, target_action_step_id, target_milestone_id) = 1);
    END IF;

    -- 1-to-1 Type-Target Coupling Check Constraint
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_timeline_type_target_coupling') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT chk_timeline_type_target_coupling
            CHECK (
                (event_type = 'GOAL_ANCHORED' AND target_goal_id IS NOT NULL) OR
                (event_type = 'INSIGHT_CONNECTED' AND target_insight_id IS NOT NULL) OR
                (event_type = 'REFLECTION_TIED' AND target_reflection_id IS NOT NULL) OR
                (event_type = 'ACTION_DISPATCHED' AND target_action_step_id IS NOT NULL) OR
                (event_type = 'MILESTONE_PROGRESSION' AND target_milestone_id IS NOT NULL) OR
                (event_type = 'TIMELINE_EVENT_AMENDED' AND replaces_event_id IS NOT NULL)
            );
    END IF;

    -- SuccessAuditLog: Actor FK and Deferrable Target FKs
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_successaudit_actor') THEN
        ALTER TABLE learning_successauditlog
            ADD CONSTRAINT fk_successaudit_actor
            FOREIGN KEY (tenant_id, actor_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE RESTRICT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_successaudit_target_plan') THEN
        ALTER TABLE learning_successauditlog
            ADD CONSTRAINT fk_successaudit_target_plan
            FOREIGN KEY (tenant_id, target_plan_id)
            REFERENCES learning_studentsuccessplan (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_successaudit_target_action') THEN
        ALTER TABLE learning_successauditlog
            ADD CONSTRAINT fk_successaudit_target_action
            FOREIGN KEY (tenant_id, target_action_step_id)
            REFERENCES learning_successactionstep (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_successaudit_target_timeline') THEN
        ALTER TABLE learning_successauditlog
            ADD CONSTRAINT fk_successaudit_target_timeline
            FOREIGN KEY (tenant_id, target_timeline_event_id)
            REFERENCES learning_successtimelineevent (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    -- Audit Target XOR Check Constraint
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_successaudit_target_xor') THEN
        ALTER TABLE learning_successauditlog
            ADD CONSTRAINT chk_successaudit_target_xor
            CHECK (num_nonnulls(target_plan_id, target_action_step_id, target_timeline_event_id) = 1);
    END IF;

    -- 13-key PII Exclusion Union Array Blacklist on JSONB metadata
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_timeline_metadata_no_pii') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT chk_timeline_metadata_no_pii
            CHECK (
                jsonb_typeof(metadata) = 'object'
                AND NOT (metadata ?| ARRAY[
                    'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
                    'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
                ])
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_successaudit_metadata_no_pii') THEN
        ALTER TABLE learning_successauditlog
            ADD CONSTRAINT chk_successaudit_metadata_no_pii
            CHECK (
                jsonb_typeof(metadata) = 'object'
                AND NOT (metadata ?| ARRAY[
                    'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
                    'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
                ])
            );
    END IF;

    -- PII text scrubbing regex constraints
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_successplan_notes_no_pii') THEN
        ALTER TABLE learning_studentsuccessplan
            ADD CONSTRAINT chk_successplan_notes_no_pii
            CHECK (
                notes IS NULL OR
                notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_actionstep_no_pii') THEN
        ALTER TABLE learning_successactionstep
            ADD CONSTRAINT chk_actionstep_no_pii
            CHECK (
                description IS NULL OR
                description !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_timeline_headline_no_pii') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT chk_timeline_headline_no_pii
            CHECK (
                headline !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_timeline_detail_no_pii') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT chk_timeline_detail_no_pii
            CHECK (
                detail IS NULL OR
                detail !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
            );
    END IF;

    -- Text length check constraints
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_successplan_title_len') THEN
        ALTER TABLE learning_studentsuccessplan
            ADD CONSTRAINT chk_successplan_title_len
            CHECK (length(trim(title)) >= 3 AND length(title) <= 255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_successplan_notes_len') THEN
        ALTER TABLE learning_studentsuccessplan
            ADD CONSTRAINT chk_successplan_notes_len
            CHECK (notes IS NULL OR length(notes) <= 4000);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_actionstep_title_len') THEN
        ALTER TABLE learning_successactionstep
            ADD CONSTRAINT chk_actionstep_title_len
            CHECK (length(trim(title)) >= 3 AND length(title) <= 255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_actionstep_desc_len') THEN
        ALTER TABLE learning_successactionstep
            ADD CONSTRAINT chk_actionstep_desc_len
            CHECK (description IS NULL OR length(description) <= 4000);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_timeline_headline_len') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT chk_timeline_headline_len
            CHECK (length(trim(headline)) >= 3 AND length(headline) <= 255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_timeline_detail_len') THEN
        ALTER TABLE learning_successtimelineevent
            ADD CONSTRAINT chk_timeline_detail_len
            CHECK (detail IS NULL OR length(detail) <= 4000);
    END IF;
END $$;
"""

POSTGRES_LEARNING_SUCCESS_PLANNING_REVERSE_SQL = r"""
-- Drop constraints
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS chk_timeline_detail_len;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS chk_timeline_headline_len;
ALTER TABLE learning_successactionstep DROP CONSTRAINT IF EXISTS chk_actionstep_desc_len;
ALTER TABLE learning_successactionstep DROP CONSTRAINT IF EXISTS chk_actionstep_title_len;
ALTER TABLE learning_studentsuccessplan DROP CONSTRAINT IF EXISTS chk_successplan_notes_len;
ALTER TABLE learning_studentsuccessplan DROP CONSTRAINT IF EXISTS chk_successplan_title_len;

ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS chk_timeline_detail_no_pii;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS chk_timeline_headline_no_pii;
ALTER TABLE learning_successactionstep DROP CONSTRAINT IF EXISTS chk_actionstep_no_pii;
ALTER TABLE learning_studentsuccessplan DROP CONSTRAINT IF EXISTS chk_successplan_notes_no_pii;

ALTER TABLE learning_successauditlog DROP CONSTRAINT IF EXISTS chk_successaudit_metadata_no_pii;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS chk_timeline_metadata_no_pii;

ALTER TABLE learning_successauditlog DROP CONSTRAINT IF EXISTS chk_successaudit_target_xor;
ALTER TABLE learning_successauditlog DROP CONSTRAINT IF EXISTS fk_successaudit_target_timeline;
ALTER TABLE learning_successauditlog DROP CONSTRAINT IF EXISTS fk_successaudit_target_action;
ALTER TABLE learning_successauditlog DROP CONSTRAINT IF EXISTS fk_successaudit_target_plan;
ALTER TABLE learning_successauditlog DROP CONSTRAINT IF EXISTS fk_successaudit_actor;

ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS chk_timeline_type_target_coupling;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS chk_timeline_target_xor;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_replaces;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_target_milestone;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_target_action;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_target_reflection;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_target_insight;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_target_goal;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_actor;
ALTER TABLE learning_successtimelineevent DROP CONSTRAINT IF EXISTS fk_timelineevent_plan;

ALTER TABLE learning_successactionstep DROP CONSTRAINT IF EXISTS fk_successactionstep_plan;
ALTER TABLE learning_studentsuccessplan DROP CONSTRAINT IF EXISTS fk_studentsuccessplan_student;

-- Drop RLS policies
DROP POLICY IF EXISTS p3_vs15_audit_tenant_isolation ON learning_successauditlog;
ALTER TABLE learning_successauditlog NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_successauditlog DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs15_timeline_tenant_isolation ON learning_successtimelineevent;
ALTER TABLE learning_successtimelineevent NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_successtimelineevent DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs15_actionstep_tenant_isolation ON learning_successactionstep;
ALTER TABLE learning_successactionstep NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_successactionstep DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs15_successplan_tenant_isolation ON learning_studentsuccessplan;
ALTER TABLE learning_studentsuccessplan NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_studentsuccessplan DISABLE ROW LEVEL SECURITY;
"""


def enable_learning_success_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_LEARNING_SUCCESS_PLANNING_RLS_SQL)


def disable_learning_success_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_LEARNING_SUCCESS_PLANNING_REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0036_phase3_vs15_learning_success_planning"),
    ]

    operations = [
        migrations.RunPython(
            enable_learning_success_postgres_rls,
            reverse_code=disable_learning_success_postgres_rls,
        ),
    ]
