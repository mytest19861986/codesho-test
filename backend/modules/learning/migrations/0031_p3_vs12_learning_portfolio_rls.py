from django.db import migrations

POSTGRES_PORTFOLIO_RLS_SQL = """
-- Force RLS on LearningPortfolio
ALTER TABLE learning_learningportfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningportfolio FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_learningportfolio_tenant_isolation ON learning_learningportfolio
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on AchievementArtifact
ALTER TABLE learning_achievementartifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_achievementartifact FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_achievementartifact_tenant_isolation ON learning_achievementartifact
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on StudentJourneyTimeline
ALTER TABLE learning_studentjourneytimeline ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentjourneytimeline FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_studentjourneytimeline_tenant_isolation ON learning_studentjourneytimeline
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on PortfolioModerationAction
ALTER TABLE learning_portfoliomoderationaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_portfoliomoderationaction FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_portfoliomoderationaction_tenant_isolation ON learning_portfoliomoderationaction
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Composite Foreign Keys and Referential Integrity (Zero Bare UUIDs & NO ACTION triggers)
DO $$
BEGIN
    -- Composite FK: LearningPortfolio -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'portfolio_student_membership_fk') THEN
        ALTER TABLE learning_learningportfolio
            ADD CONSTRAINT portfolio_student_membership_fk
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: AchievementArtifact -> LearningPortfolio
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'artifact_composite_portfolio_fk') THEN
        ALTER TABLE learning_achievementartifact
            ADD CONSTRAINT artifact_composite_portfolio_fk
            FOREIGN KEY (tenant_id, portfolio_id)
            REFERENCES learning_learningportfolio (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: AchievementArtifact -> Source Submission (ON DELETE NO ACTION)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'artifact_source_submission_fk') THEN
        ALTER TABLE learning_achievementartifact
            ADD CONSTRAINT artifact_source_submission_fk
            FOREIGN KEY (tenant_id, source_submission_id)
            REFERENCES learning_submission (tenant_id, id)
            ON DELETE NO ACTION;
    END IF;

    -- Composite FK: AchievementArtifact -> Source Certificate (ON DELETE NO ACTION)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'artifact_source_certificate_fk') THEN
        ALTER TABLE learning_achievementartifact
            ADD CONSTRAINT artifact_source_certificate_fk
            FOREIGN KEY (tenant_id, source_certificate_id)
            REFERENCES learning_coursecertificate (tenant_id, id)
            ON DELETE NO ACTION;
    END IF;

    -- Composite FK: StudentJourneyTimeline -> Student Membership
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'timeline_student_membership_fk') THEN
        ALTER TABLE learning_studentjourneytimeline
            ADD CONSTRAINT timeline_student_membership_fk
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK: PortfolioModerationAction -> Target Portfolio (ON DELETE NO ACTION)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'modaction_portfolio_fk') THEN
        ALTER TABLE learning_portfoliomoderationaction
            ADD CONSTRAINT modaction_portfolio_fk
            FOREIGN KEY (tenant_id, target_portfolio_id)
            REFERENCES learning_learningportfolio (tenant_id, id)
            ON DELETE NO ACTION;
    END IF;

    -- Composite FK: PortfolioModerationAction -> Target Artifact (ON DELETE NO ACTION)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'modaction_artifact_fk') THEN
        ALTER TABLE learning_portfoliomoderationaction
            ADD CONSTRAINT modaction_artifact_fk
            FOREIGN KEY (tenant_id, target_artifact_id)
            REFERENCES learning_achievementartifact (tenant_id, id)
            ON DELETE NO ACTION;
    END IF;

    -- Composite FK: PortfolioModerationAction -> Actor Membership (ON DELETE NO ACTION)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'modaction_actor_membership_fk') THEN
        ALTER TABLE learning_portfoliomoderationaction
            ADD CONSTRAINT modaction_actor_membership_fk
            FOREIGN KEY (tenant_id, actor_id)
            REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
            ON DELETE NO ACTION;
    END IF;

    -- Extra CHECK Constraints: Artifact Title Length, Source Mapping, Mutual Exclusivity
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'artifact_title_len_check') THEN
        ALTER TABLE learning_achievementartifact
            ADD CONSTRAINT artifact_title_len_check
            CHECK (length(title) >= 3);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'artifact_source_mutual_exclusivity') THEN
        ALTER TABLE learning_achievementartifact
            ADD CONSTRAINT artifact_source_mutual_exclusivity
            CHECK (num_nonnulls(source_submission_id, source_certificate_id) <= 1);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'artifact_type_source_mapping_check') THEN
        ALTER TABLE learning_achievementartifact
            ADD CONSTRAINT artifact_type_source_mapping_check
            CHECK (
                (artifact_type = 'CAPSTONE_SUBMISSION' AND source_submission_id IS NOT NULL) OR
                (artifact_type = 'CERTIFICATE' AND source_certificate_id IS NOT NULL) OR
                (artifact_type IN ('PROJECT_CODE', 'BADGE_HIGHLIGHT'))
            );
    END IF;

    -- Extra CHECK Constraints: Timeline Title Length, Desc Length, No PII JSON
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'timeline_title_len_check') THEN
        ALTER TABLE learning_studentjourneytimeline
            ADD CONSTRAINT timeline_title_len_check
            CHECK (length(event_title) >= 3);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'timeline_desc_len_check') THEN
        ALTER TABLE learning_studentjourneytimeline
            ADD CONSTRAINT timeline_desc_len_check
            CHECK (length(narrative_description) >= 10);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'timeline_metadata_no_pii_check') THEN
        ALTER TABLE learning_studentjourneytimeline
            ADD CONSTRAINT timeline_metadata_no_pii_check
            CHECK (
                jsonb_typeof(metadata) = 'object' AND
                NOT (metadata ?| ARRAY['name', 'phone', 'email', 'avatar_url', 'national_id', 'location'])
            );
    END IF;

    -- Extra CHECK Constraints: Headline length on LearningPortfolio
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'portfolio_headline_len_check') THEN
        ALTER TABLE learning_learningportfolio
            ADD CONSTRAINT portfolio_headline_len_check
            CHECK (length(headline) >= 5);
    END IF;

    -- Moderation Action Target Check
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'modaction_target_check') THEN
        ALTER TABLE learning_portfoliomoderationaction
            ADD CONSTRAINT modaction_target_check
            CHECK (num_nonnulls(target_portfolio_id, target_artifact_id) = 1);
    END IF;
END;
$$;

-- Immutability on PortfolioModerationAction for application role
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        REVOKE UPDATE, DELETE ON learning_portfoliomoderationaction FROM codesho_runtime;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_portfoliomoderationaction FROM app_role;
    END IF;
END;
$$;
"""

