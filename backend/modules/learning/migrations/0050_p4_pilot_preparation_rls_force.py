# Generated for Phase 4 Controlled Pilot Preparation: PostgreSQL 17 FORCE RLS & Immutability

from django.db import migrations

P4_TABLES = [
    'learning_release_candidate',
    'learning_incident_record',
    'learning_pilot_tenant_provisioning_plan'
]

def enable_p4_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for tbl in P4_TABLES:
            cursor.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"DROP POLICY IF EXISTS p4_tenant_isolation_policy ON {tbl};")
            cursor.execute(
                f"CREATE POLICY p4_tenant_isolation_policy ON {tbl} "
                f"FOR ALL USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) "
                f"WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);"
            )

        cursor.execute("REVOKE DELETE ON learning_incident_record FROM PUBLIC;")
        cursor.execute("REVOKE DELETE ON learning_release_candidate FROM PUBLIC;")
        cursor.execute("REVOKE DELETE ON learning_pilot_tenant_provisioning_plan FROM PUBLIC;")

        cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_app') THEN
                REVOKE DELETE ON learning_incident_record FROM codesho_app;
                REVOKE DELETE ON learning_release_candidate FROM codesho_app;
                REVOKE DELETE ON learning_pilot_tenant_provisioning_plan FROM codesho_app;
            END IF;
        END $$;
        """)

def disable_p4_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for tbl in P4_TABLES:
            cursor.execute(f"DROP POLICY IF EXISTS p4_tenant_isolation_policy ON {tbl};")
            cursor.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;")

class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0049_incidentrecord_pilottenantprovisioningplan_and_more"),
    ]

    operations = [
        migrations.RunPython(
            enable_p4_postgres_rls,
            reverse_code=disable_p4_postgres_rls,
        ),
    ]
