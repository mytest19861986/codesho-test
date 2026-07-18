import uuid

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


TTL_AND_RLS_SQL = """
-- Tenant context is set by tenant_atomic with set_config(..., true), which is
-- PostgreSQL's SET LOCAL behavior. Never use a session-scoped app.tenant_id:
-- pooled/reused connections must receive transaction-scoped context only.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        RAISE EXCEPTION 'codesho_runtime role must exist before challenge migration';
    END IF;
    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'codesho_runtime' AND (rolsuper OR rolbypassrls)
    ) THEN
        RAISE EXCEPTION 'codesho_runtime must not be superuser or BYPASSRLS';
    END IF;
END;
$$;

ALTER TABLE identity_passcodechangechallenge OWNER TO codesho_migrator;
ALTER TABLE identity_passcodechangechallenge
    ADD CONSTRAINT passcode_change_challenge_exact_ttl
    CHECK (expires_at = issued_at + INTERVAL '600 seconds');
ALTER TABLE identity_passcodechangechallenge
    ADD CONSTRAINT passcode_change_challenge_digest_size
    CHECK (secret_digest IS NULL OR octet_length(secret_digest) = 32);

ALTER TABLE identity_passcodechangechallenge ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity_passcodechangechallenge FORCE ROW LEVEL SECURITY;

CREATE POLICY passcode_change_challenge_tenant_isolation
ON identity_passcodechangechallenge
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

REVOKE ALL ON TABLE identity_passcodechangechallenge FROM PUBLIC;
REVOKE ALL ON TABLE identity_passcodechangechallenge FROM codesho_runtime;
GRANT SELECT, INSERT, UPDATE ON TABLE identity_passcodechangechallenge TO codesho_runtime;
REVOKE DELETE, TRUNCATE, REFERENCES, TRIGGER ON TABLE identity_passcodechangechallenge
FROM codesho_runtime;
REVOKE CREATE ON SCHEMA codesho FROM codesho_runtime;
"""

REVERSE_SQL = """
DROP POLICY IF EXISTS passcode_change_challenge_tenant_isolation
ON identity_passcodechangechallenge;
ALTER TABLE identity_passcodechangechallenge DISABLE ROW LEVEL SECURITY;
ALTER TABLE identity_passcodechangechallenge
    DROP CONSTRAINT IF EXISTS passcode_change_challenge_exact_ttl;
ALTER TABLE identity_passcodechangechallenge
    DROP CONSTRAINT IF EXISTS passcode_change_challenge_digest_size;
"""


def add_postgresql_contract(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(TTL_AND_RLS_SQL)


def remove_postgresql_contract(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SQL)


class Migration(migrations.Migration):
    dependencies = [
        ("identity", "0003_user_session_auth_epoch"),
        ("platform_tenant", "0002_membership_rls"),
    ]

    operations = [
        migrations.CreateModel(
            name="PasscodeChangeChallenge",
            fields=[
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("selector", models.UUIDField(editable=False, unique=True)),
                ("credential_version", models.PositiveIntegerField()),
                (
                    "purpose",
                    models.CharField(
                        choices=[("forced_passcode_change", "Forced passcode change")],
                        default="forced_passcode_change",
                        max_length=64,
                    ),
                ),
                ("secret_digest", models.BinaryField(editable=False, max_length=32, null=True)),
                ("pepper_id", models.CharField(max_length=64)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("consumed", "Consumed"),
                            ("revoked", "Revoked"),
                            ("expired", "Expired"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                ("issued_at", models.DateTimeField()),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("expired_at", models.DateTimeField(blank=True, null=True)),
                (
                    "credential",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="passcode_change_challenges",
                        to="identity.passcodecredential",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="passcode_change_challenges",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["tenant", "selector", "purpose", "state"],
                        name="passchg_lookup_idx",
                    ),
                    models.Index(fields=["state", "expires_at"], name="passchg_cleanup_idx"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="passcodechangechallenge",
            constraint=models.CheckConstraint(
                condition=Q(("purpose", "forced_passcode_change")),
                name="passcode_change_challenge_purpose_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="passcodechangechallenge",
            constraint=models.CheckConstraint(
                condition=(
                    Q(
                        state="active",
                        secret_digest__isnull=False,
                        consumed_at__isnull=True,
                        revoked_at__isnull=True,
                        expired_at__isnull=True,
                    )
                    | Q(
                        state="consumed",
                        secret_digest__isnull=True,
                        consumed_at__isnull=False,
                        revoked_at__isnull=True,
                        expired_at__isnull=True,
                    )
                    | Q(
                        state="revoked",
                        secret_digest__isnull=True,
                        consumed_at__isnull=True,
                        revoked_at__isnull=False,
                        expired_at__isnull=True,
                    )
                    | Q(
                        state="expired",
                        secret_digest__isnull=True,
                        consumed_at__isnull=True,
                        revoked_at__isnull=True,
                        expired_at__isnull=False,
                    )
                ),
                name="passcode_change_challenge_state_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="passcodechangechallenge",
            constraint=models.UniqueConstraint(
                condition=Q(("state", "active")),
                fields=("credential", "purpose"),
                name="one_active_passcode_change_challenge",
            ),
        ),
        migrations.RunPython(add_postgresql_contract, reverse_code=remove_postgresql_contract),
    ]
