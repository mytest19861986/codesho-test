import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class PublicationState(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class AssignmentState(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    CLOSED = "closed", "Closed"


class SubmissionState(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    REVIEWED = "reviewed", "Reviewed"


class ProgressState(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"


class LearningPath(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_paths",
    )
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    state = models.CharField(
        max_length=16,
        choices=PublicationState.choices,
        default=PublicationState.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="learning_path_tenant_code_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_path_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(state__in=PublicationState.values),
                name="learning_path_state_valid",
            ),
            models.CheckConstraint(
                condition=~Q(code=""),
                name="learning_path_code_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_path_title_nonempty",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "state"], name="learn_path_tenant_state_ix"),
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.code}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "LearningPath id is immutable after creation."})
        if self.pk and not self._state.adding:
            original_code = (
                type(self).objects.filter(pk=self.pk).values_list("code", flat=True).first()
            )
            if original_code is not None and original_code != self.code:
                raise ValidationError({"code": "LearningPath code is immutable after creation."})
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="courses",
    )
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    state = models.CharField(
        max_length=16,
        choices=PublicationState.choices,
        default=PublicationState.DRAFT,
    )
    is_cohort_mandatory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="learning_course_tenant_code_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_course_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(state__in=PublicationState.values),
                name="learning_course_state_valid",
            ),
            models.CheckConstraint(
                condition=~Q(code=""),
                name="learning_course_code_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_course_title_nonempty",
            ),
        ]
        indexes = [
            models.Index(
                fields=["tenant", "state"],
                name="learn_course_tenant_state_ix",
            )
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.code}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "Course id is immutable after creation."})
        if self.pk and not self._state.adding:
            original_code = (
                type(self).objects.filter(pk=self.pk).values_list("code", flat=True).first()
            )
            if original_code is not None and original_code != self.code:
                raise ValidationError({"code": "Course code is immutable after creation."})
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="modules",
    )
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="modules")
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    position = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    state = models.CharField(
        max_length=16,
        choices=PublicationState.choices,
        default=PublicationState.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "course", "code"],
                name="learning_module_tenant_course_code_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "position"],
                name="learning_module_tenant_course_pos_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_module_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(position__gte=1),
                name="learning_module_pos_positive",
            ),
            models.CheckConstraint(
                condition=Q(state__in=PublicationState.values),
                name="learning_module_state_valid",
            ),
            models.CheckConstraint(
                condition=~Q(code=""),
                name="learning_module_code_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_module_title_nonempty",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course", "state"], name="learn_mod_tenant_course_ix"),
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.course_id}:{self.code}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "Module id is immutable after creation."})
        if self.pk and not self._state.adding:
            original = type(self).objects.filter(pk=self.pk).values("code", "position").first()
            if original is not None:
                errors: dict[str, str] = {}
                if original["code"] != self.code:
                    errors["code"] = "Module code is immutable after creation."
                if original["position"] != self.position:
                    errors["position"] = "Module position is immutable after creation."
                if errors:
                    raise ValidationError(errors)
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="lessons")
    module = models.ForeignKey(
        Module,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="lessons",
    )
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    position = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    state = models.CharField(
        max_length=16,
        choices=PublicationState.choices,
        default=PublicationState.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "course", "code"],
                name="learning_lesson_tenant_course_code_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "position"],
                name="learning_lesson_tenant_course_position_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_lesson_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(position__gte=1),
                name="learning_lesson_position_positive",
            ),
            models.CheckConstraint(
                condition=Q(state__in=PublicationState.values),
                name="learning_lesson_state_valid",
            ),
            models.CheckConstraint(
                condition=~Q(code=""),
                name="learning_lesson_code_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_lesson_title_nonempty",
            ),
        ]
        indexes = [
            models.Index(
                fields=["tenant", "course", "state"],
                name="learn_lesson_tenant_course_ix",
            )
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.course_id}:{self.code}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "Lesson id is immutable after creation."})
        if self.pk and not self._state.adding:
            original = type(self).objects.filter(pk=self.pk).values("code", "position").first()
            if original is not None:
                errors: dict[str, str] = {}
                if original["code"] != self.code:
                    errors["code"] = "Lesson code is immutable after creation."
                if original["position"] != self.position:
                    errors["position"] = "Lesson position is immutable after creation."
                if errors:
                    raise ValidationError(errors)
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name="assignments")
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    description = models.TextField(default="")
    state = models.CharField(
        max_length=16,
        choices=AssignmentState.choices,
        default=AssignmentState.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "lesson", "code"],
                name="learning_assign_tenant_lesson_code_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_assign_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(state__in=AssignmentState.values),
                name="learning_assign_state_valid",
            ),
            models.CheckConstraint(
                condition=~Q(code=""),
                name="learning_assign_code_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_assign_title_nonempty",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "lesson", "state"], name="learn_asgn_tenant_les_ix"),
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.lesson_id}:{self.code}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "Assignment id is immutable after creation."})
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT, related_name="submissions")
    student_id = models.UUIDField()
    content = models.TextField()
    state = models.CharField(
        max_length=16,
        choices=SubmissionState.choices,
        default=SubmissionState.DRAFT,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "assignment", "student_id"],
                name="learning_subm_tenant_assign_student_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_submission_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(state__in=SubmissionState.values),
                name="learning_subm_state_valid",
            ),
        ]
        indexes = [
            models.Index(
                fields=["tenant", "assignment", "state"], name="learn_subm_tenant_asgn_ix"
            ),
            models.Index(
                fields=["tenant", "student_id", "state"], name="learn_subm_tenant_stud_ix"
            ),
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.assignment_id}:{self.student_id}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "Submission id is immutable after creation."})
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="feedbacks")
    mentor_id = models.UUIDField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_feedback_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=~Q(content=""),
                name="learning_feedback_content_nonempty",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "submission"], name="learn_feed_tenant_subm_ix"),
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.submission_id}:{self.mentor_id}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "Feedback id is immutable after creation."})
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class Progress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name="progress_records")
    student_id = models.UUIDField()
    state = models.CharField(
        max_length=16,
        choices=ProgressState.choices,
        default=ProgressState.NOT_STARTED,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "lesson", "student_id"],
                name="learning_prog_tenant_lesson_student_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_prog_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(state__in=ProgressState.values),
                name="learning_prog_state_valid",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "lesson", "state"], name="learn_prog_tenant_les_ix"),
            models.Index(
                fields=["tenant", "student_id", "state"], name="learn_prog_tenant_stud_ix"
            ),
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.lesson_id}:{self.student_id}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError({"id": "Progress id is immutable after creation."})
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id


