import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0029_p3_vs11_adaptive_progression_rls"),
        ("platform_tenant", "0004_p3_vs12_guardian_access_grant"),
    ]

    operations = [
        migrations.CreateModel(
            name="LearningPortfolio",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("student_id", models.UUIDField(db_index=True)),
                ("headline", models.CharField(max_length=200)),
                ("summary_narrative", models.TextField(blank=True, default="")),
                ("featured_artifact_count", models.SmallIntegerField(default=0)),
                (
                    "visibility",
                    models.CharField(
                        choices=[
                            ("PRIVATE", "Private"),
                            ("GUARDIAN_SHARED", "Guardian Shared"),
                            ("TENANT_PUBLIC", "Tenant Public"),
                        ],
                        default="PRIVATE",
                        max_length=20,
                    ),
                ),
                (
                    "moderation_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("APPROVED", "Approved"),
                            ("FLAGGED", "Flagged"),
                            ("REMOVED", "Removed"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("public_consent_active", models.BooleanField(default=False)),
                ("public_consent_by", models.UUIDField(blank=True, null=True)),
                ("public_consent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_portfolios",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["tenant", "visibility", "moderation_status"], name="idx_portfolio_showcase"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="learningportfolio",
            constraint=models.UniqueConstraint(fields=["tenant", "id"], name="portfolio_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="learningportfolio",
            constraint=models.UniqueConstraint(fields=["tenant", "student_id"], name="portfolio_tenant_student_uniq"),
        ),
        migrations.AddConstraint(
            model_name="learningportfolio",
            constraint=models.CheckConstraint(
                condition=models.Q(visibility__in=["PRIVATE", "GUARDIAN_SHARED", "TENANT_PUBLIC"]),
                name="portfolio_visibility_check",
            ),
        ),
        migrations.AddConstraint(
            model_name="learningportfolio",
            constraint=models.CheckConstraint(
                condition=models.Q(moderation_status__in=["PENDING", "APPROVED", "FLAGGED", "REMOVED"]),
                name="portfolio_moderation_check",
            ),
        ),
        migrations.AddConstraint(
            model_name="learningportfolio",
            constraint=models.CheckConstraint(
                condition=models.Q(featured_artifact_count__gte=0),
                name="portfolio_featured_count_check",
            ),
        ),
        migrations.AddConstraint(
            model_name="learningportfolio",
            constraint=models.CheckConstraint(
                condition=~models.Q(visibility="TENANT_PUBLIC")
                | (models.Q(moderation_status="APPROVED") & models.Q(public_consent_active=True)),
                name="portfolio_public_guard",
            ),
        ),
        migrations.CreateModel(
            name="AchievementArtifact",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "artifact_type",
                    models.CharField(
                        choices=[
                            ("PROJECT_CODE", "Project Code"),
                            ("CAPSTONE_SUBMISSION", "Capstone Submission"),
                            ("CERTIFICATE", "Certificate"),
                            ("BADGE_HIGHLIGHT", "Badge Highlight"),
                        ],
                        max_length=32,
                    ),
                ),
                ("title", models.CharField(max_length=160)),
                ("reflection_notes", models.TextField(blank=True, default="")),
                ("mentor_endorsement", models.TextField(blank=True, default="")),
                ("mentor_user_id", models.UUIDField(blank=True, null=True)),
                ("is_featured", models.BooleanField(default=False)),
                (
                    "moderation_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("APPROVED", "Approved"),
                            ("FLAGGED", "Flagged"),
                            ("REMOVED", "Removed"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "portfolio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="artifacts",
                        to="learning.learningportfolio",
                    ),
                ),
                (
                    "source_certificate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="achievement_artifacts",
                        to="learning.coursecertificate",
                    ),
                ),
                (
                    "source_submission",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="achievement_artifacts",
                        to="learning.submission",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="achievement_artifacts",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["tenant", "portfolio", "is_featured"], name="idx_artifact_portfolio"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="achievementartifact",
            constraint=models.UniqueConstraint(fields=["tenant", "id"], name="artifact_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="achievementartifact",
            constraint=models.CheckConstraint(
                condition=models.Q(artifact_type__in=["PROJECT_CODE", "CAPSTONE_SUBMISSION", "CERTIFICATE", "BADGE_HIGHLIGHT"]),
                name="artifact_type_check",
            ),
        ),
        migrations.AddConstraint(
            model_name="achievementartifact",
            constraint=models.CheckConstraint(
                condition=models.Q(moderation_status__in=["PENDING", "APPROVED", "FLAGGED", "REMOVED"]),
                name="artifact_moderation_check",
            ),
        ),
        migrations.CreateModel(
            name="StudentJourneyTimeline",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("student_id", models.UUIDField(db_index=True)),
                ("event_key", models.CharField(max_length=64)),
                ("event_title", models.CharField(max_length=160)),
                ("narrative_description", models.TextField()),
                ("milestone_date", models.DateField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="journey_timelines",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["tenant", "student_id", "milestone_date"], name="idx_timeline_chronological"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="studentjourneytimeline",
            constraint=models.UniqueConstraint(fields=["tenant", "id"], name="timeline_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="studentjourneytimeline",
            constraint=models.UniqueConstraint(fields=["tenant", "student_id", "event_key"], name="timeline_tenant_event_uniq"),
        ),
        migrations.CreateModel(
            name="PortfolioModerationAction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("actor_id", models.UUIDField(db_index=True)),
                (
                    "action_type",
                    models.CharField(
                        choices=[
                            ("APPROVE", "Approve"),
                            ("UNFLAG", "Unflag"),
                            ("FLAG", "Flag"),
                            ("REMOVE", "Remove"),
                            ("RESTORE", "Restore"),
                            ("CONSENT_GRANT", "Consent Grant"),
                            ("CONSENT_REVOKE", "Consent Revoke"),
                        ],
                        max_length=32,
                    ),
                ),
                ("reason", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "target_artifact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="moderation_actions",
                        to="learning.achievementartifact",
                    ),
                ),
                (
                    "target_portfolio",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="moderation_actions",
                        to="learning.learningportfolio",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolio_moderation_actions",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["tenant", "target_portfolio"], name="idx_modaction_target_port"),
                    models.Index(fields=["tenant", "target_artifact"], name="idx_modaction_target_art"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="portfoliomoderationaction",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    action_type__in=[
                        "APPROVE",
                        "UNFLAG",
                        "FLAG",
                        "REMOVE",
                        "RESTORE",
                        "CONSENT_GRANT",
                        "CONSENT_REVOKE",
                    ]
                ),
                name="modaction_action_type_check",
            ),
        ),
    ]
