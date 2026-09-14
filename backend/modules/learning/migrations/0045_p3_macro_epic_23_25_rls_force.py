# Generated for P3-MACRO-EPIC-23-25: PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, and Append-Only Disciplines

from django.db import migrations

EPIC_23_25_TABLES = [
    'learning_curriculumdraftworkspace',
    'learning_contentchangeset',
    'learning_editorialreview',
    'learning_reviewcomment',
    'learning_reviewresolution',
    'learning_authorassignment',
    'learning_changeapprovalrecord',
    'learning_assessmentblueprint',
    'learning_learningobjectivemapping',
    'learning_rubricdefinition',
    'learning_rubriccriterion',
    'learning_assessmentreleasebinding',
    'learning_rubricreviewrecord',
    'learning_curriculumchangeimpact',
    'learning_releasereadinesscheck',
    'learning_releasereadinessgate',
    'learning_cohortrollforwardplan',
    'learning_curriculummigrationdecision',
    'learning_releaseexceptionrecord'
]

def enable_epic_23_25_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for tbl in EPIC_23_25_TABLES:
            cursor.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"DROP POLICY IF EXISTS p3_epic23_25_tenant_isolation_policy ON {tbl};")
            cursor.execute(
                f"CREATE POLICY p3_epic23_25_tenant_isolation_policy ON {tbl} "
                f"FOR ALL USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) "
                f"WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);"
            )

        cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
                BEGIN
                    ALTER ROLE codesho_runtime NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
                EXCEPTION WHEN insufficient_privilege THEN
                    NULL;
                END;
                REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM codesho_runtime;
                REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM codesho_runtime;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_app') THEN
                BEGIN
                    ALTER ROLE codesho_app NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
                EXCEPTION WHEN insufficient_privilege THEN
                    NULL;
                END;
                REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM codesho_app;
                REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM codesho_app;
                REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM codesho_app;
                REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM codesho_app;
            END IF;
        END $$;
        """)

def disable_epic_23_25_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for tbl in EPIC_23_25_TABLES:
            cursor.execute(f"DROP POLICY IF EXISTS p3_epic23_25_tenant_isolation_policy ON {tbl};")
            cursor.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;")

class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0044_p3_macro_epic_23_25_models'),
    ]

    operations = [
        migrations.RunPython(
            enable_epic_23_25_postgres_rls,
            reverse_code=disable_epic_23_25_postgres_rls,
        ),
    ]
