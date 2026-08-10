import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("platform_tenant", "0003_synthetic_membership_activation"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=160)),
                ("state", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="courses", to="platform_tenant.tenant")),
            ],
            options={
                "indexes": [models.Index(fields=["tenant", "state"], name="learn_course_tenant_state_ix")],
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "code"), name="learning_course_tenant_code_uniq"),
                    models.UniqueConstraint(fields=("tenant", "id"), name="learning_course_tenant_id_uniq"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["draft", "published", "archived"])), name="learning_course_state_valid"),
                    models.CheckConstraint(condition=models.Q(("code", ""), _negated=True), name="learning_course_code_nonempty"),
                    models.CheckConstraint(condition=models.Q(("title", ""), _negated=True), name="learning_course_title_nonempty"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Lesson",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=160)),
                ("position", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("state", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lessons", to="learning.course")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="platform_tenant.tenant")),
            ],
            options={
                "indexes": [models.Index(fields=["tenant", "course", "state"], name="learn_lesson_tenant_course_ix")],
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "course", "code"), name="learning_lesson_tenant_course_code_uniq"),
                    models.UniqueConstraint(fields=("tenant", "course", "position"), name="learning_lesson_tenant_course_position_uniq"),
                    models.CheckConstraint(condition=models.Q(("position__gte", 1)), name="learning_lesson_position_positive"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["draft", "published", "archived"])), name="learning_lesson_state_valid"),
                    models.CheckConstraint(condition=models.Q(("code", ""), _negated=True), name="learning_lesson_code_nonempty"),
                    models.CheckConstraint(condition=models.Q(("title", ""), _negated=True), name="learning_lesson_title_nonempty"),
                ],
            },
        ),
    ]