class MediaFSMState(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    READY = "ready", "Ready"
    QUARANTINED = "quarantined", "Quarantined"


class SyntheticMediaAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="synthetic_media_attachments",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="media_attachments",
    )
    title = models.CharField(max_length=160)
    storage_key = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, default="application/pdf")
    file_size_bytes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    checksum_sha256 = models.CharField(max_length=64)
    state = models.CharField(
        max_length=16,
        choices=MediaFSMState.choices,
        default=MediaFSMState.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_synthetic_media_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "storage_key"],
                name="learning_synthetic_media_tenant_storage_uniq",
            ),
            models.CheckConstraint(
                condition=Q(state__in=MediaFSMState.values),
                name="learning_synthetic_media_state_valid",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_synthetic_media_title_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(storage_key=""),
                name="learning_synthetic_media_storage_key_nonempty",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "lesson", "state"], name="learn_media_tenant_les_ix"),
        ]

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._immutable_original_id = self.id

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.lesson_id}:{self.title}"

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self._state.adding and self.id != self._immutable_original_id:
            raise ValidationError(
                {"id": "SyntheticMediaAttachment id is immutable after creation."}
            )
        self.full_clean()
        super().save(*args, **kwargs)
        self._immutable_original_id = self.id

    def clean(self) -> None:
        super().clean()
        if self.lesson_id and self.tenant_id and self.lesson.tenant_id != self.tenant_id:
            raise ValidationError(
                {"lesson": "Lesson tenant does not match Media Attachment tenant."}
            )
        expected_prefix = f"{self.tenant_id}/media/"
        if not self.storage_key.startswith(expected_prefix):
            raise ValidationError(
                {"storage_key": f"Storage key must be tenant-prefixed with '{expected_prefix}'."}
            )