REVERSE_POSTGRES_PORTFOLIO_RLS_SQL = """
ALTER TABLE learning_portfoliomoderationaction DROP CONSTRAINT IF EXISTS modaction_target_check;
ALTER TABLE learning_learningportfolio DROP CONSTRAINT IF EXISTS portfolio_headline_len_check;
ALTER TABLE learning_studentjourneytimeline DROP CONSTRAINT IF EXISTS timeline_metadata_no_pii_check;
ALTER TABLE learning_studentjourneytimeline DROP CONSTRAINT IF EXISTS timeline_desc_len_check;
ALTER TABLE learning_studentjourneytimeline DROP CONSTRAINT IF EXISTS timeline_title_len_check;
ALTER TABLE learning_achievementartifact DROP CONSTRAINT IF EXISTS artifact_type_source_mapping_check;
ALTER TABLE learning_achievementartifact DROP CONSTRAINT IF EXISTS artifact_source_mutual_exclusivity;
ALTER TABLE learning_achievementartifact DROP CONSTRAINT IF EXISTS artifact_title_len_check;

ALTER TABLE learning_portfoliomoderationaction DROP CONSTRAINT IF EXISTS modaction_actor_membership_fk;
ALTER TABLE learning_portfoliomoderationaction DROP CONSTRAINT IF EXISTS modaction_artifact_fk;
ALTER TABLE learning_portfoliomoderationaction DROP CONSTRAINT IF EXISTS modaction_portfolio_fk;
ALTER TABLE learning_studentjourneytimeline DROP CONSTRAINT IF EXISTS timeline_student_membership_fk;
ALTER TABLE learning_achievementartifact DROP CONSTRAINT IF EXISTS artifact_source_certificate_fk;
ALTER TABLE learning_achievementartifact DROP CONSTRAINT IF EXISTS artifact_source_submission_fk;
ALTER TABLE learning_achievementartifact DROP CONSTRAINT IF EXISTS artifact_composite_portfolio_fk;
ALTER TABLE learning_learningportfolio DROP CONSTRAINT IF EXISTS portfolio_student_membership_fk;

DROP POLICY IF EXISTS learning_portfoliomoderationaction_tenant_isolation ON learning_portfoliomoderationaction;
ALTER TABLE learning_portfoliomoderationaction NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_portfoliomoderationaction DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_studentjourneytimeline_tenant_isolation ON learning_studentjourneytimeline;
ALTER TABLE learning_studentjourneytimeline NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_studentjourneytimeline DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_achievementartifact_tenant_isolation ON learning_achievementartifact;
ALTER TABLE learning_achievementartifact NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_achievementartifact DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_learningportfolio_tenant_isolation ON learning_learningportfolio;
ALTER TABLE learning_learningportfolio NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_learningportfolio DISABLE ROW LEVEL SECURITY;
"""


def enable_portfolio_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_PORTFOLIO_RLS_SQL)


def disable_portfolio_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_POSTGRES_PORTFOLIO_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0030_p3_vs12_learning_portfolio"),
    ]

    operations = [
        migrations.RunPython(
            enable_portfolio_postgres_rls,
            reverse_code=disable_portfolio_postgres_rls,
        ),
    ]

