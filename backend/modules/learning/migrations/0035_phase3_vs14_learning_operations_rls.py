# Generated for P3-VS14: PostgreSQL 17 FORCE RLS & NOBYPASSRLS for Student Learning Operations

from django.db import migrations

POSTGRES_LEARNING_OPERATIONS_RLS_SQL = r"""
-- =============================================================================
-- Phase 3 VS14: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces tenant-isolation policies on all 6 learning operations tables
-- Conforms to DDL v1.6-CANONICAL and GLM Gate PASS
-- =============================================================================

-- Force RLS on LearningReflection
ALTER TABLE learning_learningreflection ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningreflection FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_refl_tenant_isolation ON learning_learningreflection;
CREATE POLICY p3_vs14_refl_tenant_isolation ON learning_learningreflection
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on StudentLearningGoal
ALTER TABLE learning_studentlearninggoal ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentlearninggoal FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_goal_tenant_isolation ON learning_studentlearninggoal;
CREATE POLICY p3_vs14_goal_tenant_isolation ON learning_studentlearninggoal
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on GoalActionPlan
ALTER TABLE learning_goalactionplan ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_goalactionplan FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_action_tenant_isolation ON learning_goalactionplan;
CREATE POLICY p3_vs14_action_tenant_isolation ON learning_goalactionplan
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on AIAssistedGrowthSuggestion
ALTER TABLE learning_aiassistedgrowthsuggestion ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_aiassistedgrowthsuggestion FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_sugg_tenant_isolation ON learning_aiassistedgrowthsuggestion;
CREATE POLICY p3_vs14_sugg_tenant_isolation ON learning_aiassistedgrowthsuggestion
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on MentorReflectionFeedback
ALTER TABLE learning_mentorreflectionfeedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_mentorreflectionfeedback FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_feedback_tenant_isolation ON learning_mentorreflectionfeedback;
CREATE POLICY p3_vs14_feedback_tenant_isolation ON learning_mentorreflectionfeedback
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Force RLS on ReflectionAuditLog
ALTER TABLE learning_reflectionauditlog ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_reflectionauditlog FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_audit_tenant_isolation ON learning_reflectionauditlog;
CREATE POLICY p3_vs14_audit_tenant_isolation ON learning_reflectionauditlog
FOR ALL
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- Append-only permissions on Audit Log
REVOKE UPDATE, DELETE ON learning_reflectionauditlog FROM PUBLIC;

-- =============================================================================
-- Composite Foreign Keys and Referential Integrity (Zero Bare UUIDs & SA-2 Deferrable FKs)
-- =============================================================================
DO $$
BEGIN
    -- Composite FK: LearningReflection -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_learningreflection_student') THEN
        ALTER TABLE learning_learningreflection
            ADD CONSTRAINT fk_learningreflection_student
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: StudentLearningGoal -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_studentlearninggoal_student') THEN
        ALTER TABLE learning_studentlearninggoal
            ADD CONSTRAINT fk_studentlearninggoal_student
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: StudentLearningGoal -> Target Milestone
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_studentlearninggoal_milestone') THEN
        ALTER TABLE learning_studentlearninggoal
            ADD CONSTRAINT fk_studentlearninggoal_milestone
            FOREIGN KEY (tenant_id, target_milestone_id)
            REFERENCES learning_learningmilestone (tenant_id, id)
            ON DELETE SET NULL;
    END IF;

    -- Composite FK: GoalActionPlan -> Goal
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_goalactionplan_goal') THEN
        ALTER TABLE learning_goalactionplan
            ADD CONSTRAINT fk_goalactionplan_goal
            FOREIGN KEY (tenant_id, goal_id)
            REFERENCES learning_studentlearninggoal (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: AIAssistedGrowthSuggestion -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_growthsuggestion_student') THEN
        ALTER TABLE learning_aiassistedgrowthsuggestion
            ADD CONSTRAINT fk_growthsuggestion_student
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: AIAssistedGrowthSuggestion -> Source Insight
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_growthsuggestion_insight') THEN
        ALTER TABLE learning_aiassistedgrowthsuggestion
            ADD CONSTRAINT fk_growthsuggestion_insight
            FOREIGN KEY (tenant_id, source_insight_id)
            REFERENCES learning_learninginsight (tenant_id, id)
            ON DELETE SET NULL;
    END IF;

    -- Composite FK: AIAssistedGrowthSuggestion -> Generation Run
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_growthsuggestion_run') THEN
        ALTER TABLE learning_aiassistedgrowthsuggestion
            ADD CONSTRAINT fk_growthsuggestion_run
            FOREIGN KEY (tenant_id, generation_run_id)
            REFERENCES learning_calculationrun (tenant_id, id)
            ON DELETE SET NULL;
    END IF;

    -- Composite FK: MentorReflectionFeedback -> Reflection
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_feedback_reflection') THEN
        ALTER TABLE learning_mentorreflectionfeedback
            ADD CONSTRAINT fk_feedback_reflection
            FOREIGN KEY (tenant_id, reflection_id)
            REFERENCES learning_learningreflection (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: MentorReflectionFeedback -> Mentor Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_feedback_mentor') THEN
        ALTER TABLE learning_mentorreflectionfeedback
            ADD CONSTRAINT fk_feedback_mentor
            FOREIGN KEY (tenant_id, mentor_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE RESTRICT;
    END IF;

    -- Composite FK: ReflectionAuditLog -> Actor Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_auditlog_actor') THEN
        ALTER TABLE learning_reflectionauditlog
            ADD CONSTRAINT fk_auditlog_actor
            FOREIGN KEY (tenant_id, actor_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE RESTRICT;
    END IF;

    -- SA-2 Fix: DEFERRABLE INITIALLY DEFERRED FKs on ReflectionAuditLog to avoid cascade order locks
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_auditlog_target_reflection') THEN
        ALTER TABLE learning_reflectionauditlog
            ADD CONSTRAINT fk_auditlog_target_reflection
            FOREIGN KEY (tenant_id, target_reflection_id)
            REFERENCES learning_learningreflection (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_auditlog_target_goal') THEN
        ALTER TABLE learning_reflectionauditlog
            ADD CONSTRAINT fk_auditlog_target_goal
            FOREIGN KEY (tenant_id, target_goal_id)
            REFERENCES learning_studentlearninggoal (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_auditlog_target_feedback') THEN
        ALTER TABLE learning_reflectionauditlog
            ADD CONSTRAINT fk_auditlog_target_feedback
            FOREIGN KEY (tenant_id, target_feedback_id)
            REFERENCES learning_mentorreflectionfeedback (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_auditlog_target_suggestion') THEN
        ALTER TABLE learning_reflectionauditlog
            ADD CONSTRAINT fk_auditlog_target_suggestion
            FOREIGN KEY (tenant_id, target_suggestion_id)
            REFERENCES learning_aiassistedgrowthsuggestion (tenant_id, id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;

    -- Check Constraint: Polymorphic XOR on Audit Targets
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_audit_target_xor') THEN
        ALTER TABLE learning_reflectionauditlog
            ADD CONSTRAINT chk_audit_target_xor
            CHECK (num_nonnulls(target_reflection_id, target_goal_id, target_feedback_id, target_suggestion_id) = 1);
    END IF;

    -- D1 Fix: Full union blacklist on evidence_context
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_suggestion_evidence_no_pii') THEN
        ALTER TABLE learning_aiassistedgrowthsuggestion
            ADD CONSTRAINT chk_suggestion_evidence_no_pii
            CHECK (
                jsonb_typeof(evidence_context) = 'object'
                AND NOT (evidence_context ?| ARRAY[
                    'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
                    'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
                ])
            );
    END IF;

    -- D1 Fix: Full union blacklist on audit metadata
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_audit_metadata_no_pii') THEN
        ALTER TABLE learning_reflectionauditlog
            ADD CONSTRAINT chk_audit_metadata_no_pii
            CHECK (
                jsonb_typeof(metadata) = 'object'
                AND NOT (metadata ?| ARRAY[
                    'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
                    'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
                ])
            );
    END IF;

    -- PII text scrubbing constraints
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_reflection_no_pii') THEN
        ALTER TABLE learning_learningreflection
            ADD CONSTRAINT chk_reflection_no_pii
            CHECK (
                content !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_feedback_no_pii') THEN
        ALTER TABLE learning_mentorreflectionfeedback
            ADD CONSTRAINT chk_feedback_no_pii
            CHECK (
                feedback_text !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_suggestion_provenance_digest') THEN
        ALTER TABLE learning_aiassistedgrowthsuggestion
            ADD CONSTRAINT chk_suggestion_provenance_digest
            CHECK (provenance_digest ~ '^[0-9a-f]{64}$');
    END IF;
END $$;
"""