class CourseProgressAggregate(models.Model):
    """
    Tenant-bounded projection aggregate for course completion metrics.
    Derived state only - never a source of truth.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="course_progress_aggregates",
    )
    student_id = models.UUIDField(db_index=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="progress_aggregates",
    )
    total_lessons = models.PositiveIntegerField(default=0)
    completed_lessons = models.PositiveIntegerField(default=0)
    progress_percentage = models.PositiveIntegerField(default=0)
    last_event_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_cpa_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "course"],
                name="learning_cpa_tenant_student_course_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id"], name="cpa_tenant_student_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.course_id}:{self.progress_percentage}%"


class AssignmentSubmissionMetrics(models.Model):
    """
    Tenant-bounded projection aggregate for mentor review queues and assignment metrics.
    Derived state only.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="assignment_submission_metrics",
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submission_metrics",
    )
    submitted_count = models.PositiveIntegerField(default=0)
    under_review_count = models.PositiveIntegerField(default=0)
    reviewed_count = models.PositiveIntegerField(default=0)
    last_event_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_asm_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "assignment"],
                name="learning_asm_tenant_assignment_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "assignment"], name="asm_tenant_assignment_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.assignment_id}:submitted={self.submitted_count}"


class RoleActivityFeed(models.Model):
    """
    Tenant-bounded append-friendly activity feed projection.
    Strictly Zero-PII: stores only synthetic role identifiers and action metadata.
    """

    class ActivityRole(models.TextChoices):
        STUDENT = "student", "Student"
        MENTOR = "mentor", "Mentor"
        PARENT = "parent", "Parent"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="role_activity_feeds",
    )
    source_event_id = models.UUIDField(db_index=True)
    target_role = models.CharField(max_length=16, choices=ActivityRole.choices)
    user_id = models.UUIDField(db_index=True, null=True, blank=True)
    activity_type = models.CharField(max_length=64)
    summary = models.CharField(max_length=255)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_raf_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "source_event_id", "target_role"],
                name="learning_raf_tenant_source_event_role_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["tenant", "target_role", "user_id"], name="raf_tenant_role_user_ix"
            ),
            models.Index(fields=["tenant", "-occurred_at", "-id"], name="raf_tenant_cursor_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.target_role}:{self.activity_type}"


class ProjectionWatermark(models.Model):
    """
    Tracks processed event sequence/timestamp per tenant and projection to guarantee ordering and idempotency.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="projection_watermarks",
    )
    projection_name = models.CharField(max_length=64)
    last_event_id = models.UUIDField()
    last_occurred_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_pw_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "projection_name"],
                name="learning_pw_tenant_projection_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "projection_name"], name="pw_tenant_proj_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.projection_name}:{self.last_event_id}"


class ProjectionDeadLetterEvent(models.Model):
    """
    Stores poisoned or unprocessable projection events with failure reason for offline debugging and replay.
    Strictly Zero-PII.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="projection_dead_letters",
    )
    event_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=64)
    reason = models.CharField(max_length=255)
    raw_payload_zero_pii = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_dle_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "event_id"],
                name="learning_dle_tenant_event_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "event_type"], name="dle_tenant_type_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:DLQ:{self.event_type}:{self.event_id}"


class NotificationDeliveryState(models.TextChoices):
    PENDING = "pending", "Pending"
    DISPATCHING = "dispatching", "Dispatching"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"


class NotificationItem(models.Model):
    """
    In-app Notification Item for P3-VS3.
    Strictly Zero-PII, multi-tenant with FORCE RLS, role-partitioned, idempotent.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="notification_items",
    )
    user_id = models.UUIDField(db_index=True)
    role = models.CharField(max_length=16, db_index=True)
    title = models.CharField(max_length=160)
    message = models.CharField(max_length=500)
    notification_type = models.CharField(max_length=64, db_index=True)
    state = models.CharField(
        max_length=16,
        choices=NotificationDeliveryState.choices,
        default=NotificationDeliveryState.PENDING,
        db_index=True,
    )
    event_id = models.UUIDField(null=True, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=255, null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    read_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_notification_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="learning_notification_tenant_idemp_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "user_id", "-created_at"], name="notif_tenant_user_created_ix"),
            models.Index(fields=["tenant", "role", "state"], name="notif_tenant_role_state_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.user_id}:{self.notification_type}:{self.state}"


class BadgeDefinition(models.Model):
    """
    Catalog of gamification badges.
    Can be global or tenant-scoped, strictly zero-PII.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    badge_code = models.CharField(max_length=64, unique=True, db_index=True)
    badge_level = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=160)
    description = models.CharField(max_length=255, default="")
    threshold = models.PositiveIntegerField(default=1)
    is_repeatable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["badge_code", "badge_level"],
                name="badge_def_code_level_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.badge_code}:L{self.badge_level}:{self.title}"


