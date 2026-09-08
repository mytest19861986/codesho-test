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
