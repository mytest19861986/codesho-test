import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0025_p3_vs9_supervision_rls"),
        ("platform_tenant", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscussionThread",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("author_id", models.UUIDField(db_index=True)),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending Moderation"),
                            ("APPROVED", "Approved"),
                            ("FLAGGED", "Flagged"),
                            ("REMOVED", "Removed"),
                        ],
                        db_index=True,
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("is_pinned", models.BooleanField(default=False)),
                ("is_locked", models.BooleanField(default=False)),
                ("replies_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "cohort",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discussion_threads",
                        to="learning.cohort",
                    ),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discussion_threads",
                        to="learning.lesson",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discussion_threads",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DiscussionComment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("author_id", models.UUIDField(db_index=True)),
                ("body", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending Moderation"),
                            ("APPROVED", "Approved"),
                            ("FLAGGED", "Flagged"),
                            ("REMOVED", "Removed"),
                        ],
                        db_index=True,
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("is_mentor_endorsed", models.BooleanField(default=False)),
                ("endorsed_by_id", models.UUIDField(blank=True, null=True)),
                ("endorsed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="learning.discussioncomment",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discussion_comments",
                        to="platform_tenant.tenant",
                    ),
                ),
                (
                    "thread",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="learning.discussionthread",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DiscussionModerationAction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("APPROVE", "Approve Content"),
                            ("FLAG", "Flag Content"),
                            ("REMOVE", "Remove Content"),
                            ("RESTORE", "Restore Content"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "previous_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("PENDING", "Pending Moderation"),
                            ("APPROVED", "Approved"),
                            ("FLAGGED", "Flagged"),
                            ("REMOVED", "Removed"),
                        ],
                        max_length=16,
                        null=True,
                    ),
                ),
                (
                    "new_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending Moderation"),
                            ("APPROVED", "Approved"),
                            ("FLAGGED", "Flagged"),
                            ("REMOVED", "Removed"),
                        ],
                        max_length=16,
                    ),
                ),
                ("performed_by", models.UUIDField(db_index=True)),
                ("reason", models.CharField(max_length=255)),
                ("note", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "target_comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="moderation_actions",
                        to="learning.discussioncomment",
                    ),
                ),
                (
                    "target_thread",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="moderation_actions",
                        to="learning.discussionthread",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discussion_moderation_actions",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="discussionthread",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_discussionthread_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="discussionthread",
            constraint=models.CheckConstraint(
                condition=(
                    (models.Q(cohort__isnull=False) & models.Q(lesson__isnull=True))
                    | (models.Q(cohort__isnull=True) & models.Q(lesson__isnull=False))
                ),
                name="learning_thread_single_scope_xor",
            ),
        ),
        migrations.AddConstraint(
            model_name="discussionthread",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=["PENDING", "APPROVED", "FLAGGED", "REMOVED"]),
                name="learning_thread_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="discussionthread",
            constraint=models.CheckConstraint(condition=~models.Q(title=""), name="learning_thread_title_nonempty"),
        ),
        migrations.AddConstraint(
            model_name="discussionthread",
            constraint=models.CheckConstraint(condition=~models.Q(body=""), name="learning_thread_body_nonempty"),
        ),
        migrations.AddIndex(
            model_name="discussionthread",
            index=models.Index(fields=["tenant", "cohort", "status"], name="thread_t_coh_st_ix"),
        ),
        migrations.AddIndex(
            model_name="discussionthread",
            index=models.Index(fields=["tenant", "lesson", "status"], name="thread_t_les_st_ix"),
        ),
        migrations.AddIndex(
            model_name="discussionthread",
            index=models.Index(fields=["tenant", "author_id", "status"], name="thread_t_auth_st_ix"),
        ),
        migrations.AddConstraint(
            model_name="discussioncomment",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_discussioncomment_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="discussioncomment",
            constraint=models.UniqueConstraint(fields=("tenant", "id", "thread"), name="learning_comment_tenant_id_thread_uniq"),
        ),
        migrations.AddConstraint(
            model_name="discussioncomment",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=["PENDING", "APPROVED", "FLAGGED", "REMOVED"]),
                name="learning_comment_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="discussioncomment",
            constraint=models.CheckConstraint(condition=~models.Q(body=""), name="learning_comment_body_nonempty"),
        ),
        migrations.AddConstraint(
            model_name="discussioncomment",
            constraint=models.CheckConstraint(
                condition=models.Q(parent__isnull=True) | ~models.Q(parent=models.F("id")),
                name="learning_comment_prevent_self_parent",
            ),
        ),
        migrations.AddIndex(
            model_name="discussioncomment",
            index=models.Index(fields=["tenant", "thread", "status"], name="comment_t_th_st_ix"),
        ),
        migrations.AddIndex(
            model_name="discussioncomment",
            index=models.Index(fields=["tenant", "parent", "status"], name="comment_t_pr_st_ix"),
        ),
        migrations.AddIndex(
            model_name="discussioncomment",
            index=models.Index(fields=["tenant", "author_id", "status"], name="comment_t_auth_st_ix"),
        ),
        migrations.AddConstraint(
            model_name="discussionmoderationaction",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_moderationaction_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="discussionmoderationaction",
            constraint=models.CheckConstraint(
                condition=(
                    (models.Q(target_thread__isnull=False) & models.Q(target_comment__isnull=True))
                    | (models.Q(target_thread__isnull=True) & models.Q(target_comment__isnull=False))
                ),
                name="learning_modaction_target_xor",
            ),
        ),
        migrations.AddConstraint(
            model_name="discussionmoderationaction",
            constraint=models.CheckConstraint(
                condition=models.Q(action__in=["APPROVE", "FLAG", "REMOVE", "RESTORE"]),
                name="learning_modaction_action_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="discussionmoderationaction",
            constraint=models.CheckConstraint(
                condition=models.Q(new_status__in=["PENDING", "APPROVED", "FLAGGED", "REMOVED"]),
                name="learning_modaction_new_status_valid",
            ),
        ),
        migrations.AddIndex(
            model_name="discussionmoderationaction",
            index=models.Index(fields=["tenant", "target_thread", "created_at"], name="modaction_t_th_cr_ix"),
        ),
        migrations.AddIndex(
            model_name="discussionmoderationaction",
            index=models.Index(fields=["tenant", "target_comment", "created_at"], name="modaction_t_cm_cr_ix"),
        ),
        migrations.AddIndex(
            model_name="discussionmoderationaction",
            index=models.Index(fields=["tenant", "performed_by", "created_at"], name="modaction_t_perf_cr_ix"),
        ),
    ]
