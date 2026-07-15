from django.db import migrations


RLS_SQL = """
ALTER TABLE platform_tenant_tenantmembership ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_tenant_tenantmembership FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_membership_isolation
ON platform_tenant_tenantmembership
USING (
    tenant_id::text = NULLIF(current_setting('app.tenant_id', true), '')
)
WITH CHECK (
    tenant_id::text = NULLIF(current_setting('app.tenant_id', true), '')
);
"""

REVERSE_SQL = """
DROP POLICY IF EXISTS tenant_membership_isolation
ON platform_tenant_tenantmembership;
ALTER TABLE platform_tenant_tenantmembership DISABLE ROW LEVEL SECURITY;
"""


def enable_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(RLS_SQL)


def disable_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SQL)


class Migration(migrations.Migration):
    dependencies = [("platform_tenant", "0001_initial")]
    operations = [
        migrations.RunPython(enable_rls, reverse_code=disable_rls)
    ]
