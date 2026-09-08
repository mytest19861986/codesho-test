from django.db import migrations

POSTGRES_GAMIFICATION_RLS_SQL = """
-- Force RLS on StudentProgressionProfile
ALTER TABLE learning_studentprogressionprofile ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentprogressionprofile FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_progression_profile_tenant_isolation ON learning_studentprogressionprofile
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on StudentBadgeAward
ALTER TABLE learning_studentbadgeaward ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_studentbadgeaward FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_badge_award_tenant_isolation ON learning_studentbadgeaward
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));
"""

REVERSE_GAMIFICATION_RLS_SQL = """
DROP POLICY IF EXISTS learning_badge_award_tenant_isolation ON learning_studentbadgeaward;
ALTER TABLE learning_studentbadgeaward NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_studentbadgeaward DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_progression_profile_tenant_isolation ON learning_studentprogressionprofile;
ALTER TABLE learning_studentprogressionprofile NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_studentprogressionprofile DISABLE ROW LEVEL SECURITY;
"""


def enable_gamification_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_GAMIFICATION_RLS_SQL)


def disable_gamification_postgres_rls(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_GAMIFICATION_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0014_p3_vs4_gamification"),
    ]

    operations = [
        migrations.RunPython(
            enable_gamification_postgres_rls,
            reverse_code=disable_gamification_postgres_rls,
        ),
    ]