class StudentProgressionProfile(models.Model):
    """
    Tenant-bounded progression and daily streak profile.
    Strictly Zero-PII, protected by optimistic locking with version field.
    Day boundary strictly normalized to UTC Midnight.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="student_progression_profiles",
    )
    student_id = models.UUIDField(db_index=True)
    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak_days = models.PositiveIntegerField(default=0)
    last_qualifying_date = models.DateField(null=True, blank=True)
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    completed_lessons_count = models.PositiveIntegerField(default=0)
    reviewed_submissions_count = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_spp_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id"],
                name="learning_spp_tenant_student_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id"], name="spp_tenant_student_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:streak={self.current_streak_days}:xp={self.total_xp}"


class StudentBadgeAward(models.Model):
    """
    Immutable tenant-bounded record of student badge grants.
    Protected by FORCE RLS and idempotency constraints.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="student_badge_awards",
    )
    student_id = models.UUIDField(db_index=True)
    badge = models.ForeignKey(
        BadgeDefinition,
        on_delete=models.PROTECT,
        related_name="awards",
    )
    badge_code = models.CharField(max_length=64, db_index=True)
    badge_level = models.PositiveSmallIntegerField(default=1)
    source_event_id = models.UUIDField(null=True, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=255, null=True, blank=True)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_sba_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "badge_code", "badge_level"],
                name="learning_sba_tenant_student_badge_level_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="learning_sba_tenant_idemp_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "-awarded_at"], name="sba_tenant_stud_award_ix"),
            models.Index(fields=["tenant", "badge_code"], name="sba_tenant_badge_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.badge_code}:L{self.badge_level}"


class Cohort(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="cohorts",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="cohorts",
    )
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    max_capacity = models.PositiveIntegerField(default=30)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "course", "code"],
                name="learning_cohort_tenant_course_code_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "id"],
                name="learning_cohort_tenant_course_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_cohort_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=~Q(code=""),
                name="learning_cohort_code_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_cohort_title_nonempty",
            ),
            models.CheckConstraint(
                condition=Q(max_capacity__gt=0),
                name="learning_cohort_capacity_positive",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course", "is_active"], name="cohort_tenant_course_act_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.course.code}:{self.code}"


class EnrollmentStatus(models.TextChoices):
    ENROLLED = "enrolled", "Enrolled"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    COMPLETED = "completed", "Completed"


class CourseEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    student_id = models.UUIDField(db_index=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=16,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ENROLLED,
    )
    idempotency_key = models.CharField(max_length=255, null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_enrollment_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "course"],
                name="learning_enrollment_tenant_student_course_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="learning_enrollment_tenant_idemp_uniq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=EnrollmentStatus.values),
                name="learning_enrollment_status_valid",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="enroll_tenant_student_st_ix"),
            models.Index(fields=["tenant", "cohort", "status"], name="enroll_tenant_cohort_st_ix"),
            models.Index(fields=["tenant", "course", "status"], name="enroll_tenant_course_st_ix"),
        ]

    def clean(self):
        super().clean()
        if self.cohort is not None:
            if self.cohort.course_id != self.course_id:
                raise ValidationError({"cohort": "Cohort must belong to the selected course."})
            if self.cohort.tenant_id != self.tenant_id:
                raise ValidationError({"cohort": "Cohort tenant must match enrollment tenant."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.course.code}:{self.status}"


class CoursePrerequisite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="course_prerequisites",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="prerequisites",
    )
    prerequisite_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="required_for",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_prereq_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "prerequisite_course"],
                name="learning_prereq_tenant_course_prereq_uniq",
            ),
            models.CheckConstraint(
                condition=~Q(course=models.F("prerequisite_course")),
                name="learning_prereq_no_self_reference",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course"], name="prereq_tenant_course_ix"),
            models.Index(fields=["tenant", "prerequisite_course"], name="prereq_tenant_reqfor_ix"),
        ]

    def clean(self):
        super().clean()
        if self.course_id == self.prerequisite_course_id:
            raise ValidationError({"prerequisite_course": "Course cannot be a prerequisite for itself."})
        if self.course.tenant_id != self.tenant_id or self.prerequisite_course.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between course and prerequisite.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.course.code}<-{self.prerequisite_course.code}"


class CodeAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="code_assessments",
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="code_assessments")
    language = models.CharField(max_length=32, default="python")
    timeout_seconds = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1)])
    memory_limit_mb = models.PositiveIntegerField(default=256, validators=[MinValueValidator(16)])
    starter_code = models.TextField(blank=True, default="")
    testcases = models.JSONField(default=list)
    testcases_hash = models.CharField(max_length=64, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_codeassessment_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "lesson"],
                name="learning_codeassessment_tenant_lesson_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "lesson", "is_active"], name="codeassess_t_les_act_ix"),
        ]

    def clean(self):
        super().clean()
        if self.lesson and self.lesson.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between lesson and code assessment.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.lesson_id}:{self.language}"


class ExecutionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    PASSED = "passed", "Passed"
    FAILED = "failed", "Failed"
    TIMED_OUT = "timed_out", "Timed Out"
    ERROR = "error", "Error"


class CodeExecutionRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="code_execution_runs",
    )
    assessment = models.ForeignKey(
        CodeAssessment,
        on_delete=models.CASCADE,
        related_name="execution_runs",
        null=True,
        blank=True,
    )
    student_id = models.UUIDField(db_index=True)
    attempt_number = models.PositiveIntegerField(default=1)
    submitted_code = models.TextField()
    code_hash = models.CharField(max_length=64, db_index=True)
    runtime_image_hash = models.CharField(max_length=64, default="codesho-python-sandbox:sha256-standard")
    idempotency_key = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING,
        db_index=True,
    )
    duration_ms = models.PositiveIntegerField(default=0)
    memory_used_kb = models.PositiveIntegerField(default=0)
    stdout_log = models.TextField(blank=True, default="")
    stderr_log = models.TextField(blank=True, default="")
    lease_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_coderun_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "assessment", "student_id", "attempt_number"],
                condition=models.Q(assessment__isnull=False),
                name="learning_coderun_attempt_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="learning_coderun_idemp_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="coderun_t_student_st_ix"),
            models.Index(fields=["tenant", "assessment", "status"], name="coderun_t_assess_st_ix"),
            models.Index(fields=["status", "lease_expires_at"], name="coderun_lease_recover_ix"),
        ]

    def clean(self):
        super().clean()
        if self.assessment and self.assessment.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between execution run and assessment.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:attempt_{self.attempt_number}:{self.status}"


class AssessmentResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="assessment_results",
    )
    execution_run = models.OneToOneField(
        CodeExecutionRun,
        on_delete=models.CASCADE,
        related_name="result",
    )
    assessment = models.ForeignKey(
        CodeAssessment,
        on_delete=models.CASCADE,
        related_name="results",
    )
    student_id = models.UUIDField(db_index=True)
    passed_tests_count = models.PositiveIntegerField(default=0)
    total_tests_count = models.PositiveIntegerField(default=0)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_passed = models.BooleanField(default=False)
    is_final = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_assessresult_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "assessment", "student_id"],
                name="learning_assessresult_final_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "is_passed"], name="assessres_t_student_pass_ix"),
        ]

    def clean(self):
        super().clean()
        if self.assessment and self.assessment.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between assessment result and assessment.")
        if self.execution_run and self.execution_run.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between assessment result and execution run.")

    def save(self, *args, **kwargs):
        if not self._state.adding and self.pk:
            raise ValidationError("AssessmentResult is immutable after initial recording.")
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.score}"



class CertificateTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="certificate_templates",
    )
    course = models.ForeignKey(
        "learning.Course",
        on_delete=models.CASCADE,
        related_name="certificate_templates",
    )
    version = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, default="")
    min_score_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=70.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_certtemplate_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "version"],
                name="learning_certtemplate_tenant_course_ver_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course", "is_active"], name="certtmpl_t_course_act_ix"),
        ]

    def clean(self):
        super().clean()
        if self.course and self.course.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between CertificateTemplate and Course.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} (v{self.version})"


class CourseCertificateStatus(models.TextChoices):
    ISSUED = "ISSUED", "Issued"
    REVOKED = "REVOKED", "Revoked"


class CourseCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="issued_certificates",
    )
    course = models.ForeignKey(
        "learning.Course",
        on_delete=models.PROTECT,
        related_name="issued_certificates",
    )
    template = models.ForeignKey(
        CertificateTemplate,
        on_delete=models.PROTECT,
        related_name="issued_certificates",
    )
    student_id = models.UUIDField(db_index=True)
    completion_round = models.PositiveIntegerField(default=1)
    certificate_number = models.CharField(max_length=64, db_index=True)
    verification_hash = models.CharField(max_length=64, db_index=True)
    status = models.CharField(
        max_length=16,
        choices=CourseCertificateStatus.choices,
        default=CourseCertificateStatus.ISSUED,
    )
    final_score = models.DecimalField(max_digits=5, decimal_places=2)
    completion_snapshot = models.JSONField(default=dict)
    source_event_id = models.UUIDField(db_index=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_coursecert_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "student_id", "completion_round"],
                name="learning_coursecert_round_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "certificate_number"],
                name="learning_coursecert_number_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "verification_hash"],
                name="learning_coursecert_hash_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "source_event_id"],
                name="learning_coursecert_source_event_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "student_id"],
                condition=Q(status="ISSUED"),
                name="idx_unique_active_certificate",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="coursecert_t_stu_status_ix"),
            models.Index(fields=["tenant", "certificate_number"], name="coursecert_t_number_ix"),
        ]

    def clean(self):
        super().clean()
        if self.course and self.course.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between CourseCertificate and Course.")
        if self.template and self.template.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between CourseCertificate and CertificateTemplate.")
        if self.template and self.course and self.template.course_id != self.course_id:
            raise ValidationError("CourseCertificate template does not belong to specified course.")

    def save(self, *args, **kwargs):
        if not self._state.adding and self.pk:
            orig = CourseCertificate.objects.filter(pk=self.pk).values(
                "course_id", "template_id", "student_id", "certificate_number",
                "verification_hash", "final_score", "source_event_id", "issued_at"
            ).first()
            if orig:
                if (
                    orig["course_id"] != self.course_id or
                    orig["template_id"] != self.template_id or
                    orig["student_id"] != self.student_id or
                    orig["certificate_number"] != self.certificate_number or
                    orig["verification_hash"] != self.verification_hash or
                    orig["final_score"] != self.final_score or
                    orig["source_event_id"] != self.source_event_id
                ):
                    raise ValidationError("Core certificate issuance fields are strictly immutable.")
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.certificate_number} ({self.status})"


class CertificateVerificationRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="certificate_verification_records",
    )
    certificate = models.ForeignKey(
        CourseCertificate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="verification_records",
    )
    queried_number = models.CharField(max_length=64, db_index=True)
    result_status = models.CharField(max_length=16)  # VALID, REVOKED, NOT_FOUND, INVALID_HASH
    queried_by_role = models.CharField(max_length=16, default="anonymous")
    queried_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_certverif_tenant_id_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "queried_number", "queried_at"], name="certverif_t_num_date_ix"),
        ]

    def clean(self):
        super().clean()
        if self.certificate and self.certificate.tenant_id != self.tenant_id:
            raise ValidationError("Tenant mismatch between CertificateVerificationRecord and CourseCertificate.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.queried_number}:{self.result_status}"


class CohortSupervision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="cohort_supervisions",
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        related_name="supervisors",
    )
    mentor_id = models.UUIDField(db_index=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.UUIDField(null=True, blank=True)
    is_lead = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.UUIDField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_cohortsupervision_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "cohort", "mentor_id"],
                condition=Q(is_active=True),
                name="learning_cohortsupervision_active_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "cohort"],
                condition=Q(is_active=True, is_lead=True),
                name="learning_cohortsupervision_single_lead_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "mentor_id", "is_active"], name="cohortsup_t_men_act_ix"),
        ]

    def clean(self):
        super().clean()
        if self.cohort and str(self.cohort.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between CohortSupervision and Cohort.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_id}:{self.mentor_id}:lead={self.is_lead}"


