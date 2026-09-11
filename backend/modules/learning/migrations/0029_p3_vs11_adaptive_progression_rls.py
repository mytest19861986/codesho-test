from django.db import migrations

POSTGRES_ADAPTIVE_PROGRESSION_RLS_SQL = """
-- Force RLS on SkillDefinition
ALTER TABLE learning_skilldefinition ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_skilldefinition FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_skilldefinition_tenant_isolation ON learning_skilldefinition
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on SkillDependency
ALTER TABLE learning_skilldependency ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_skilldependency FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_skilldependency_tenant_isolation ON learning_skilldependency
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on LessonSkillMapping
ALTER TABLE learning_lessonskillmapping ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_lessonskillmapping FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_lessonskillmapping_tenant_isolation ON learning_lessonskillmapping
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on ProcessedLearningEvent
ALTER TABLE learning_processedlearningevent ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_processedlearningevent FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_processedlearningevent_tenant_isolation ON learning_processedlearningevent
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on StudentSkillProgress
ALTER TABLE learning_studentskillprogress ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentskillprogress FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_studentskillprogress_tenant_isolation ON learning_studentskillprogress
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on StudentLearningProfile
ALTER TABLE learning_studentlearningprofile ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentlearningprofile FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_studentlearningprofile_tenant_isolation ON learning_studentlearningprofile
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on LearningRecommendation
ALTER TABLE learning_learningrecommendation ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningrecommendation FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_learningrecommendation_tenant_isolation ON learning_learningrecommendation
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on RecommendationTransitionLog
ALTER TABLE learning_recommendationtransitionlog ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_recommendationtransitionlog FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_recommendationtransitionlog_tenant_isolation ON learning_recommendationtransitionlog
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Composite Foreign Key Constraints and Referential Integrity (Zero Bare UUIDs)
DO $$
BEGIN
    -- Composite FK for SkillDependency -> Source Skill
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_skilldep_tenant_source_skill') THEN
        ALTER TABLE learning_skilldependency
            ADD CONSTRAINT fk_skilldep_tenant_source_skill
            FOREIGN KEY (tenant_id, source_skill_id)
            REFERENCES learning_skilldefinition (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for SkillDependency -> Target Skill
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_skilldep_tenant_target_skill') THEN
        ALTER TABLE learning_skilldependency
            ADD CONSTRAINT fk_skilldep_tenant_target_skill
            FOREIGN KEY (tenant_id, target_skill_id)
            REFERENCES learning_skilldefinition (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for LessonSkillMapping -> Lesson
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_lessonskill_tenant_lesson') THEN
        ALTER TABLE learning_lessonskillmapping
            ADD CONSTRAINT fk_lessonskill_tenant_lesson
            FOREIGN KEY (tenant_id, lesson_id)
            REFERENCES learning_lesson (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for LessonSkillMapping -> Skill
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_lessonskill_tenant_skill') THEN
        ALTER TABLE learning_lessonskillmapping
            ADD CONSTRAINT fk_lessonskill_tenant_skill
            FOREIGN KEY (tenant_id, skill_id)
            REFERENCES learning_skilldefinition (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for StudentSkillProgress -> Skill
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_studentskill_tenant_skill') THEN
        ALTER TABLE learning_studentskillprogress
            ADD CONSTRAINT fk_studentskill_tenant_skill
            FOREIGN KEY (tenant_id, skill_id)
            REFERENCES learning_skilldefinition (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for LearningRecommendation -> Target Course
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_recommendation_tenant_course') THEN
        ALTER TABLE learning_learningrecommendation
            ADD CONSTRAINT fk_recommendation_tenant_course
            FOREIGN KEY (tenant_id, target_course_id)
            REFERENCES learning_course (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for LearningRecommendation -> Target Lesson
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_recommendation_tenant_lesson') THEN
        ALTER TABLE learning_learningrecommendation
            ADD CONSTRAINT fk_recommendation_tenant_lesson
            FOREIGN KEY (tenant_id, target_lesson_id)
            REFERENCES learning_lesson (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for LearningRecommendation -> Target Skill
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_recommendation_tenant_skill') THEN
        ALTER TABLE learning_learningrecommendation
            ADD CONSTRAINT fk_recommendation_tenant_skill
            FOREIGN KEY (tenant_id, target_skill_id)
            REFERENCES learning_skilldefinition (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for RecommendationTransitionLog -> Recommendation
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rec_trans_log_tenant_rec') THEN
        ALTER TABLE learning_recommendationtransitionlog
            ADD CONSTRAINT fk_rec_trans_log_tenant_rec
            FOREIGN KEY (tenant_id, recommendation_id)
            REFERENCES learning_learningrecommendation (tenant_id, id)
            ON DELETE CASCADE;
    END IF;
END;
$$;

-- DAG Guard Trigger using Recursive CTE and Advisory Lock (B1 Enforced)
CREATE OR REPLACE FUNCTION learning_fn_skill_dag_guard()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- Advisory xact lock to serialize concurrent edge additions per tenant (Phantom-Cycle race guard)
    PERFORM pg_advisory_xact_lock(hashtextextended(NEW.tenant_id::text, 42));

    -- Qwen Invariant 5: Forbid linking to inactive skills
    IF EXISTS (
        SELECT 1 FROM learning_skilldefinition 
        WHERE tenant_id = NEW.tenant_id AND id IN (NEW.source_skill_id, NEW.target_skill_id) AND is_active = FALSE
    ) THEN
        RAISE EXCEPTION 'Dependency cannot be established on an inactive skill';
    END IF;

    -- Recursive CTE cycle detection
    IF EXISTS (
        WITH RECURSIVE walk(node) AS (
            SELECT NEW.target_skill_id
            UNION
            SELECT d.target_skill_id
            FROM learning_skilldependency d
            JOIN walk w ON d.tenant_id = NEW.tenant_id
                       AND d.source_skill_id = w.node
                       AND (TG_OP = 'INSERT' OR d.id <> NEW.id)
        )
        SELECT 1 FROM walk WHERE node = NEW.source_skill_id
    ) THEN
        RAISE EXCEPTION 'DAG invariant violated: %% -> %% creates a cyclic dependency',
            NEW.source_skill_id, NEW.target_skill_id;
    END IF;
    RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_skill_dag_guard ON learning_skilldependency;
CREATE TRIGGER trg_skill_dag_guard
    BEFORE INSERT OR UPDATE OF source_skill_id, target_skill_id
    ON learning_skilldependency
    FOR EACH ROW EXECUTE FUNCTION learning_fn_skill_dag_guard();

-- Immutability DDL for RecommendationTransitionLog audit trail
REVOKE UPDATE, DELETE ON learning_recommendationtransitionlog FROM PUBLIC;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_recommendationtransitionlog FROM app_role;
    END IF;
END;
$$;
"""

