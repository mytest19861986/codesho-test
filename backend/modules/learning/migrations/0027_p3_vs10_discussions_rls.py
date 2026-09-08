from django.db import migrations

POSTGRES_DISCUSSIONS_RLS_SQL = """
-- Force RLS on DiscussionThread
ALTER TABLE learning_discussionthread ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_discussionthread FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_discussionthread_tenant_isolation ON learning_discussionthread
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on DiscussionComment
ALTER TABLE learning_discussioncomment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_discussioncomment FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_discussioncomment_tenant_isolation ON learning_discussioncomment
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on DiscussionModerationAction
ALTER TABLE learning_discussionmoderationaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_discussionmoderationaction FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_discussionmoderationaction_tenant_isolation ON learning_discussionmoderationaction
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Composite Foreign Key Constraints and Referential Integrity
DO $$
BEGIN
    -- Composite FK for DiscussionThread -> Cohort
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_discthread_tenant_cohort') THEN
        ALTER TABLE learning_discussionthread
            ADD CONSTRAINT fk_discthread_tenant_cohort
            FOREIGN KEY (tenant_id, cohort_id)
            REFERENCES learning_cohort (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for DiscussionThread -> Lesson
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_discthread_tenant_lesson') THEN
        ALTER TABLE learning_discussionthread
            ADD CONSTRAINT fk_discthread_tenant_lesson
            FOREIGN KEY (tenant_id, lesson_id)
            REFERENCES learning_lesson (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for DiscussionComment -> Thread
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_disccomment_tenant_thread') THEN
        ALTER TABLE learning_discussioncomment
            ADD CONSTRAINT fk_disccomment_tenant_thread
            FOREIGN KEY (tenant_id, thread_id)
            REFERENCES learning_discussionthread (tenant_id, id)
            ON DELETE CASCADE;
    END IF;

    -- Hierarchical Same-Thread Composite FK for DiscussionComment -> Parent Comment
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_disccomment_tenant_parent_thread') THEN
        ALTER TABLE learning_discussioncomment
            ADD CONSTRAINT fk_disccomment_tenant_parent_thread
            FOREIGN KEY (tenant_id, parent_id, thread_id)
            REFERENCES learning_discussioncomment (tenant_id, id, thread_id)
            ON DELETE CASCADE;
    END IF;

    -- Composite FK for ModerationAction -> Target Thread (ON DELETE RESTRICT)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_modaction_tenant_target_thread') THEN
        ALTER TABLE learning_discussionmoderationaction
            ADD CONSTRAINT fk_modaction_tenant_target_thread
            FOREIGN KEY (tenant_id, target_thread_id)
            REFERENCES learning_discussionthread (tenant_id, id)
            ON DELETE RESTRICT;
    END IF;

    -- Composite FK for ModerationAction -> Target Comment (ON DELETE RESTRICT)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_modaction_tenant_target_comment') THEN
        ALTER TABLE learning_discussionmoderationaction
            ADD CONSTRAINT fk_modaction_tenant_target_comment
            FOREIGN KEY (tenant_id, target_comment_id)
            REFERENCES learning_discussioncomment (tenant_id, id)
            ON DELETE RESTRICT;
    END IF;
END;
$$;

-- Immutability DDL for DiscussionModerationAction audit trail
REVOKE UPDATE, DELETE ON learning_discussionmoderationaction FROM PUBLIC;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_discussionmoderationaction FROM app_role;
    END IF;
END;
$$;
"""

REVERSE_DISCUSSIONS_RLS_SQL = """
ALTER TABLE learning_discussionmoderationaction DROP CONSTRAINT IF EXISTS fk_modaction_tenant_target_comment;
ALTER TABLE learning_discussionmoderationaction DROP CONSTRAINT IF EXISTS fk_modaction_tenant_target_thread;
ALTER TABLE learning_discussioncomment DROP CONSTRAINT IF EXISTS fk_disccomment_tenant_parent_thread;
ALTER TABLE learning_discussioncomment DROP CONSTRAINT IF EXISTS fk_disccomment_tenant_thread;
ALTER TABLE learning_discussionthread DROP CONSTRAINT IF EXISTS fk_discthread_tenant_lesson;
ALTER TABLE learning_discussionthread DROP CONSTRAINT IF EXISTS fk_discthread_tenant_cohort;

DROP POLICY IF EXISTS learning_discussionmoderationaction_tenant_isolation ON learning_discussionmoderationaction;
ALTER TABLE learning_discussionmoderationaction NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_discussionmoderationaction DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_discussioncomment_tenant_isolation ON learning_discussioncomment;
ALTER TABLE learning_discussioncomment NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_discussioncomment DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_discussionthread_tenant_isolation ON learning_discussionthread;
ALTER TABLE learning_discussionthread NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_discussionthread DISABLE ROW LEVEL SECURITY;
"""


def enable_discussions_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_DISCUSSIONS_RLS_SQL)


def disable_discussions_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_DISCUSSIONS_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0026_p3_vs10_discussions"),
    ]

    operations = [
        migrations.RunPython(
            enable_discussions_postgres_rls,
            reverse_code=disable_discussions_postgres_rls,
        ),
    ]
