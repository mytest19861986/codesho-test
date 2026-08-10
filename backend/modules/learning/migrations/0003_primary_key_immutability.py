from django.db import migrations


FORWARD_SQL = """
CREATE OR REPLACE FUNCTION learning_reject_immutable_updates()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, codesho, pg_temp
AS $$
BEGIN
    IF TG_TABLE_NAME = 'learning_course' THEN
        IF NEW.id IS DISTINCT FROM OLD.id THEN
            RAISE EXCEPTION 'Course id is immutable after creation';
        END IF;
        IF NEW.code IS DISTINCT FROM OLD.code THEN
            RAISE EXCEPTION 'Course code is immutable after creation';
        END IF;
    END IF;
    IF TG_TABLE_NAME = 'learning_lesson' THEN
        IF NEW.id IS DISTINCT FROM OLD.id THEN
            RAISE EXCEPTION 'Lesson id is immutable after creation';
        END IF;
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
"""

REVERSE_SQL = """
CREATE OR REPLACE FUNCTION learning_reject_immutable_updates()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, codesho, pg_temp
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
"""


def enable_primary_key_guards(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(FORWARD_SQL)


def disable_primary_key_guards(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SQL)


class Migration(migrations.Migration):
    dependencies = [("learning", "0002_tenant_rls")]
    operations = [
        migrations.RunPython(
            enable_primary_key_guards,
            reverse_code=disable_primary_key_guards,
        ),
    ]
