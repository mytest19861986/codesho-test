from django.db import migrations

POSTGRES_MEDIA_RLS_SQL = """
-- Enforce composite tenant foreign key between synthetic media and lesson
ALTER TABLE learning_syntheticmediaattachment
ADD CONSTRAINT learning_synthetic_media_same_tenant_lesson_fk
FOREIGN KEY (tenant_id, lesson_id)
REFERENCES learning_lesson (tenant_id, id)
DEFERRABLE INITIALLY IMMEDIATE;

-- Force RLS on Synthetic Media Attachment table
ALTER TABLE learning_syntheticmediaattachment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_syntheticmediaattachment FORCE ROW LEVEL SECURITY;

-- Tenant isolation policy (Fail-Closed)
CREATE POLICY learning_synthetic_media_tenant_isolation ON learning_syntheticmediaattachment
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Restrict dangerous DML from runtime role
REVOKE DELETE, TRUNCATE ON TABLE learning_syntheticmediaattachment FROM codesho_runtime;
"""

REVERSE_MEDIA_RLS_SQL = """
DROP POLICY IF EXISTS learning_synthetic_media_tenant_isolation ON learning_syntheticmediaattachment;
ALTER TABLE learning_syntheticmediaattachment NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_syntheticmediaattachment DISABLE ROW LEVEL SECURITY;
ALTER TABLE learning_syntheticmediaattachment DROP CONSTRAINT IF EXISTS learning_synthetic_media_same_tenant_lesson_fk;
"""

def enable_media_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_MEDIA_RLS_SQL)

def disable_media_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_MEDIA_RLS_SQL)

class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0006_syntheticmediaattachment"),
    ]

    operations = [
        migrations.RunPython(
            enable_media_postgres_rls,
            reverse_code=disable_media_postgres_rls,
        ),
    ]
