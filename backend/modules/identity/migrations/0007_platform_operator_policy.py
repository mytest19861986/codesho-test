import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("identity", "0006_passcode_change_cleanup_function"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlatformOperatorPolicy",
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
                (
                    "model_label",
                    models.CharField(
                        choices=[
                            ("identity.User", "identity.User"),
                            ("platform_tenant.Tenant", "platform_tenant.Tenant"),
                            (
                                "platform_tenant.TenantMembership",
                                "platform_tenant.TenantMembership",
                            ),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[("list", "List"), ("view", "View")],
                        max_length=64,
                    ),
                ),
                (
                    "scope_kind",
                    models.CharField(
                        choices=[("platform_user_safe", "Platform user safe")],
                        max_length=64,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="created_operator_policies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "operator_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="platform_operator_policies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "revoked_by_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="revoked_operator_policies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        condition=Q(active=True),
                        fields=("operator_user", "model_label", "action", "scope_kind"),
                        name="unique_active_operator_policy",
                    ),
                    models.CheckConstraint(
                        condition=Q(
                            model_label__in=[
                                "identity.User",
                                "platform_tenant.Tenant",
                                "platform_tenant.TenantMembership",
                            ]
                        ),
                        name="operator_policy_model_label_valid",
                    ),
                    models.CheckConstraint(
                        condition=Q(action__in=["list", "view"]),
                        name="operator_policy_action_valid",
                    ),
                    models.CheckConstraint(
                        condition=Q(scope_kind__in=["platform_user_safe"]),
                        name="operator_policy_scope_kind_valid",
                    ),
                    models.CheckConstraint(
                        condition=(
                            Q(
                                active=True,
                                revoked_at__isnull=True,
                                revoked_by_user__isnull=True,
                            )
                            | Q(
                                active=False,
                                revoked_at__isnull=False,
                                revoked_by_user__isnull=False,
                            )
                        ),
                        name="operator_policy_revocation_consistent",
                    ),
                ],
            },
        ),
    ]