REVERSE_ADAPTIVE_PROGRESSION_RLS_SQL = """
DROP TRIGGER IF EXISTS trg_skill_dag_guard ON learning_skilldependency;
DROP FUNCTION IF EXISTS learning_fn_skill_dag_guard();

ALTER TABLE learning_recommendationtransitionlog DROP CONSTRAINT IF EXISTS fk_rec_trans_log_tenant_rec;
ALTER TABLE learning_learningrecommendation DROP CONSTRAINT IF EXISTS fk_recommendation_tenant_skill;
ALTER TABLE learning_learningrecommendation DROP CONSTRAINT IF EXISTS fk_recommendation_tenant_lesson;
ALTER TABLE learning_learningrecommendation DROP CONSTRAINT IF EXISTS fk_recommendation_tenant_course;
ALTER TABLE learning_studentskillprogress DROP CONSTRAINT IF EXISTS fk_studentskill_tenant_skill;
ALTER TABLE learning_lessonskillmapping DROP CONSTRAINT IF EXISTS fk_lessonskill_tenant_skill;
ALTER TABLE learning_lessonskillmapping DROP CONSTRAINT IF EXISTS fk_lessonskill_tenant_lesson;
ALTER TABLE learning_skilldependency DROP CONSTRAINT IF EXISTS fk_skilldep_tenant_target_skill;
ALTER TABLE learning_skilldependency DROP CONSTRAINT IF EXISTS fk_skilldep_tenant_source_skill;

DROP POLICY IF EXISTS learning_recommendationtransitionlog_tenant_isolation ON learning_recommendationtransitionlog;
DROP POLICY IF EXISTS learning_learningrecommendation_tenant_isolation ON learning_learningrecommendation;
DROP POLICY IF EXISTS learning_studentlearningprofile_tenant_isolation ON learning_studentlearningprofile;
DROP POLICY IF EXISTS learning_studentskillprogress_tenant_isolation ON learning_studentskillprogress;
DROP POLICY IF EXISTS learning_processedlearningevent_tenant_isolation ON learning_processedlearningevent;
DROP POLICY IF EXISTS learning_lessonskillmapping_tenant_isolation ON learning_lessonskillmapping;
DROP POLICY IF EXISTS learning_skilldependency_tenant_isolation ON learning_skilldependency;
DROP POLICY IF EXISTS learning_skilldefinition_tenant_isolation ON learning_skilldefinition;
"""


def enable_adaptive_progression_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_ADAPTIVE_PROGRESSION_RLS_SQL)


def disable_adaptive_progression_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_ADAPTIVE_PROGRESSION_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0028_p3_vs11_adaptive_progression"),
    ]

    operations = [
        migrations.RunPython(
            enable_adaptive_progression_postgres_rls,
            reverse_code=disable_adaptive_progression_postgres_rls,
        ),
    ]

