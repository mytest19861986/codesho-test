from django.db import migrations

POSTGRES_WATERMARK_DLQ_RLS_SQL = """
-- Force RLS on ProjectionWatermark
ALTER TABLE learning_projectionwatermark ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_projectionwatermark FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_pw_tenant_isolation ON learning_projectionwatermark
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on ProjectionDeadLetterEvent
ALTER TABLE learning_projectiondeadletterevent ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_projectiondeadletterevent FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_dle_tenant_isolation ON learning_projectiondeadletterevent
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));
"""

REVERSE_WATERMARK_DLQ_RLS_SQL = """
DROP POLICY IF EXISTS learning_dle_tenant_isolation ON learning_projectiondeadletterevent;
ALTER TABLE learning_projectiondeadletterevent NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_projectiondeadletterevent DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_pw_tenant_isolation ON learning_projectionwatermark;
ALTER TABLE learning_projectionwatermark NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_projectionwatermark DISABLE ROW LEVEL SECURITY;
"""

def enable_watermark_dlq_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_WATERMARK_DLQ_RLS_SQL)

def disable_watermark_dlq_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_WATERMARK_DLQ_RLS_SQL)

class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0010_p3_vs2_watermark_dlq"),
    ]

    operations = [
        migrations.RunPython(
            enable_watermark_dlq_postgres_rls,
            reverse_code=disable_watermark_dlq_postgres_rls,
        ),
    ]