REVERSE_POSTGRES_LEARNING_OPERATIONS_RLS_SQL = """
DROP POLICY IF EXISTS p3_vs14_audit_tenant_isolation ON learning_reflectionauditlog;
ALTER TABLE learning_reflectionauditlog NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_reflectionauditlog DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_feedback_tenant_isolation ON learning_mentorreflectionfeedback;
ALTER TABLE learning_mentorreflectionfeedback NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_mentorreflectionfeedback DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_sugg_tenant_isolation ON learning_aiassistedgrowthsuggestion;
ALTER TABLE learning_aiassistedgrowthsuggestion NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_aiassistedgrowthsuggestion DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_action_tenant_isolation ON learning_goalactionplan;
ALTER TABLE learning_goalactionplan NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_goalactionplan DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_goal_tenant_isolation ON learning_studentlearninggoal;
ALTER TABLE learning_studentlearninggoal NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_studentlearninggoal DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p3_vs14_refl_tenant_isolation ON learning_learningreflection;
ALTER TABLE learning_learningreflection NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_learningreflection DISABLE ROW LEVEL SECURITY;
"""


def enable_learning_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_LEARNING_OPERATIONS_RLS_SQL)


def disable_learning_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_POSTGRES_LEARNING_OPERATIONS_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0034_phase3_vs14_learning_operations"),
    ]

    operations = [
        migrations.RunPython(
            enable_learning_operations_postgres_rls,
            reverse_code=disable_learning_operations_postgres_rls,
        ),
    ]
