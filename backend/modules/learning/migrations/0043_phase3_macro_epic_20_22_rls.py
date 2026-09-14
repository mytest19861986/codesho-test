# Generated for P3-MACRO-EPIC-20-22: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

CURRICULUM_OPERATIONS_TABLES = [
    'learning_curriculumversion',
    'learning_courserelease',
    'learning_modulereleasesnapshot',
    'learning_lessonreleasesnapshot',
    'learning_releaseapprovalrecord',
    'learning_curriculumreleaseauditlog',
    'learning_cohortschedule',
    'learning_learningsession',
    'learning_sessionoccurrence',
    'learning_sessionattendancestate',
    'learning_sessionchangerecord',
    'learning_programdeliveryaggregate',
    'learning_curriculumreleasecoverage',
    'learning_cohortschedulehealth',
    'learning_deliveryexceptionqueue'
]

def enable_curriculum_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for t in CURRICULUM_OPERATIONS_TABLES:
            cursor.execute(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"DROP POLICY IF EXISTS p3_tenant_isolation_policy ON {t};")
            cursor.execute(
                f"CREATE POLICY p3_tenant_isolation_policy ON {t} "
                f"FOR ALL USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) "
                f"WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);"
            )

        # STRICT APPEND-ONLY DISCIPLINE: REVOKE MUTATION PERMISSIONS
        cursor.execute("REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM PUBLIC;")
        cursor.execute("REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM PUBLIC;")
        cursor.execute("REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM PUBLIC;")
        cursor.execute("REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord FROM PUBLIC;")
        cursor.execute("REVOKE UPDATE, DELETE ON learning_sessionchangerecord FROM PUBLIC;")

        cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
                REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM app_role;
                REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM app_role;
                REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM app_role;
                REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord FROM app_role;
                REVOKE UPDATE, DELETE ON learning_sessionchangerecord FROM app_role;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
                REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_sessionchangerecord FROM codesho_runtime;
            END IF;
        END $$;
        """)

def disable_curriculum_operations_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for t in CURRICULUM_OPERATIONS_TABLES:
            cursor.execute(f"DROP POLICY IF EXISTS p3_tenant_isolation_policy ON {t};")
            cursor.execute(f"ALTER TABLE {t} NO FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {t} DISABLE ROW LEVEL SECURITY;")

class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0042_phase3_macro_epic_20_22_models'),
    ]

    operations = [
        migrations.RunPython(
            enable_curriculum_operations_postgres_rls,
            reverse_code=disable_curriculum_operations_postgres_rls,
        ),
    ]
