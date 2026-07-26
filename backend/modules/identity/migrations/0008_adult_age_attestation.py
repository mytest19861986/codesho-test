import uuid

from django.db import migrations, models
from django.db.models import Q


def enforce_attestation_immutability(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        CREATE OR REPLACE FUNCTION codesho.enforce_adult_age_attestation_immutability()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'adult age attestations are append-only';
        END;
        $$;

        CREATE TRIGGER adult_age_attestation_immutable
        BEFORE UPDATE OR DELETE ON codesho.identity_adultageattestation
        FOR EACH ROW EXECUTE FUNCTION codesho.enforce_adult_age_attestation_immutability();

        REVOKE UPDATE, DELETE, TRUNCATE
        ON codesho.identity_adultageattestation FROM codesho_runtime;
        """
    )


def drop_attestation_immutability(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        DROP TRIGGER IF EXISTS adult_age_attestation_immutable
        ON codesho.identity_adultageattestation;
        DROP FUNCTION IF EXISTS codesho.enforce_adult_age_attestation_immutability();
        """
    )


class Migration(migrations.Migration):
    dependencies = [("identity", "0007_platform_operator_policy")]

    operations = [
        migrations.CreateModel(
            name="AdultAgeAttestation",
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
                ("subject_id", models.UUIDField(editable=False)),
                (
                    "status",
                    models.CharField(
                        choices=[("adult_attested", "Adult attested")],
                        default="adult_attested",
                        editable=False,
                        max_length=32,
                    ),
                ),
                ("policy_version", models.CharField(editable=False, max_length=64)),
                (
                    "source",
                    models.CharField(
                        choices=[("internal_test_api", "Internal test API")],
                        default="internal_test_api",
                        editable=False,
                        max_length=32,
                    ),
                ),
                (
                    "audit_event_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("attested_at", models.DateTimeField(auto_now_add=True, editable=False)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("tenant_id", "subject_id", "policy_version"),
                        name="unique_adult_attestation_per_policy",
                    ),
                    models.CheckConstraint(
                        condition=Q(status="adult_attested"),
                        name="adult_attestation_status_valid",
                    ),
                    models.CheckConstraint(
                        condition=Q(source="internal_test_api"),
                        name="adult_attestation_source_valid",
                    ),
                ]
            },
        ),
        migrations.RunPython(
            enforce_attestation_immutability,
            drop_attestation_immutability,
        ),
    ]
