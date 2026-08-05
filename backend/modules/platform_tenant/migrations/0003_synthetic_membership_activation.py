from django.db import migrations, models
from django.db.migrations.exceptions import IrreversibleError
from django.db.models import Q

MEMBERSHIP_CONTRACT_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        RAISE EXCEPTION 'codesho_runtime role must exist before synthetic membership migration';
    END IF;
    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'codesho_runtime' AND (rolsuper OR rolbypassrls)
    ) THEN
        RAISE EXCEPTION 'codesho_runtime must not be superuser or BYPASSRLS';
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION codesho.enforce_synthetic_membership_dormancy()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, codesho, pg_temp
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF OLD.is_synthetic_bootstrap THEN
            RAISE EXCEPTION 'synthetic bootstrap membership is immutable';
        END IF;
        RETURN OLD;
    END IF;
    IF NEW.is_synthetic_bootstrap
       AND (NEW.is_active OR NEW.role IS NOT NULL) THEN
        RAISE EXCEPTION 'synthetic bootstrap membership must remain inactive and roleless';
    END IF;
    IF TG_OP = 'UPDATE' AND OLD.is_synthetic_bootstrap
       AND (NEW.is_active OR NEW.role IS DISTINCT FROM OLD.role
            OR NEW.is_synthetic_bootstrap IS DISTINCT FROM OLD.is_synthetic_bootstrap
            OR NEW.tenant_id IS DISTINCT FROM OLD.tenant_id
            OR NEW.user_id IS DISTINCT FROM OLD.user_id) THEN
        RAISE EXCEPTION 'synthetic bootstrap membership activation is forbidden';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER synthetic_membership_dormancy_guard
BEFORE INSERT OR UPDATE OR DELETE ON codesho.platform_tenant_tenantmembership
FOR EACH ROW EXECUTE FUNCTION codesho.enforce_synthetic_membership_dormancy();

REVOKE TRUNCATE ON TABLE codesho.platform_tenant_tenantmembership
FROM codesho_runtime;
"""

REVERSE_MEMBERSHIP_CONTRACT_SQL = """
ALTER TABLE codesho.platform_tenant_tenantmembership NO FORCE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM codesho.platform_tenant_tenantmembership
        WHERE is_synthetic_bootstrap OR role IS NULL
    ) THEN
        RAISE EXCEPTION
            'synthetic membership migration cannot be reversed while incompatible data exists';
    END IF;
END;
$$;

-- Dependency platform_tenant.0002_membership_rls remains applied while 0003 is
-- reversed and owns the table's ENABLE + FORCE RLS contract. Restore it after
-- the temporary owner-visible compatibility guard before removing 0003 objects.
ALTER TABLE codesho.platform_tenant_tenantmembership FORCE ROW LEVEL SECURITY;

DROP TRIGGER IF EXISTS synthetic_membership_dormancy_guard
ON codesho.platform_tenant_tenantmembership;
DROP FUNCTION IF EXISTS codesho.enforce_synthetic_membership_dormancy();
GRANT TRUNCATE ON TABLE codesho.platform_tenant_tenantmembership TO codesho_runtime;
"""


def install_contract(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(MEMBERSHIP_CONTRACT_SQL)


def remove_contract(apps, schema_editor):  # type: ignore[no-untyped-def]
    if schema_editor.connection.vendor != "postgresql":
        return
    try:
        schema_editor.execute(REVERSE_MEMBERSHIP_CONTRACT_SQL)
    except Exception as exc:
        raise IrreversibleError(
            "synthetic membership contract cannot be reversed while protected data exists"
        ) from exc


class Migration(migrations.Migration):
    dependencies = [
        ("platform_tenant", "0002_membership_rls"),
        ("identity", "0009_adult_attestation_provenance"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantmembership",
            name="is_synthetic_bootstrap",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name="tenantmembership",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("owner", "Owner"),
                    ("admin", "Admin"),
                    ("mentor", "Mentor"),
                    ("learner", "Learner"),
                    ("guardian", "Guardian"),
                ],
                max_length=16,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="tenantmembership",
            constraint=models.CheckConstraint(
                condition=Q(is_active=False, is_synthetic_bootstrap=True, role__isnull=True)
                | Q(is_synthetic_bootstrap=False),
                name="synthetic_membership_dormant_fields_consistent",
            ),
        ),
        migrations.AddConstraint(
            model_name="tenantmembership",
            constraint=models.CheckConstraint(
                condition=Q(is_active=False) | Q(role__isnull=False),
                name="active_membership_requires_role",
            ),
        ),
        migrations.RunPython(install_contract, reverse_code=remove_contract),
    ]
