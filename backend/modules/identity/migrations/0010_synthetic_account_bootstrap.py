import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.migrations.exceptions import IrreversibleError
from django.db.models import Q

BOOTSTRAP_CONTRACT_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        RAISE EXCEPTION 'codesho_runtime role must exist before synthetic bootstrap migration';
    END IF;
    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'codesho_runtime' AND (rolsuper OR rolbypassrls)
    ) THEN
        RAISE EXCEPTION 'codesho_runtime must not be superuser or BYPASSRLS';
    END IF;
END;
$$;

ALTER TABLE codesho.identity_syntheticbootstraprequest OWNER TO codesho_migrator;
ALTER TABLE codesho.identity_syntheticbootstraprequest ENABLE ROW LEVEL SECURITY;
ALTER TABLE codesho.identity_syntheticbootstraprequest FORCE ROW LEVEL SECURITY;

CREATE POLICY synthetic_bootstrap_request_tenant_isolation
ON codesho.identity_syntheticbootstraprequest
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

CREATE OR REPLACE FUNCTION codesho.enforce_synthetic_bootstrap_request_contract()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, codesho, pg_temp
AS $$
DECLARE
    attestation_tenant uuid;
    provenance_tenant uuid;
    provenance_attestation uuid;
    membership_tenant uuid;
    membership_user uuid;
BEGIN
    IF TG_OP <> 'INSERT' THEN
        RAISE EXCEPTION 'synthetic bootstrap requests are append-only';
    END IF;
    IF current_setting('app.tenant_id', true) IS DISTINCT FROM NEW.tenant_id::text THEN
        RAISE EXCEPTION 'tenant context is required for synthetic bootstrap';
    END IF;
    SELECT tenant_id INTO attestation_tenant
    FROM codesho.identity_adultageattestation WHERE id = NEW.attestation_id;
    SELECT tenant_id, attestation_id INTO provenance_tenant, provenance_attestation
    FROM codesho.identity_adultattestationprovenance WHERE id = NEW.provenance_id;
    SELECT tenant_id, user_id INTO membership_tenant, membership_user
    FROM codesho.platform_tenant_tenantmembership WHERE id = NEW.membership_id;
    IF attestation_tenant IS DISTINCT FROM NEW.tenant_id
       OR provenance_tenant IS DISTINCT FROM NEW.tenant_id
       OR provenance_attestation IS DISTINCT FROM NEW.attestation_id
       OR membership_tenant IS DISTINCT FROM NEW.tenant_id
       OR membership_user IS DISTINCT FROM NEW.user_id THEN
        RAISE EXCEPTION 'synthetic bootstrap tenant linkage is invalid';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM codesho.identity_user
        WHERE id = NEW.user_id AND identity_mode = 'synthetic'
          AND is_active = false AND username IS NULL AND email IS NULL
          AND synthetic_handle IS NOT NULL AND password LIKE '!%%'
    ) THEN
        RAISE EXCEPTION 'synthetic bootstrap user is not dormant and opaque';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM codesho.platform_tenant_tenantmembership
        WHERE id = NEW.membership_id AND is_active = false
          AND role IS NULL AND is_synthetic_bootstrap = true
    ) THEN
        RAISE EXCEPTION 'synthetic bootstrap membership is not dormant';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION codesho.enforce_synthetic_user_dormancy()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, codesho, pg_temp
AS $$
BEGIN
    IF NEW.identity_mode = 'synthetic'
       AND (NEW.is_active OR NEW.username IS NOT NULL OR NEW.email IS NOT NULL
            OR NEW.first_name <> '' OR NEW.last_name <> ''
            OR NEW.synthetic_handle IS NULL OR NEW.password NOT LIKE '!%%') THEN
        RAISE EXCEPTION 'synthetic user must remain inactive, opaque and unusable';
    END IF;
    IF TG_OP = 'UPDATE' AND OLD.identity_mode = 'synthetic'
       AND (NEW.identity_mode IS DISTINCT FROM OLD.identity_mode
            OR NEW.is_active OR NEW.username IS NOT NULL OR NEW.email IS NOT NULL
            OR NEW.first_name <> '' OR NEW.last_name <> ''
            OR NEW.synthetic_handle IS DISTINCT FROM OLD.synthetic_handle
            OR NEW.password NOT LIKE '!%%') THEN
        RAISE EXCEPTION 'synthetic user dormancy is immutable';
    END IF;
    IF TG_OP = 'UPDATE' AND OLD.identity_mode IS DISTINCT FROM NEW.identity_mode THEN
        RAISE EXCEPTION 'identity mode transitions are forbidden';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER synthetic_user_dormancy_guard
