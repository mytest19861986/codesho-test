from django.db import migrations


POSTGRES_SQL = """
ALTER TABLE learning_course ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_course FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_lesson ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_lesson FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_course_tenant_isolation
ON learning_course
USING (
    tenant_id::text = NULLIF(current_setting('app.tenant_id', true), '')
)
WITH CHECK (
    tenant_id::text = NULLIF(current_setting('app.tenant_id', true), '')
);

CREATE POLICY learning_lesson_tenant_isolation
ON learning_lesson
USING (
    tenant_id::text = NULLIF(current_setting('app.tenant_id', true), '')
)
WITH CHECK (
    tenant_id::text = NULLIF(current_setting('app.tenant_id', true), '')
);

ALTER TABLE learning_lesson
ADD CONSTRAINT learning_lesson_same_tenant_course_fk
FOREIGN KEY (tenant_id, course_id)
REFERENCES learning_course (tenant_id, id)
DEFERRABLE INITIALLY IMMEDIATE;

CREATE OR REPLACE FUNCTION learning_reject_immutable_updates()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_TABLE_NAME = 'learning_course' AND NEW.code IS DISTINCT FROM OLD.code THEN
        RAISE EXCEPTION 'Course code is immutable after creation';
    END IF;
    IF TG_TABLE_NAME = 'learning_lesson' THEN
        IF NEW.code IS DISTINCT FROM OLD.code THEN
            RAISE EXCEPTION 'Lesson code is immutable after creation';
        END IF;
        IF NEW.position IS DISTINCT FROM OLD.position THEN
            RAISE EXCEPTION 'Lesson position is immutable after creation';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER learning_course_immutable_guard
BEFORE UPDATE ON learning_course
FOR EACH ROW EXECUTE FUNCTION learning_reject_immutable_updates();

CREATE TRIGGER learning_lesson_immutable_guard
BEFORE UPDATE ON learning_lesson
FOR EACH ROW EXECUTE FUNCTION learning_reject_immutable_updates();
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS learning_lesson_immutable_guard ON learning_lesson;
DROP TRIGGER IF EXISTS learning_course_immutable_guard ON learning_course;
DROP FUNCTION IF EXISTS learning_reject_immutable_updates();
ALTER TABLE learning_lesson DROP CONSTRAINT IF EXISTS learning_lesson_same_tenant_course_fk;
DROP POLICY IF EXISTS learning_lesson_tenant_isolation ON learning_lesson;
DROP POLICY IF EXISTS learning_course_tenant_isolation ON learning_course;
ALTER TABLE learning_lesson DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_course DISABLE ROW LEVEL SECURITY;
"""


def enable_postgres_guards(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_SQL)


def disable_postgres_guards(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SQL)


class Migration(migrations.Migration):
    dependencies = [("learning", "0001_initial")]
    operations = [
        migrations.RunPython(enable_postgres_guards, reverse_code=disable_postgres_guards),
    ]
