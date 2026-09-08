from django.db import migrations

POSTGRES_NOTIFICATION_RLS_SQL = """
-- Force RLS on NotificationItem
ALTER TABLE learning_notificationitem ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_notificationitem FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_notification_tenant_isolation ON learning_notificationitem
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));
"""

REVERSE_NOTIFICATION_RLS_SQL = """
DROP POLICY IF EXISTS learning_notification_tenant_isolation ON learning_notificationitem;
ALTER TABLE learning_notificationitem NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_notificationitem DISABLE ROW LEVEL SECURITY;
"""


def enable_notification_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_NOTIFICATION_RLS_SQL)


def disable_notification_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_NOTIFICATION_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0012_p3_vs3_notifications"),
    ]

    operations = [
        migrations.RunPython(
            enable_notification_postgres_rls,
            reverse_code=disable_notification_postgres_rls,
        ),
    ]
