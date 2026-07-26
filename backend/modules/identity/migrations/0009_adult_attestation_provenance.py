import uuid

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q

PROVENANCE_CONTRACT_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        RAISE EXCEPTION 'codesho_runtime role must exist before provenance migration';
    END IF;
    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'codesho_runtime' AND (rolsuper OR rolbypassrls)
    ) THEN
        RAISE EXCEPTION 'codesho_runtime must not be superuser or BYPASSRLS';
    END IF;
END;
$$;

ALTER TABLE codesho.identity_adultattestationprovenance OWNER TO codesho_migrator;
ALTER TABLE codesho.identity_adultattestationprovenance ENABLE ROW LEVEL SECURITY;
ALTER TABLE codesho.identity_adultattestationprovenance FORCE ROW LEVEL SECURITY;

CREATE POLICY adult_attestation_provenance_tenant_isolation
ON codesho.identity_adultattestationprovenance
USING (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''))
WITH CHECK (tenant_id::text = NULLIF(current_setting('app.tenant_id', true), ''));

CREATE OR REPLACE FUNCTION codesho.enforce_adult_attestation_provenance_contract()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, codesho, pg_temp
AS $$
DECLARE
    attestation_tenant uuid;
BEGIN
    IF TG_OP <> 'INSERT' THEN
        RAISE EXCEPTION 'adult attestation provenance is append-only';
    END IF;

    IF current_setting('app.tenant_id', true) IS DISTINCT FROM NEW.tenant_id::text THEN
        RAISE EXCEPTION 'tenant context is required for provenance';
    END IF;

    IF NEW.collection_context IS DISTINCT FROM 'internal_synthetic_harness'
       OR NEW.receipt_kind IS DISTINCT FROM 'self_attestation' THEN
        RAISE EXCEPTION 'adult attestation provenance constants are invalid';
    END IF;

    SELECT tenant_id
    INTO attestation_tenant
    FROM codesho.identity_adultageattestation
    WHERE id = NEW.attestation_id;

    IF NOT FOUND OR attestation_tenant IS DISTINCT FROM NEW.tenant_id THEN
        RAISE EXCEPTION 'attestation and provenance tenant mismatch';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER adult_attestation_provenance_immutable
BEFORE INSERT OR UPDATE OR DELETE ON codesho.identity_adultattestationprovenance
FOR EACH ROW EXECUTE FUNCTION codesho.enforce_adult_attestation_provenance_contract();

REVOKE ALL ON TABLE codesho.identity_adultattestationprovenance FROM PUBLIC;
REVOKE ALL ON TABLE codesho.identity_adultattestationprovenance FROM codesho_runtime;
GRANT INSERT ON TABLE codesho.identity_adultattestationprovenance TO codesho_runtime;
REVOKE SELECT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
ON TABLE codesho.identity_adultattestationprovenance FROM codesho_runtime;
"""

REVERSE_CONTRACT_SQL = """
DROP TRIGGER IF EXISTS adult_attestation_provenance_immutable
ON codesho.identity_adultattestationprovenance;
DROP FUNCTION IF EXISTS codesho.enforce_adult_attestation_provenance_contract();
DROP POLICY IF EXISTS adult_attestation_provenance_tenant_isolation
ON codesho.identity_adultattestationprovenance;
ALTER TABLE codesho.identity_adultattestationprovenance DISABLE ROW LEVEL SECURITY;
"""


def add_postgresql_contract(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(PROVENANCE_CONTRACT_SQL)


def remove_postgresql_contract(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_CONTRACT_SQL)


class Migration(migrations.Migration):
    dependencies = [("identity", "0008_adult_age_attestation")]

    operations = [
        migrations.CreateModel(
            name="AdultAttestationProvenance",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("tenant_id", models.UUIDField(editable=False)),
                (
                    "collection_context",
                    models.CharField(
                        choices=[
                            (
                                "internal_synthetic_harness",
                                "Internal synthetic harness",
                            )
                        ],
                        default="internal_synthetic_harness",
                        editable=False,
                        max_length=64,
                    ),
                ),
                (
                    "receipt_kind",
                    models.CharField(
                        choices=[("self_attestation", "Self attestation")],
                        default="self_attestation",
                        editable=False,
                        max_length=32,
                    ),
                ),
                ("recorded_at", models.DateTimeField(auto_now_add=True, editable=False)),
                (
                    "attestation",
                    models.OneToOneField(
                        db_column="attestation_id",
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="identity.adultageattestation",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(
                        condition=Q(collection_context="internal_synthetic_harness"),
                        name="adult_provenance_context_valid",
                    ),
                    models.CheckConstraint(
                        condition=Q(receipt_kind="self_attestation"),
                        name="adult_provenance_receipt_valid",
                    ),
                ]
            },
        ),
        migrations.RunPython(add_postgresql_contract, reverse_code=remove_postgresql_contract),
    ]
