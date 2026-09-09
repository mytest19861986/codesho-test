from django.db import migrations

POSTGRES_GROWTH_INSIGHTS_RLS_SQL = """
-- =============================================================================
-- Phase 3 VS13: PostgreSQL 17 FORCE ROW LEVEL SECURITY with NOBYPASSRLS
-- Enforces tenant-isolation policies on all 6 growth insight projection tables
-- =============================================================================

-- Force RLS on CalculationRun
ALTER TABLE learning_calculationrun ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_calculationrun FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_calculationrun_tenant_isolation ON learning_calculationrun
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on GrowthMetricSnapshot
ALTER TABLE learning_growthmetricsnapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_growthmetricsnapshot FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_growthmetricsnapshot_tenant_isolation ON learning_growthmetricsnapshot
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on StudentGrowthTrend
ALTER TABLE learning_studentgrowthtrend ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentgrowthtrend FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_studentgrowthtrend_tenant_isolation ON learning_studentgrowthtrend
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on LearningMilestone
ALTER TABLE learning_learningmilestone ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningmilestone FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_learningmilestone_tenant_isolation ON learning_learningmilestone
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on LearningInsight
ALTER TABLE learning_learninginsight ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learninginsight FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_learninginsight_tenant_isolation ON learning_learninginsight
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on InsightGenerationEvent
ALTER TABLE learning_insightgenerationevent ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_insightgenerationevent FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_insightgenerationevent_tenant_isolation ON learning_insightgenerationevent
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- =============================================================================
-- Composite Foreign Keys and Referential Integrity (Zero Bare UUIDs & NO ACTION triggers)
-- =============================================================================
DO $$
BEGIN
    -- Composite FK: CalculationRun -> Triggered By Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'calcrun_triggered_by_membership_fk') THEN
        ALTER TABLE learning_calculationrun
            ADD CONSTRAINT calcrun_triggered_by_membership_fk
            FOREIGN KEY (tenant_id, triggered_by)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE NO ACTION;
    END IF;

    -- Composite FK: GrowthMetricSnapshot -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'growth_metric_student_membership_fk') THEN
        ALTER TABLE learning_growthmetricsnapshot
            ADD CONSTRAINT growth_metric_student_membership_fk
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: GrowthMetricSnapshot -> CalculationRun
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'growth_metric_calculation_run_fk') THEN
        ALTER TABLE learning_growthmetricsnapshot
            ADD CONSTRAINT growth_metric_calculation_run_fk
            FOREIGN KEY (tenant_id, calculation_run_id)
            REFERENCES learning_calculationrun (tenant_id, id)
            ON DELETE RESTRICT;
    END IF;

    -- Composite FK: StudentGrowthTrend -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'growth_trend_student_membership_fk') THEN
        ALTER TABLE learning_studentgrowthtrend
            ADD CONSTRAINT growth_trend_student_membership_fk
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: StudentGrowthTrend -> CalculationRun
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'growth_trend_calculation_run_fk') THEN
        ALTER TABLE learning_studentgrowthtrend
            ADD CONSTRAINT growth_trend_calculation_run_fk
            FOREIGN KEY (tenant_id, calculation_run_id)
            REFERENCES learning_calculationrun (tenant_id, id)
            ON DELETE RESTRICT;
    END IF;

    -- Composite FK: LearningMilestone -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'milestone_student_membership_fk') THEN
        ALTER TABLE learning_learningmilestone
            ADD CONSTRAINT milestone_student_membership_fk
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: LearningMilestone -> Source Submission
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'milestone_source_submission_fk') THEN
        ALTER TABLE learning_learningmilestone
            ADD CONSTRAINT milestone_source_submission_fk
            FOREIGN KEY (tenant_id, source_submission_id)
            REFERENCES learning_submission (tenant_id, id)
            ON DELETE NO ACTION;
    END IF;

    -- Composite FK: LearningMilestone -> Source Certificate
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'milestone_source_certificate_fk') THEN
        ALTER TABLE learning_learningmilestone
            ADD CONSTRAINT milestone_source_certificate_fk
            FOREIGN KEY (tenant_id, source_certificate_id)
            REFERENCES learning_coursecertificate (tenant_id, id)
            ON DELETE NO ACTION;
    END IF;

    -- Composite FK: LearningInsight -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'insight_student_membership_fk') THEN
        ALTER TABLE learning_learninginsight
            ADD CONSTRAINT insight_student_membership_fk
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: LearningInsight -> CalculationRun
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'insight_calculation_run_fk') THEN
        ALTER TABLE learning_learninginsight
            ADD CONSTRAINT insight_calculation_run_fk
            FOREIGN KEY (tenant_id, calculation_run_id)
            REFERENCES learning_calculationrun (tenant_id, id)
            ON DELETE RESTRICT;
    END IF;

    -- Composite FK: InsightGenerationEvent -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'generation_event_student_membership_fk') THEN
        ALTER TABLE learning_insightgenerationevent
            ADD CONSTRAINT generation_event_student_membership_fk
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: InsightGenerationEvent -> CalculationRun
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'generation_event_calculation_run_fk') THEN
        ALTER TABLE learning_insightgenerationevent
            ADD CONSTRAINT generation_event_calculation_run_fk
            FOREIGN KEY (tenant_id, calculation_run_id)
            REFERENCES learning_calculationrun (tenant_id, id)
            ON DELETE RESTRICT;
    END IF;

    -- Composite FK: InsightGenerationEvent -> Triggered By Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'generation_event_triggered_by_fk') THEN
        ALTER TABLE learning_insightgenerationevent
            ADD CONSTRAINT generation_event_triggered_by_fk
            FOREIGN KEY (tenant_id, triggered_by)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE NO ACTION;
    END IF;

    -- Extra CHECK Constraints: No PII on GrowthMetricSnapshot metadata
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'growth_metric_metadata_no_pii_check') THEN
        ALTER TABLE learning_growthmetricsnapshot
            ADD CONSTRAINT growth_metric_metadata_no_pii_check
            CHECK (
                jsonb_typeof(metadata) = 'object' AND
                NOT (metadata ?| ARRAY['name', 'phone', 'email', 'avatar_url', 'national_id', 'location'])
            );
    END IF;

    -- Extra CHECK Constraints: No PII on StudentGrowthTrend competency_vectors
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'growth_trend_vectors_no_pii_check') THEN
        ALTER TABLE learning_studentgrowthtrend
            ADD CONSTRAINT growth_trend_vectors_no_pii_check
            CHECK (
                jsonb_typeof(competency_vectors) = 'object' AND
                NOT (competency_vectors ?| ARRAY['name', 'phone', 'email', 'avatar_url', 'national_id', 'location'])
            );
    END IF;

    -- Extra CHECK Constraints: Evidence digest format and no PII on LearningMilestone
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'milestone_digest_format_check') THEN
        ALTER TABLE learning_learningmilestone
            ADD CONSTRAINT milestone_digest_format_check
            CHECK (evidence_digest ~* '^[0-9a-f]{64}$');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'milestone_evidence_no_pii_check') THEN
        ALTER TABLE learning_learningmilestone
            ADD CONSTRAINT milestone_evidence_no_pii_check
            CHECK (
                jsonb_typeof(evidence_payload) = 'object' AND
                NOT (evidence_payload ?| ARRAY['name', 'phone', 'email', 'avatar_url', 'national_id', 'location'])
            );
    END IF;

    -- Extra CHECK Constraints: Length checks and no PII on LearningInsight
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'insight_title_len_check') THEN
        ALTER TABLE learning_learninginsight
            ADD CONSTRAINT insight_title_len_check
            CHECK (length(title) >= 5);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'insight_desc_len_check') THEN
        ALTER TABLE learning_learninginsight
            ADD CONSTRAINT insight_desc_len_check
            CHECK (length(description) >= 15);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'insight_metadata_no_pii_check') THEN
        ALTER TABLE learning_learninginsight
            ADD CONSTRAINT insight_metadata_no_pii_check
            CHECK (
                jsonb_typeof(metadata) = 'object' AND
                NOT (metadata ?| ARRAY['name', 'phone', 'email', 'avatar_url', 'national_id', 'location'])
            );
    END IF;

    -- Extra CHECK Constraints: Digest format on InsightGenerationEvent
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'generation_event_digest_format_check') THEN
        ALTER TABLE learning_insightgenerationevent
            ADD CONSTRAINT generation_event_digest_format_check
            CHECK (payload_digest ~* '^[0-9a-f]{64}$');
    END IF;
END;
$$;

-- Immutability on InsightGenerationEvent for application roles
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        REVOKE UPDATE, DELETE ON learning_insightgenerationevent FROM codesho_runtime;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_insightgenerationevent FROM app_role;
    END IF;
END;
$$;
"""