BEFORE INSERT OR UPDATE ON codesho.identity_user
FOR EACH ROW EXECUTE FUNCTION codesho.enforce_synthetic_user_dormancy();

CREATE OR REPLACE FUNCTION codesho.reject_synthetic_user_credential()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, codesho, pg_temp
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM codesho.identity_user
        WHERE id = NEW.user_id AND identity_mode = 'synthetic'
    ) THEN
        RAISE EXCEPTION 'synthetic users cannot receive credentials';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER synthetic_user_credential_guard
BEFORE INSERT OR UPDATE ON codesho.identity_passcodecredential
FOR EACH ROW EXECUTE FUNCTION codesho.reject_synthetic_user_credential();

CREATE TRIGGER synthetic_bootstrap_request_contract
BEFORE INSERT OR UPDATE OR DELETE ON codesho.identity_syntheticbootstraprequest
FOR EACH ROW EXECUTE FUNCTION codesho.enforce_synthetic_bootstrap_request_contract();

REVOKE ALL ON TABLE codesho.identity_syntheticbootstraprequest FROM PUBLIC;
GRANT SELECT, INSERT ON TABLE codesho.identity_syntheticbootstraprequest TO codesho_runtime;
REVOKE UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
ON TABLE codesho.identity_syntheticbootstraprequest FROM codesho_runtime;
"""


def install_contract(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(BOOTSTRAP_CONTRACT_SQL)


def irreversible(apps, schema_editor):  # type: ignore[no-untyped-def]
    raise IrreversibleError("synthetic bootstrap contract is irreversible")


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("identity", "0009_adult_attestation_provenance"),
        ("platform_tenant", "0003_synthetic_membership_activation"),
    ]

    operations = [
        migrations.CreateModel(
            name="SyntheticBootstrapRequest",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("tenant_id", models.UUIDField(editable=False)),
                ("idempotency_key", models.UUIDField(editable=False)),
                (
                    "state",
                    models.CharField(
                        choices=[("completed", "Completed")],
                        default="completed",
                        editable=False,
                        max_length=16,
                    ),
                ),
                ("audit_event_id", models.UUIDField(editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, editable=False)),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="identity_mode",
            field=models.CharField(
                choices=[("human", "Human"), ("synthetic", "Synthetic")],
                default="human",
                editable=False,
                max_length=16,
            ),
        ),
        migrations.AlterModelOptions(name="user", options={}),
        migrations.AddField(
            model_name="user",
            name="synthetic_handle",
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                condition=Q(
                    identity_mode="human",
                    username__isnull=False,
                    email__isnull=False,
                    synthetic_handle__isnull=True,
                )
                | Q(
                    identity_mode="synthetic",
                    username__isnull=True,
                    email__isnull=True,
                    synthetic_handle__isnull=False,
                    is_active=False,
                    first_name="",
                    last_name="",
                ),
                name="user_identity_mode_fields_consistent",
            ),
        ),
        migrations.AddField(
            model_name="syntheticbootstraprequest",
            name="attestation",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="identity.adultageattestation",
            ),
        ),
        migrations.AddField(
            model_name="syntheticbootstraprequest",
            name="membership",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="synthetic_bootstrap_requests",
                to="platform_tenant.tenantmembership",
            ),
        ),
        migrations.AddField(
            model_name="syntheticbootstraprequest",
            name="provenance",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="identity.adultattestationprovenance",
            ),
        ),
        migrations.AddField(
            model_name="syntheticbootstraprequest",
            name="user",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="synthetic_bootstrap_requests",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="syntheticbootstraprequest",
            constraint=models.UniqueConstraint(
                fields=("tenant_id", "attestation"),
                name="unique_synthetic_request_tenant_attestation",
            ),
        ),
        migrations.AddConstraint(
            model_name="syntheticbootstraprequest",
            constraint=models.UniqueConstraint(
                fields=("tenant_id", "idempotency_key"),
                name="unique_synthetic_request_tenant_idempotency",
            ),
        ),
        migrations.AddConstraint(
            model_name="syntheticbootstraprequest",
            constraint=models.CheckConstraint(
                condition=Q(state="completed"),
                name="synthetic_request_terminal_state_valid",
            ),
        ),
        migrations.RunPython(install_contract, reverse_code=irreversible),
    ]