class CohortProgressAggregate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="cohort_progress_aggregates",
    )
    cohort = models.OneToOneField(
        Cohort,
        on_delete=models.CASCADE,
        related_name="analytics_aggregate",
    )
    total_enrolled = models.PositiveIntegerField(default=0)
    active_students = models.PositiveIntegerField(default=0)
    completed_students = models.PositiveIntegerField(default=0)
    average_progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_assessment_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_cohortprogaggregate_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "cohort"],
                name="learning_cohortprogaggregate_tenant_cohort_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "cohort"], name="cohortprog_t_coh_ix"),
        ]

    def clean(self):
        super().clean()
        if self.cohort and str(self.cohort.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between CohortProgressAggregate and Cohort.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_id}:avg={self.average_progress_percentage}%"


class StudentSupervisionAlertStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
    RESOLVED = "RESOLVED", "Resolved"


class StudentSupervisionAlertType(models.TextChoices):
    STALLED_PROGRESS = "STALLED_PROGRESS", "Stalled Progress"
    FAILED_ASSESSMENTS = "FAILED_ASSESSMENTS", "Failed Assessments"
    AT_RISK_DROPOUT = "AT_RISK_DROPOUT", "At Risk Dropout"


class StudentSupervisionAlertSeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"


class StudentSupervisionAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="student_supervision_alerts",
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    student_id = models.UUIDField(db_index=True)
    alert_type = models.CharField(
        max_length=32,
        choices=StudentSupervisionAlertType.choices,
    )
    severity = models.CharField(
        max_length=16,
        choices=StudentSupervisionAlertSeverity.choices,
    )
    status = models.CharField(
        max_length=16,
        choices=StudentSupervisionAlertStatus.choices,
        default=StudentSupervisionAlertStatus.ACTIVE,
        db_index=True,
    )
    rule_version = models.PositiveIntegerField(default=1)
    deduplication_key = models.CharField(max_length=255, unique=True, db_index=True)
    details = models.JSONField(default=dict)
    schema_version = models.PositiveIntegerField(default=1)
    data_classification = models.CharField(max_length=32, default="INTERNAL_EDUCATIONAL_ANALYTICS")
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.UUIDField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_studentsupalert_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "cohort", "student_id", "alert_type"],
                condition=Q(status="ACTIVE"),
                name="learning_supalert_active_dedup_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "cohort", "status", "resolved_at"], name="supalert_t_c_st_res_ix"),
            models.Index(fields=["tenant", "student_id", "status"], name="supalert_t_stu_st_ix"),
        ]

    def clean(self):
        super().clean()
        if self.cohort and str(self.cohort.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between StudentSupervisionAlert and Cohort.")
        if self.status == StudentSupervisionAlertStatus.ACKNOWLEDGED:
            if not self.acknowledged_at or not self.acknowledged_by:
                raise ValidationError("Acknowledged alerts require acknowledged_at and acknowledged_by.")
        if self.status == StudentSupervisionAlertStatus.RESOLVED:
            if not self.resolved_at:
                raise ValidationError("Resolved alerts require resolved_at timestamp.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_id}:{self.student_id}:{self.alert_type}:{self.status}"


class DiscussionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending Moderation"
    APPROVED = "APPROVED", "Approved"
    FLAGGED = "FLAGGED", "Flagged"
    REMOVED = "REMOVED", "Removed"


class ModerationActionType(models.TextChoices):
    APPROVE = "APPROVE", "Approve Content"
    FLAG = "FLAG", "Flag Content"
    REMOVE = "REMOVE", "Remove Content"
    RESTORE = "RESTORE", "Restore Content"


class DiscussionThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="discussion_threads",
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="discussion_threads",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="discussion_threads",
    )
    author_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=DiscussionStatus.choices,
        default=DiscussionStatus.PENDING,
        db_index=True,
    )
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    replies_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_discussionthread_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(cohort__isnull=False) & Q(lesson__isnull=True))
                    | (Q(cohort__isnull=True) & Q(lesson__isnull=False))
                ),
                name="learning_thread_single_scope_xor",
            ),
            models.CheckConstraint(
                condition=Q(status__in=DiscussionStatus.values),
                name="learning_thread_status_valid",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="learning_thread_title_nonempty",
            ),
            models.CheckConstraint(
                condition=~Q(body=""),
                name="learning_thread_body_nonempty",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "cohort", "status"], name="thread_t_coh_st_ix"),
            models.Index(fields=["tenant", "lesson", "status"], name="thread_t_les_st_ix"),
            models.Index(fields=["tenant", "author_id", "status"], name="thread_t_auth_st_ix"),
        ]

    def clean(self):
        super().clean()
        if bool(self.cohort_id) == bool(self.lesson_id):
            raise ValidationError("Thread must be associated with exactly one of Cohort or Lesson (DB XOR).")
        if self.cohort and str(self.cohort.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between Thread and Cohort.")
        if self.lesson and str(self.lesson.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between Thread and Lesson.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.id}:{self.status}:{self.title[:30]}"


class DiscussionComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="discussion_comments",
    )
    thread = models.ForeignKey(
        DiscussionThread,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    author_id = models.UUIDField(db_index=True)
    body = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=DiscussionStatus.choices,
        default=DiscussionStatus.PENDING,
        db_index=True,
    )
    is_mentor_endorsed = models.BooleanField(default=False)
    endorsed_by_id = models.UUIDField(null=True, blank=True)
    endorsed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_discussioncomment_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "id", "thread"],
                name="learning_comment_tenant_id_thread_uniq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=DiscussionStatus.values),
                name="learning_comment_status_valid",
            ),
            models.CheckConstraint(
                condition=~Q(body=""),
                name="learning_comment_body_nonempty",
            ),
            models.CheckConstraint(
                condition=Q(parent__isnull=True) | ~Q(parent=models.F("id")),
                name="learning_comment_prevent_self_parent",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "thread", "status"], name="comment_t_th_st_ix"),
            models.Index(fields=["tenant", "parent", "status"], name="comment_t_pr_st_ix"),
            models.Index(fields=["tenant", "author_id", "status"], name="comment_t_auth_st_ix"),
        ]

    def clean(self):
        super().clean()
        if self.thread and str(self.thread.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between Comment and Thread.")
        if self.parent_id:
            if self.parent_id == self.id:
                raise ValidationError("Comment cannot be its own parent.")
            if self.parent:
                if str(self.parent.tenant_id) != str(self.tenant_id):
                    raise ValidationError("Tenant mismatch between Comment and Parent Comment.")
                if self.parent.thread_id != self.thread_id:
                    raise ValidationError("Parent comment must belong to the exact same thread.")
        if self.is_mentor_endorsed and not self.endorsed_by_id:
            raise ValidationError("Endorsed comment must record endorsed_by_id.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.thread_id}:{self.id}:{self.status}"


class DiscussionModerationAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="discussion_moderation_actions",
    )
    target_thread = models.ForeignKey(
        DiscussionThread,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="moderation_actions",
    )
    target_comment = models.ForeignKey(
        DiscussionComment,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="moderation_actions",
    )
    action = models.CharField(max_length=16, choices=ModerationActionType.choices)
    previous_status = models.CharField(max_length=16, choices=DiscussionStatus.choices, null=True, blank=True)
    new_status = models.CharField(max_length=16, choices=DiscussionStatus.choices)
    performed_by = models.UUIDField(db_index=True)
    reason = models.CharField(max_length=255)
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_moderationaction_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(target_thread__isnull=False) & Q(target_comment__isnull=True))
                    | (Q(target_thread__isnull=True) & Q(target_comment__isnull=False))
                ),
                name="learning_modaction_target_xor",
            ),
            models.CheckConstraint(
                condition=Q(action__in=ModerationActionType.values),
                name="learning_modaction_action_valid",
            ),
            models.CheckConstraint(
                condition=Q(new_status__in=DiscussionStatus.values),
                name="learning_modaction_new_status_valid",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "target_thread", "created_at"], name="modaction_t_th_cr_ix"),
            models.Index(fields=["tenant", "target_comment", "created_at"], name="modaction_t_cm_cr_ix"),
            models.Index(fields=["tenant", "performed_by", "created_at"], name="modaction_t_perf_cr_ix"),
        ]

    def clean(self):
        super().clean()
        if bool(self.target_thread_id) == bool(self.target_comment_id):
            raise ValidationError("Moderation action must target exactly one of thread or comment.")
        if self.target_thread and str(self.target_thread.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between ModerationAction and TargetThread.")
        if self.target_comment and str(self.target_comment.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between ModerationAction and TargetComment.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("DiscussionModerationAction is append-only and cannot be modified.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("DiscussionModerationAction records are immutable audit logs and cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.action}:{self.performed_by}:{self.created_at}"

