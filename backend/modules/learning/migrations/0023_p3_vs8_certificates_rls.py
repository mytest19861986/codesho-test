from django.db import migrations

POSTGRES_CERTIFICATES_RLS_SQL = """
-- Force RLS on CertificateTemplate
ALTER TABLE learning_certificatetemplate ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_certificatetemplate FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_certificatetemplate_tenant_isolation ON learning_certificatetemplate
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on CourseCertificate
ALTER TABLE learning_coursecertificate ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coursecertificate FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_coursecertificate_tenant_isolation ON learning_coursecertificate
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

-- Force RLS on CertificateVerificationRecord
ALTER TABLE learning_certificateverificationrecord ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_certificateverificationrecord FORCE ROW LEVEL SECURITY;

CREATE POLICY learning_certificateverificationrecord_tenant_isolation ON learning_certificateverificationrecord
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));
"""

REVERSE_CERTIFICATES_RLS_SQL = """
DROP POLICY IF EXISTS learning_certificateverificationrecord_tenant_isolation ON learning_certificateverificationrecord;
ALTER TABLE learning_certificateverificationrecord NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_certificateverificationrecord DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_coursecertificate_tenant_isolation ON learning_coursecertificate;
ALTER TABLE learning_coursecertificate NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_coursecertificate DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_certificatetemplate_tenant_isolation ON learning_certificatetemplate;
ALTER TABLE learning_certificatetemplate NO FORCE ROW LEVEL SECURITY;
ALTER TABLE learning_certificatetemplate DISABLE ROW LEVEL SECURITY;
"""


def enable_certificates_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(POSTGRES_CERTIFICATES_RLS_SQL)


def disable_certificates_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_CERTIFICATES_RLS_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0022_p3_vs8_certificates"),
    ]

    operations = [
        migrations.RunPython(
            enable_certificates_postgres_rls,
            reverse_code=disable_certificates_postgres_rls,
        ),
    ]
