from django.db import migrations

RUNTIME_COLUMN_GRANTS_SQL = """
REVOKE UPDATE ON TABLE identity_passcodechangechallenge FROM codesho_runtime;
GRANT UPDATE (state, secret_digest, revoked_at, consumed_at, expired_at)
ON TABLE identity_passcodechangechallenge TO codesho_runtime;
"""


def restrict_runtime_update_columns(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(RUNTIME_COLUMN_GRANTS_SQL)


class Migration(migrations.Migration):
    dependencies = [("identity", "0004_passcodechangechallenge")]

    operations = [
        migrations.RunPython(
            restrict_runtime_update_columns,
            reverse_code=migrations.RunPython.noop,
        )
    ]
