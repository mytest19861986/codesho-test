import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0027_p3_vs10_discussions_rls"),
        ("platform_tenant", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SkillDefinition",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("slug", models.SlugField(max_length=64)),
                ("title", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("ALGORITHMS", "Algorithms"),
                            ("SYNTAX", "Syntax & Core"),
                            ("DATA_STRUCTURES", "Data Structures"),
                            ("OOP", "Object Oriented Programming"),
                            ("PROBLEM_SOLVING", "Problem Solving"),
                        ],
                        max_length=64,
                    ),
                ),
                ("difficulty_level", models.PositiveSmallIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skill_definitions",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SkillDependency",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("is_strict", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "source_skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prerequisites",
                        to="learning.skilldefinition",
                    ),
                ),
                (
                    "target_skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dependents",
                        to="learning.skilldefinition",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skill_dependencies",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LessonSkillMapping",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("mastery_weight", models.DecimalField(decimal_places=2, default=1.0, max_digits=4)),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skill_mappings",
                        to="learning.lesson",
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lesson_mappings",
                        to="learning.skilldefinition",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lesson_skill_mappings",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProcessedLearningEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_id", models.UUIDField(db_index=True)),
                ("event_type", models.CharField(max_length=64)),
                ("student_id", models.UUIDField(db_index=True)),
                ("processed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="processed_learning_events",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StudentSkillProgress",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("student_id", models.UUIDField(db_index=True)),
                (
                    "mastery_level",
                    models.CharField(
                        choices=[
                            ("NOT_STARTED", "Not Started"),
                            ("BEGINNER", "Beginner"),
                            ("DEVELOPING", "Developing"),
                            ("PROFICIENT", "Proficient"),
                            ("MASTERED", "Mastered"),
                        ],
                        default="NOT_STARTED",
                        max_length=16,
                    ),
                ),
                ("mastery_score", models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ("practice_count", models.PositiveIntegerField(default=0)),
                ("last_evaluated_at", models.DateTimeField()),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_progresses",
                        to="learning.skilldefinition",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_skill_progresses",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StudentLearningProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("student_id", models.UUIDField(db_index=True)),
                ("total_skills_tracked", models.PositiveIntegerField(default=0)),
                ("mastered_skills_count", models.PositiveIntegerField(default=0)),
                ("developing_skills_count", models.PositiveIntegerField(default=0)),
                ("overall_competency_index", models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ("identified_learning_gaps", models.JSONField(default=list)),
                ("last_rebuilt_at", models.DateTimeField()),
                ("rebuild_version", models.PositiveIntegerField(default=1)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_learning_profiles",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LearningRecommendation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("student_id", models.UUIDField(db_index=True)),
                (
                    "recommendation_type",
                    models.CharField(
                        choices=[
                            ("REMEDIAL_PRACTICE", "Remedial Practice"),
                            ("NEXT_CHALLENGE", "Next Milestone Challenge"),
                            ("SKILL_EXPANSION", "Skill Expansion"),
                            ("REVISION", "Spaced Revision"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("GENERATED", "Generated"),
                            ("VIEWED", "Viewed"),
                            ("ACCEPTED", "Accepted"),
                            ("COMPLETED", "Completed"),
                            ("DISMISSED", "Dismissed"),
                            ("SUPERSEDED", "Superseded"),
                        ],
                        default="GENERATED",
                        max_length=16,
                    ),
                ),
                ("priority", models.PositiveSmallIntegerField(default=1)),
                ("recommendation_reason", models.CharField(max_length=500)),
                ("evidence_context", models.JSONField(default=dict)),
                ("idempotency_key", models.CharField(db_index=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "target_course",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recommendations",
                        to="learning.course",
                    ),
                ),
                (
                    "target_lesson",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recommendations",
                        to="learning.lesson",
                    ),
                ),
                (
                    "target_skill",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recommendations",
                        to="learning.skilldefinition",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_recommendations",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecommendationTransitionLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("from_status", models.CharField(max_length=16)),
                ("to_status", models.CharField(max_length=16)),
                ("actor_id", models.UUIDField(db_index=True)),
                (
                    "actor_type",
                    models.CharField(
                        choices=[
                            ("STUDENT", "Student"),
                            ("SYSTEM", "System Worker"),
                            ("STAFF", "Staff/Mentor"),
                        ],
                        max_length=16,
                    ),
                ),
                ("transition_reason", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recommendation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transition_logs",
                        to="learning.learningrecommendation",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recommendation_transition_logs",
                        to="platform_tenant.tenant",
                    ),
                ),
            ],
        ),
        # Constraints & Indexes
        migrations.AddConstraint(
            model_name="skilldefinition",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_skilldefinition_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="skilldefinition",
            constraint=models.UniqueConstraint(fields=("tenant", "slug"), name="learning_skilldefinition_tenant_slug_uniq"),
        ),
        migrations.AddConstraint(
            model_name="skilldefinition",
            constraint=models.CheckConstraint(
                condition=models.Q(difficulty_level__gte=1) & models.Q(difficulty_level__lte=5),
                name="learning_skill_difficulty_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="skilldefinition",
            constraint=models.CheckConstraint(
                condition=~models.Q(slug=""),
                name="learning_skill_slug_nonempty",
            ),
        ),
        migrations.AddConstraint(
            model_name="skilldefinition",
            constraint=models.CheckConstraint(
                condition=models.Q(category__in=["ALGORITHMS", "SYNTAX", "DATA_STRUCTURES", "OOP", "PROBLEM_SOLVING"]),
                name="learning_skill_category_valid",
            ),
        ),
        migrations.AddIndex(
            model_name="skilldefinition",
            index=models.Index(fields=["tenant", "category", "is_active"], name="skill_t_cat_act_ix"),
        ),
        migrations.AddConstraint(
            model_name="skilldependency",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_skilldependency_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="skilldependency",
            constraint=models.UniqueConstraint(fields=("tenant", "source_skill", "target_skill"), name="learning_skilldependency_edge_uniq"),
        ),
        migrations.AddConstraint(
            model_name="skilldependency",
            constraint=models.CheckConstraint(
                condition=~models.Q(source_skill=models.F("target_skill")),
                name="learning_skill_no_self_dependency",
            ),
        ),
        migrations.AddConstraint(
            model_name="lessonskillmapping",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_lessonskill_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="lessonskillmapping",
            constraint=models.UniqueConstraint(fields=("tenant", "lesson", "skill"), name="learning_lessonskill_lesson_skill_uniq"),
        ),
        migrations.AddConstraint(
            model_name="lessonskillmapping",
            constraint=models.CheckConstraint(
                condition=models.Q(mastery_weight__gt=0.0) & models.Q(mastery_weight__lte=1.0),
                name="learning_lessonskill_weight_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="processedlearningevent",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_proc_event_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="processedlearningevent",
            constraint=models.UniqueConstraint(fields=("tenant", "event_id", "event_type"), name="learning_proc_event_id_type_uniq"),
        ),
        migrations.AddIndex(
            model_name="processedlearningevent",
            index=models.Index(fields=["tenant", "student_id", "processed_at"], name="proc_event_t_st_pr_ix"),
        ),
        migrations.AddConstraint(
            model_name="studentskillprogress",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_studentskill_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="studentskillprogress",
            constraint=models.UniqueConstraint(fields=("tenant", "student_id", "skill"), name="learning_studentskill_student_skill_uniq"),
        ),
        migrations.AddConstraint(
            model_name="studentskillprogress",
            constraint=models.CheckConstraint(
                condition=models.Q(mastery_score__gte=0.0) & models.Q(mastery_score__lte=100.0),
                name="learning_studentskill_score_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="studentskillprogress",
            constraint=models.CheckConstraint(
                condition=models.Q(mastery_level__in=["NOT_STARTED", "BEGINNER", "DEVELOPING", "PROFICIENT", "MASTERED"]),
                name="learning_studentskill_level_valid",
            ),
        ),
        migrations.AddIndex(
            model_name="studentskillprogress",
            index=models.Index(fields=["tenant", "student_id", "mastery_level"], name="studentskill_t_st_lvl_ix"),
        ),
        migrations.AddConstraint(
            model_name="studentlearningprofile",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_learningprofile_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="studentlearningprofile",
            constraint=models.UniqueConstraint(fields=("tenant", "student_id"), name="learning_learningprofile_student_uniq"),
        ),
        migrations.AddConstraint(
            model_name="studentlearningprofile",
            constraint=models.CheckConstraint(
                condition=models.Q(overall_competency_index__gte=0.0) & models.Q(overall_competency_index__lte=100.0),
                name="learning_profile_competency_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="studentlearningprofile",
            constraint=models.CheckConstraint(
                condition=models.Q(total_skills_tracked__gte=models.F("mastered_skills_count"))
                & models.Q(total_skills_tracked__gte=models.F("developing_skills_count")),
                name="learning_profile_counts_consistent",
            ),
        ),
        migrations.AddConstraint(
            model_name="learningrecommendation",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_recommendation_tenant_id_uniq"),
        ),
        migrations.AddConstraint(
            model_name="learningrecommendation",
            constraint=models.UniqueConstraint(fields=("tenant", "idempotency_key"), name="learning_recommendation_idempotency_uniq"),
        ),
        migrations.AddConstraint(
            model_name="learningrecommendation",
            constraint=models.CheckConstraint(
                condition=models.Q(priority__gte=1) & models.Q(priority__lte=5),
                name="learning_rec_priority_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="learningrecommendation",
            constraint=models.CheckConstraint(
                condition=models.Q(recommendation_type__in=["REMEDIAL_PRACTICE", "NEXT_CHALLENGE", "SKILL_EXPANSION", "REVISION"]),
                name="learning_rec_type_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="learningrecommendation",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=["GENERATED", "VIEWED", "ACCEPTED", "COMPLETED", "DISMISSED", "SUPERSEDED"]),
                name="learning_rec_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="learningrecommendation",
            constraint=models.CheckConstraint(
                condition=(
                    (models.Q(target_course__isnull=False) & models.Q(target_lesson__isnull=True) & models.Q(target_skill__isnull=True))
                    | (models.Q(target_course__isnull=True) & models.Q(target_lesson__isnull=False) & models.Q(target_skill__isnull=True))
                    | (models.Q(target_course__isnull=True) & models.Q(target_lesson__isnull=True) & models.Q(target_skill__isnull=False))
                ),
                name="learning_rec_target_single_choice",
            ),
        ),
        migrations.AddIndex(
            model_name="learningrecommendation",
            index=models.Index(fields=["tenant", "student_id", "status"], name="rec_t_st_stat_ix"),
        ),
        migrations.AddConstraint(
            model_name="recommendationtransitionlog",
            constraint=models.UniqueConstraint(fields=("tenant", "id"), name="learning_rec_trans_log_tenant_id_uniq"),
        ),
        migrations.AddIndex(
            model_name="recommendationtransitionlog",
            index=models.Index(fields=["tenant", "recommendation", "created_at"], name="rec_log_t_rec_cr_ix"),
        ),
    ]