REVERSE_POSTGRES_GROWTH_INSIGHTS_RLS_SQL = """
ALTER TABLE learning_insightgenerationevent DROP CONSTRAINT IF EXISTS generation_event_digest_format_check;
ALTER TABLE learning_learninginsight DROP CONSTRAINT IF EXISTS insight_metadata_no_pii_check;
ALTER TABLE learning_learninginsight DROP CONSTRAINT IF EXISTS insight_desc_len_check;
ALTER TABLE learning_learninginsight DROP CONSTRAINT IF EXISTS insight_title_len_check;
ALTER TABLE learning_learningmilestone DROP CONSTRAINT IF EXISTS milestone_evidence_no_pii_check;
ALTER TABLE learning_learningmilestone DROP CONSTRAINT IF EXISTS milestone_digest_format_check;
ALTER TABLE learning_studentgrowthtrend DROP CONSTRAINT IF EXISTS growth_trend_vectors_no_pii_check;
ALTER TABLE learning_growthmetricsnapshot DROP CONSTRAINT IF EXISTS growth_metric_metadata_no_pii_check;

ALTER TABLE learning_insightgenerationevent DROP CONSTRAINT IF EXISTS generation_event_triggered_by_fk;
ALTER TABLE learning_insightgenerationevent DROP CONSTRAINT IF EXISTS generation_event_calculation_run_fk;
ALTER TABLE learning_insightgenerationevent DROP CONSTRAINT IF EXISTS generation_event_student_membership_fk;
ALTER TABLE learning_learninginsight DROP CONSTRAINT IF EXISTS insight_calculation_run_fk;
ALTER TABLE learning_learninginsight DROP CONSTRAINT IF EXISTS insight_student_membership_fk;
ALTER TABLE learning_learningmilestone DROP CONSTRAINT IF EXISTS milestone_source_certificate_fk;
ALTER TABLE learning_learningmilestone DROP CONSTRAINT IF EXISTS milestone_source_submission_fk;
ALTER TABLE learning_learningmilestone DROP CONSTRAINT IF EXISTS milestone_student_membership_fk;
ALTER TABLE learning_studentgrowthtrend DROP CONSTRAINT IF EXISTS growth_trend_calculation_run_fk;
ALTER TABLE learning_studentgrowthtrend DROP CONSTRAINT IF EXISTS growth_trend_student_membership_fk;
ALTER TABLE learning_growthmetricsnapshot DROP CONSTRAINT IF EXISTS growth_metric_calculation_run_fk;
ALTER TABLE learning_growthmetricsnapshot DROP CONSTRAINT IF EXISTS growth_metric_student_membership_fk;
ALTER TABLE learning_calculationrun DROP CONSTRAINT IF EXISTS calcrun_triggered_by_membership_fk;

DROP POLICY IF EXISTS learning_insightgenerationevent_tenant_isolation ON learning_insightgenerationevent;
ALTER TABLE learning_insightgenerationevent NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_insightgenerationevent DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_learninginsight_tenant_isolation ON learning_learninginsight;
ALTER TABLE learning_learninginsight NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_learninginsight DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_learningmilestone_tenant_isolation ON learning_learningmilestone;
ALTER TABLE learning_learningmilestone NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_learningmilestone DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_studentgrowthtrend_tenant_isolation ON learning_studentgrowthtrend;
ALTER TABLE learning_studentgrowthtrend NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_studentgrowthtrend DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_growthmetricsnapshot_tenant_isolation ON learning_growthmetricsnapshot;
ALTER TABLE learning_growthmetricsnapshot NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_growthmetricsnapshot DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_calculationrun_tenant_isolation ON learning_calculationrun;
ALTER TABLE learning_calculationrun NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_calculationrun DISABLE ROW LEVEL SECURITY;
"""


def enable_growth_insights_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_GROWTH_INSIGHTS_RLS_SQL)


def disable_growth_insights_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_POSTGRES_GROWTH_INSIGHTS_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0032_phase3_vs13_growth_insights"),
    ]

    operations = [
        migrations.RunPython(
            enable_growth_insights_postgres_rls,
            reverse_code=disable_growth_insights_postgres_rls,
        ),
    ]
