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


# =============================================================================
# Phase 3 VS11: Adaptive Progression and Personalization Engine Models
# =============================================================================

class SkillCategory(models.TextChoices):
    ALGORITHMS = "ALGORITHMS", "Algorithms"
    SYNTAX = "SYNTAX", "Syntax & Core"
    DATA_STRUCTURES = "DATA_STRUCTURES", "Data Structures"
    OOP = "OOP", "Object Oriented Programming"
    PROBLEM_SOLVING = "PROBLEM_SOLVING", "Problem Solving"


class MasteryLevel(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not Started"
    BEGINNER = "BEGINNER", "Beginner"
    DEVELOPING = "DEVELOPING", "Developing"
    PROFICIENT = "PROFICIENT", "Proficient"
    MASTERED = "MASTERED", "Mastered"


class RecommendationType(models.TextChoices):
    REMEDIAL_PRACTICE = "REMEDIAL_PRACTICE", "Remedial Practice"
    NEXT_CHALLENGE = "NEXT_CHALLENGE", "Next Milestone Challenge"
    SKILL_EXPANSION = "SKILL_EXPANSION", "Skill Expansion"
    REVISION = "REVISION", "Spaced Revision"


class RecommendationStatus(models.TextChoices):
    GENERATED = "GENERATED", "Generated"
    VIEWED = "VIEWED", "Viewed"
    ACCEPTED = "ACCEPTED", "Accepted"
    COMPLETED = "COMPLETED", "Completed"
    DISMISSED = "DISMISSED", "Dismissed"
    SUPERSEDED = "SUPERSEDED", "Superseded"


class TransitionActorType(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    SYSTEM = "SYSTEM", "System Worker"
    STAFF = "STAFF", "Staff/Mentor"


class SkillDefinition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="skill_definitions",
    )
    slug = models.SlugField(max_length=64)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=64, choices=SkillCategory.choices)
    difficulty_level = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_skilldefinition_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "slug"],
                name="learning_skilldefinition_tenant_slug_uniq",
            ),
            models.CheckConstraint(
                condition=Q(difficulty_level__gte=1) & Q(difficulty_level__lte=5),
                name="learning_skill_difficulty_range",
            ),
            models.CheckConstraint(
                condition=~Q(slug=""),
                name="learning_skill_slug_nonempty",
            ),
            models.CheckConstraint(
                condition=Q(category__in=SkillCategory.values),
                name="learning_skill_category_valid",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "category", "is_active"], name="skill_t_cat_act_ix"),
        ]

    def clean(self):
        super().clean()
        if len(self.slug) < 3:
            raise ValidationError("Skill slug must be at least 3 characters.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.slug}"


class SkillDependency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="skill_dependencies",
    )
    source_skill = models.ForeignKey(
        SkillDefinition,
        on_delete=models.CASCADE,
        related_name="prerequisites",
    )
    target_skill = models.ForeignKey(
        SkillDefinition,
        on_delete=models.CASCADE,
        related_name="dependents",
    )
    is_strict = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_skilldependency_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "source_skill", "target_skill"],
                name="learning_skilldependency_edge_uniq",
            ),
            models.CheckConstraint(
                condition=~Q(source_skill=models.F("target_skill")),
                name="learning_skill_no_self_dependency",
            ),
        ]

    def clean(self):
        super().clean()
        if self.source_skill_id == self.target_skill_id:
            raise ValidationError("Skill cannot depend on itself.")
        if self.source_skill and str(self.source_skill.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between dependency and source skill.")
        if self.target_skill and str(self.target_skill.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between dependency and target skill.")
        if self.source_skill and not self.source_skill.is_active:
            raise ValidationError("Cannot establish dependency with inactive source skill.")
        if self.target_skill and not self.target_skill.is_active:
            raise ValidationError("Cannot establish dependency with inactive target skill.")

        # In-memory application cycle check
        visited = set()
        queue = [self.target_skill_id]
        while queue:
            curr = queue.pop(0)
            if curr == self.source_skill_id:
                raise ValidationError("Cycle detected in skill dependency graph.")
            if curr not in visited:
                visited.add(curr)
                dependents = SkillDependency.objects.filter(
                    tenant_id=self.tenant_id,
                    source_skill_id=curr,
                ).values_list("target_skill_id", flat=True)
                queue.extend(dependents)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.source_skill_id}->{self.target_skill_id}"


class LessonSkillMapping(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="lesson_skill_mappings",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="skill_mappings",
    )
    skill = models.ForeignKey(
        SkillDefinition,
        on_delete=models.CASCADE,
        related_name="lesson_mappings",
    )
    mastery_weight = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_lessonskill_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "lesson", "skill"],
                name="learning_lessonskill_lesson_skill_uniq",
            ),
            models.CheckConstraint(
                condition=Q(mastery_weight__gt=0.00) & Q(mastery_weight__lte=1.00),
                name="learning_lessonskill_weight_range",
            ),
        ]

    def clean(self):
        super().clean()
        if self.lesson and str(self.lesson.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between LessonSkillMapping and Lesson.")
        if self.skill and str(self.skill.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between LessonSkillMapping and SkillDefinition.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.lesson_id}:{self.skill_id}"


class ProcessedLearningEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="processed_learning_events",
    )
    event_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=64)
    student_id = models.UUIDField(db_index=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_proc_event_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "event_id", "event_type"],
                name="learning_proc_event_id_type_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "processed_at"], name="proc_event_t_st_pr_ix"),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("ProcessedLearningEvent is append-only.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("ProcessedLearningEvent records are immutable.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.event_type}:{self.event_id}"


class StudentSkillProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="student_skill_progresses",
    )
    student_id = models.UUIDField(db_index=True)
    skill = models.ForeignKey(
        SkillDefinition,
        on_delete=models.CASCADE,
        related_name="student_progresses",
    )
    mastery_level = models.CharField(
        max_length=16,
        choices=MasteryLevel.choices,
        default=MasteryLevel.NOT_STARTED,
    )
    mastery_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    practice_count = models.PositiveIntegerField(default=0)
    last_evaluated_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_studentskill_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "skill"],
                name="learning_studentskill_student_skill_uniq",
            ),
            models.CheckConstraint(
                condition=Q(mastery_score__gte=0.00) & Q(mastery_score__lte=100.00),
                name="learning_studentskill_score_range",
            ),
            models.CheckConstraint(
                condition=Q(mastery_level__in=MasteryLevel.values),
                name="learning_studentskill_level_valid",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "mastery_level"], name="studentskill_t_st_lvl_ix"),
        ]

    def clean(self):
        super().clean()
        if self.skill and str(self.skill.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between StudentSkillProgress and SkillDefinition.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.skill_id}:{self.mastery_level}"


class StudentLearningProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="student_learning_profiles",
    )
    student_id = models.UUIDField(db_index=True)
    total_skills_tracked = models.PositiveIntegerField(default=0)
    mastered_skills_count = models.PositiveIntegerField(default=0)
    developing_skills_count = models.PositiveIntegerField(default=0)
    overall_competency_index = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    identified_learning_gaps = models.JSONField(default=list)
    last_rebuilt_at = models.DateTimeField()
    rebuild_version = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_learningprofile_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id"],
                name="learning_learningprofile_student_uniq",
            ),
            models.CheckConstraint(
                condition=Q(overall_competency_index__gte=0.00) & Q(overall_competency_index__lte=100.00),
                name="learning_profile_competency_range",
            ),
            models.CheckConstraint(
                condition=Q(total_skills_tracked__gte=models.F("mastered_skills_count"))
                & Q(total_skills_tracked__gte=models.F("developing_skills_count")),
                name="learning_profile_counts_consistent",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:v{self.rebuild_version}"


class LearningRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_recommendations",
    )
    student_id = models.UUIDField(db_index=True)
    target_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommendations",
    )
    target_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommendations",
    )
    target_skill = models.ForeignKey(
        SkillDefinition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommendations",
    )
    recommendation_type = models.CharField(max_length=32, choices=RecommendationType.choices)
    status = models.CharField(
        max_length=16,
        choices=RecommendationStatus.choices,
        default=RecommendationStatus.GENERATED,
    )
    priority = models.PositiveSmallIntegerField(default=1)
    recommendation_reason = models.CharField(max_length=500)
    evidence_context = models.JSONField(default=dict)
    idempotency_key = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_recommendation_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                name="learning_recommendation_idempotency_uniq",
            ),
            models.CheckConstraint(
                condition=Q(priority__gte=1) & Q(priority__lte=5),
                name="learning_rec_priority_range",
            ),
            models.CheckConstraint(
                condition=Q(recommendation_type__in=RecommendationType.values),
                name="learning_rec_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(status__in=RecommendationStatus.values),
                name="learning_rec_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(target_course__isnull=False) & Q(target_lesson__isnull=True) & Q(target_skill__isnull=True))
                    | (Q(target_course__isnull=True) & Q(target_lesson__isnull=False) & Q(target_skill__isnull=True))
                    | (Q(target_course__isnull=True) & Q(target_lesson__isnull=True) & Q(target_skill__isnull=False))
                ),
                name="learning_rec_target_single_choice",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="rec_t_st_stat_ix"),
        ]

    def clean(self):
        super().clean()
        targets = [self.target_course_id, self.target_lesson_id, self.target_skill_id]
        if sum(1 for t in targets if t is not None) != 1:
            raise ValidationError("Recommendation must target exactly one of course, lesson, or skill.")
        if len(self.recommendation_reason.strip()) < 10:
            raise ValidationError("Recommendation reason must be at least 10 characters.")
        if not self.evidence_context or self.evidence_context == {}:
            raise ValidationError("Evidence context cannot be empty (Explainability First).")
        if self.target_course and str(self.target_course.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between LearningRecommendation and TargetCourse.")
        if self.target_lesson and str(self.target_lesson.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between LearningRecommendation and TargetLesson.")
        if self.target_skill and str(self.target_skill.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between LearningRecommendation and TargetSkill.")
        if self.target_skill and not self.target_skill.is_active:
            raise ValidationError("Cannot generate recommendation for inactive target skill.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.recommendation_type}:{self.status}"


class RecommendationTransitionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="recommendation_transition_logs",
    )
    recommendation = models.ForeignKey(
        LearningRecommendation,
        on_delete=models.CASCADE,
        related_name="transition_logs",
    )
    from_status = models.CharField(max_length=16)
    to_status = models.CharField(max_length=16)
    actor_id = models.UUIDField(db_index=True)
    actor_type = models.CharField(max_length=16, choices=TransitionActorType.choices)
    transition_reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_rec_trans_log_tenant_id_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "recommendation", "created_at"], name="rec_log_t_rec_cr_ix"),
        ]

    def clean(self):
        super().clean()
        if self.recommendation and str(self.recommendation.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between RecommendationTransitionLog and Recommendation.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("RecommendationTransitionLog is append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("RecommendationTransitionLog records are immutable audit logs and cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.recommendation_id}:{self.from_status}->{self.to_status}"


class PortfolioVisibility(models.TextChoices):
    PRIVATE = "PRIVATE", "Private"
    GUARDIAN_SHARED = "GUARDIAN_SHARED", "Guardian Shared"
    TENANT_PUBLIC = "TENANT_PUBLIC", "Tenant Public"


class PortfolioModerationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    FLAGGED = "FLAGGED", "Flagged"
    REMOVED = "REMOVED", "Removed"


class ArtifactType(models.TextChoices):
    PROJECT_CODE = "PROJECT_CODE", "Project Code"
    CAPSTONE_SUBMISSION = "CAPSTONE_SUBMISSION", "Capstone Submission"
    CERTIFICATE = "CERTIFICATE", "Certificate"
    BADGE_HIGHLIGHT = "BADGE_HIGHLIGHT", "Badge Highlight"


class ModerationActionType(models.TextChoices):
    APPROVE = "APPROVE", "Approve"
    UNFLAG = "UNFLAG", "Unflag"
    FLAG = "FLAG", "Flag"
    REMOVE = "REMOVE", "Remove"
    RESTORE = "RESTORE", "Restore"
    CONSENT_GRANT = "CONSENT_GRANT", "Consent Grant"
    CONSENT_REVOKE = "CONSENT_REVOKE", "Consent Revoke"


class LearningPortfolio(models.Model):
    """
    P3-VS12: Student learning portfolio root entity.
    Enforces storytelling over ranking, fail-closed child privacy, and showcase consent gates.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_portfolios",
    )
    student_id = models.UUIDField(db_index=True)
    headline = models.CharField(max_length=200)
    summary_narrative = models.TextField(blank=True, default="")
    featured_artifact_count = models.SmallIntegerField(default=0)
    visibility = models.CharField(
        max_length=20,
        choices=PortfolioVisibility.choices,
        default=PortfolioVisibility.PRIVATE,
    )
    moderation_status = models.CharField(
        max_length=20,
        choices=PortfolioModerationStatus.choices,
        default=PortfolioModerationStatus.PENDING,
    )
    public_consent_active = models.BooleanField(default=False)
    public_consent_by = models.UUIDField(null=True, blank=True)
    public_consent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant", "id"], name="portfolio_tenant_id_uniq"),
            models.UniqueConstraint(fields=["tenant", "student_id"], name="portfolio_tenant_student_uniq"),
            models.CheckConstraint(
                condition=Q(visibility__in=PortfolioVisibility.values),
                name="portfolio_visibility_check",
            ),
            models.CheckConstraint(
                condition=Q(moderation_status__in=PortfolioModerationStatus.values),
                name="portfolio_moderation_check",
            ),
            models.CheckConstraint(
                condition=models.Q(featured_artifact_count__gte=0),
                name="portfolio_featured_count_check",
            ),
            models.CheckConstraint(
                condition=~Q(visibility="TENANT_PUBLIC") | (Q(moderation_status="APPROVED") & Q(public_consent_active=True)),
                name="portfolio_public_guard",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "visibility", "moderation_status"], name="idx_portfolio_showcase"),
        ]

    def clean(self):
        super().clean()
        if len(self.headline.strip()) < 5:
            raise ValidationError({"headline": "Headline must be at least 5 characters."})
        if self.visibility == PortfolioVisibility.TENANT_PUBLIC:
            if self.moderation_status != PortfolioModerationStatus.APPROVED or not self.public_consent_active:
                raise ValidationError("Showcase publication requires APPROVED moderation status and active consent.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.headline[:30]}"


class AchievementArtifact(models.Model):
    """
    P3-VS12: Verifiable educational artifact anchoring student achievements to evidence.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="achievement_artifacts",
    )
    portfolio = models.ForeignKey(
        LearningPortfolio,
        on_delete=models.CASCADE,
        related_name="artifacts",
    )
    artifact_type = models.CharField(max_length=32, choices=ArtifactType.choices)
    title = models.CharField(max_length=160)
    reflection_notes = models.TextField(blank=True, default="")
    mentor_endorsement = models.TextField(blank=True, default="")
    mentor_user_id = models.UUIDField(null=True, blank=True)
    source_submission = models.ForeignKey(
        "learning.Submission",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="achievement_artifacts",
    )
    source_certificate = models.ForeignKey(
        "learning.CourseCertificate",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="achievement_artifacts",
    )
    moderation_status = models.CharField(
        max_length=20,
        choices=PortfolioModerationStatus.choices,
        default=PortfolioModerationStatus.PENDING,
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant", "id"], name="artifact_tenant_id_uniq"),
            models.CheckConstraint(
                condition=Q(artifact_type__in=ArtifactType.values),
                name="artifact_type_check",
            ),
            models.CheckConstraint(
                condition=Q(moderation_status__in=PortfolioModerationStatus.values),
                name="artifact_moderation_check",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "portfolio", "is_featured"], name="idx_artifact_portfolio"),
        ]

    def clean(self):
        super().clean()
        if len(self.title.strip()) < 3:
            raise ValidationError({"title": "Title must be at least 3 characters."})
        if self.portfolio and str(self.portfolio.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between AchievementArtifact and LearningPortfolio.")
        if self.source_submission and self.source_certificate:
            raise ValidationError("Artifact cannot be simultaneously linked to submission and certificate.")
        if self.artifact_type == ArtifactType.CAPSTONE_SUBMISSION and not self.source_submission:
            raise ValidationError({"source_submission": "CAPSTONE_SUBMISSION requires a valid source submission."})
        if self.artifact_type == ArtifactType.CERTIFICATE and not self.source_certificate:
            raise ValidationError({"source_certificate": "CERTIFICATE requires a valid source certificate."})
        if self.source_submission and str(self.source_submission.tenant_id) != str(self.tenant_id):
            raise ValidationError("Cross-tenant source submission link rejected.")
        if self.source_certificate and str(self.source_certificate.tenant_id) != str(self.tenant_id):
            raise ValidationError("Cross-tenant source certificate link rejected.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.portfolio_id}:{self.title}"


class StudentJourneyTimeline(models.Model):
    """
    P3-VS12: Chronological student educational journey narrative milestones.
    Guarantees Zero PII in metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="journey_timelines",
    )
    student_id = models.UUIDField(db_index=True)
    event_key = models.CharField(max_length=64)
    event_title = models.CharField(max_length=160)
    narrative_description = models.TextField()
    milestone_date = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant", "id"], name="timeline_tenant_id_uniq"),
            models.UniqueConstraint(fields=["tenant", "student_id", "event_key"], name="timeline_tenant_event_uniq"),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "milestone_date"], name="idx_timeline_chronological"),
        ]

    def clean(self):
        super().clean()
        if len(self.event_title.strip()) < 3:
            raise ValidationError({"event_title": "Event title must be at least 3 characters."})
        if len(self.narrative_description.strip()) < 10:
            raise ValidationError({"narrative_description": "Narrative description must be at least 10 characters."})
        forbidden_pii = {'name', 'phone', 'email', 'avatar_url', 'national_id', 'location'}
        if isinstance(self.metadata, dict):
            found_pii = forbidden_pii.intersection(self.metadata.keys())
            if found_pii:
                raise ValidationError({"metadata": f"PII keys forbidden in journey timeline metadata: {found_pii}"})

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.event_key}"


class PortfolioModerationAction(models.Model):
    """
    P3-VS12: Append-only audit ledger for content moderation and showcase consent events.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="portfolio_moderation_actions",
    )
    target_portfolio = models.ForeignKey(
        LearningPortfolio,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="moderation_actions",
    )
    target_artifact = models.ForeignKey(
        AchievementArtifact,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="moderation_actions",
    )
    actor_id = models.UUIDField(db_index=True)
    action_type = models.CharField(max_length=32, choices=ModerationActionType.choices)
    reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(action_type__in=ModerationActionType.values),
                name="modaction_action_type_check",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "target_portfolio"], name="idx_modaction_target_port"),
            models.Index(fields=["tenant", "target_artifact"], name="idx_modaction_target_art"),
        ]

    def clean(self):
        super().clean()
        if (self.target_portfolio is None and self.target_artifact is None) or (self.target_portfolio and self.target_artifact):
            raise ValidationError("Moderation action must target exactly one of portfolio or artifact.")
        if self.target_portfolio and str(self.target_portfolio.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between moderation action and target portfolio.")
        if self.target_artifact and str(self.target_artifact.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between moderation action and target artifact.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("PortfolioModerationAction is append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("PortfolioModerationAction records are immutable audit logs and cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.action_type}:{self.actor_id}"


# =============================================================================
# P3-VS13: Longitudinal Learning Intelligence & Growth Models
# =============================================================================

class CalculationRunStatus(models.TextChoices):
    RUNNING = "RUNNING", "Running"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class GrowthMetricKey(models.TextChoices):
    CODING_VELOCITY = "CODING_VELOCITY", "Coding Velocity"
    CONCEPT_MASTERY = "CONCEPT_MASTERY", "Concept Mastery"
    PROBLEM_SOLVING = "PROBLEM_SOLVING", "Problem Solving"
    PERSISTENCE = "PERSISTENCE", "Persistence"
    CODE_QUALITY = "CODE_QUALITY", "Code Quality"


class TrendDirection(models.TextChoices):
    ACCELERATING = "ACCELERATING", "Accelerating"
    STEADY = "STEADY", "Steady"
    DEVELOPING = "DEVELOPING", "Developing"
    NEEDS_SUPPORT = "NEEDS_SUPPORT", "Needs Support"


class MilestoneStatus(models.TextChoices):
    ACHIEVED = "ACHIEVED", "Achieved"
    RETRACTED = "RETRACTED", "Retracted"


class InsightType(models.TextChoices):
    COMPETENCY_GROWTH = "COMPETENCY_GROWTH", "Competency Growth"
    STRENGTH_AREA = "STRENGTH_AREA", "Strength Area"
    MOMENTUM_STREAK = "MOMENTUM_STREAK", "Momentum Streak"
    FOCUS_RECOMMENDATION = "FOCUS_RECOMMENDATION", "Focus Recommendation"
    MASTERY_MILESTONE = "MASTERY_MILESTONE", "Mastery Milestone"


class ConfidenceLevel(models.TextChoices):
    HIGH = "HIGH", "High"
    MEDIUM = "MEDIUM", "Medium"
    LOW = "LOW", "Low"


class InsightLifecycleStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    SUPERSEDED = "SUPERSEDED", "Superseded"
    RETRACTED = "RETRACTED", "Retracted"


class GenerationEventStatus(models.TextChoices):
    PROCESSED = "PROCESSED", "Processed"
    REJECTED = "REJECTED", "Rejected"
    FAILED = "FAILED", "Failed"


class CalculationRun(models.Model):
    """
    Formal registry anchoring calculation runs to tenant and trigger actor.
    Enforces referential integrity across all derived projections.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_calculation_runs",
    )
    triggered_by = models.UUIDField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=CalculationRunStatus.choices,
        default=CalculationRunStatus.RUNNING,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_calcrun_tenant_id_uniq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=CalculationRunStatus.values),
                name="learning_calcrun_status_check",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status__in=["COMPLETED", "FAILED"]) & Q(completed_at__isnull=False)) |
                    (Q(status="RUNNING") & Q(completed_at__isnull=True))
                ),
                name="learning_calcrun_completion_check",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "started_at"], name="idx_calcrun_tenant_started"),
            models.Index(fields=["tenant", "triggered_by"], name="idx_calcrun_tenant_trigger"),
        ]

    def clean(self):
        super().clean()
        if self.status in [CalculationRunStatus.COMPLETED, CalculationRunStatus.FAILED] and not self.completed_at:
            raise ValidationError("Completed/Failed calculation runs must have completed_at timestamp.")
        if self.status == CalculationRunStatus.RUNNING and self.completed_at:
            raise ValidationError("Running calculation runs cannot have a completed_at timestamp.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.id}:{self.status}"


class GrowthMetricSnapshot(models.Model):
    """
    Point-in-time snapshot of student growth across defined competencies.
    Append-Only projection per daily snapshot date.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_metric_snapshots",
    )
    student_id = models.UUIDField(db_index=True)
    metric_key = models.CharField(max_length=64, choices=GrowthMetricKey.choices)
    metric_value = models.DecimalField(max_digits=8, decimal_places=2)
    baseline_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    growth_delta = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    calculation_run = models.ForeignKey(
        CalculationRun,
        on_delete=models.RESTRICT,
        related_name="metric_snapshots",
    )
    snapshot_date = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_metric_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "metric_key", "snapshot_date"],
                name="learning_metric_daily_student_uniq",
            ),
            models.CheckConstraint(
                condition=Q(metric_key__in=GrowthMetricKey.values),
                name="learning_metric_key_check",
            ),
            models.CheckConstraint(
                condition=Q(metric_value__gte=0.00) & Q(metric_value__lte=1000.00),
                name="learning_metric_value_range",
            ),
            models.CheckConstraint(
                condition=Q(baseline_value__isnull=True) | (Q(baseline_value__gte=0.00) & Q(baseline_value__lte=1000.00)),
                name="learning_metric_baseline_range",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "metric_key", "snapshot_date"], name="idx_growth_metric_timeline"),
        ]

    def clean(self):
        super().clean()
        if str(self.calculation_run.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between metric snapshot and calculation run.")
        if self.baseline_value is not None:
            self.growth_delta = self.metric_value - self.baseline_value
        else:
            self.growth_delta = 0.00
        # PII Scrubbing check
        pii_keys = {"name", "phone", "email", "national_id", "location", "avatar_url"}
        if any(k in self.metadata for k in pii_keys):
            raise ValidationError("Metadata contains prohibited PII fields.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.metric_key}:{self.snapshot_date}"


class StudentGrowthTrend(models.Model):
    """
    Current consolidated competency vectors and longitudinal trajectory.
    Mutable-Latest projection updated during recalculation runs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_growth_trends",
    )
    student_id = models.UUIDField(db_index=True)
    competency_domain = models.CharField(max_length=64)
    trend_direction = models.CharField(
        max_length=32,
        choices=TrendDirection.choices,
        default=TrendDirection.DEVELOPING,
    )
    current_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    velocity_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_milestones_achieved = models.IntegerField(default=0)
    competency_vectors = models.JSONField(default=dict, blank=True)
    calculation_run = models.ForeignKey(
        CalculationRun,
        on_delete=models.RESTRICT,
        related_name="growth_trends",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_trend_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "competency_domain"],
                name="learning_trend_domain_uniq",
            ),
            models.CheckConstraint(
                condition=Q(trend_direction__in=TrendDirection.values),
                name="learning_trend_direction_check",
            ),
            models.CheckConstraint(
                condition=Q(current_score__gte=0.00) & Q(current_score__lte=100.00),
                name="learning_trend_score_range",
            ),
            models.CheckConstraint(
                condition=Q(velocity_rate__gte=-100.00) & Q(velocity_rate__lte=100.00),
                name="learning_trend_velocity_range",
            ),
            models.CheckConstraint(
                condition=Q(total_milestones_achieved__gte=0),
                name="learning_trend_milestones_non_negative",
            ),
        ]

    def clean(self):
        super().clean()
        if str(self.calculation_run.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between growth trend and calculation run.")
        pii_keys = {"name", "phone", "email", "national_id", "location", "avatar_url"}
        if any(k in self.competency_vectors for k in pii_keys):
            raise ValidationError("Competency vectors contain prohibited PII fields.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.competency_domain}"


class LearningMilestone(models.Model):
    """
    Formative milestones reached by student with cryptographic evidence digest.
    Revocable via formal RETRACTED status and restorable.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_milestones",
    )
    student_id = models.UUIDField(db_index=True)
    milestone_code = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=MilestoneStatus.choices,
        default=MilestoneStatus.ACHIEVED,
    )
    achieved_at = models.DateTimeField(auto_now_add=True)
    retracted_at = models.DateTimeField(null=True, blank=True)
    retraction_reason = models.TextField(null=True, blank=True)
    source_submission = models.ForeignKey(
        Submission,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="learning_milestones",
    )
    source_certificate = models.ForeignKey(
        CourseCertificate,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="learning_milestones",
    )
    evidence_digest = models.CharField(max_length=64)
    evidence_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_milestone_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "milestone_code"],
                condition=Q(status="ACHIEVED"),
                name="uq_milestone_active_code",
            ),
            models.CheckConstraint(
                condition=Q(status__in=MilestoneStatus.values),
                name="learning_milestone_status_check",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status="RETRACTED") & Q(retracted_at__isnull=False) & Q(retraction_reason__isnull=False)) |
                    (Q(status="ACHIEVED") & Q(retracted_at__isnull=True) & Q(retraction_reason__isnull=True))
                ),
                name="learning_milestone_retraction_check",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "achieved_at"], name="idx_milestone_chronological"),
        ]

    def clean(self):
        super().clean()
        if self.status == MilestoneStatus.RETRACTED:
            if not self.retracted_at or not self.retraction_reason:
                raise ValidationError("Retracted milestone must have retracted_at and retraction_reason.")
        elif self.status == MilestoneStatus.ACHIEVED:
            if self.retracted_at or self.retraction_reason:
                raise ValidationError("Achieved milestone cannot have retraction metadata.")
        if len(self.evidence_digest) != 64:
            raise ValidationError("Evidence digest must be a 64-character hexadecimal SHA-256 string.")
        pii_keys = {"name", "phone", "email", "national_id", "location", "avatar_url"}
        if any(k in self.evidence_payload for k in pii_keys):
            raise ValidationError("Evidence payload contains prohibited PII fields.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.milestone_code}:{self.status}"


class LearningInsight(models.Model):
    """
    Qualitative personalized formative insight generated for student.
    Lifecycle: ACTIVE -> SUPERSEDED (on re-derivation) or RETRACTED.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_insights",
    )
    student_id = models.UUIDField(db_index=True)
    insight_type = models.CharField(max_length=40, choices=InsightType.choices)
    title = models.CharField(max_length=180)
    description = models.TextField()
    confidence_level = models.CharField(
        max_length=16,
        choices=ConfidenceLevel.choices,
        default=ConfidenceLevel.MEDIUM,
    )
    lifecycle_status = models.CharField(
        max_length=20,
        choices=InsightLifecycleStatus.choices,
        default=InsightLifecycleStatus.ACTIVE,
    )
    calculation_run = models.ForeignKey(
        CalculationRun,
        on_delete=models.RESTRICT,
        related_name="learning_insights",
    )
    valid_until = models.DateTimeField(null=True, blank=True)
    retracted_at = models.DateTimeField(null=True, blank=True)
    retraction_reason = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_insight_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "insight_type"],
                condition=Q(lifecycle_status="ACTIVE"),
                name="uq_insight_singleton_active",
            ),
            models.CheckConstraint(
                condition=Q(insight_type__in=InsightType.values),
                name="learning_insight_type_check",
            ),
            models.CheckConstraint(
                condition=Q(confidence_level__in=ConfidenceLevel.values),
                name="learning_insight_confidence_check",
            ),
            models.CheckConstraint(
                condition=Q(lifecycle_status__in=InsightLifecycleStatus.values),
                name="learning_insight_lifecycle_check",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(lifecycle_status="RETRACTED") & Q(retracted_at__isnull=False) & Q(retraction_reason__isnull=False)) |
                    (Q(lifecycle_status__in=["ACTIVE", "SUPERSEDED"]) & Q(retracted_at__isnull=True) & Q(retraction_reason__isnull=True))
                ),
                name="learning_insight_retraction_check",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "created_at"], name="idx_insight_active_feed"),
        ]

    def clean(self):
        super().clean()
        if str(self.calculation_run.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between insight and calculation run.")
        if self.lifecycle_status == InsightLifecycleStatus.RETRACTED:
            if not self.retracted_at or not self.retraction_reason:
                raise ValidationError("Retracted insight must have retracted_at and retraction_reason.")
        elif self.retracted_at or self.retraction_reason:
            raise ValidationError("Active or superseded insight cannot have retraction metadata.")
        pii_keys = {"name", "phone", "email", "national_id", "location", "avatar_url"}
        if any(k in self.metadata for k in pii_keys):
            raise ValidationError("Metadata contains prohibited PII fields.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.insight_type}:{self.lifecycle_status}"


class InsightGenerationEvent(models.Model):
    """
    Append-Only Audit & Idempotency Log for insight derivation runs.
    Enforces strict idempotency per event_type and event_key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="insight_generation_events",
    )
    student_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=64)
    event_key = models.CharField(max_length=128)
    calculation_run = models.ForeignKey(
        CalculationRun,
        on_delete=models.RESTRICT,
        related_name="generation_events",
    )
    status = models.CharField(
        max_length=20,
        choices=GenerationEventStatus.choices,
        default=GenerationEventStatus.PROCESSED,
    )
    failure_reason = models.TextField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    triggered_by = models.UUIDField(db_index=True)
    payload_digest = models.CharField(max_length=64)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="learning_genevent_tenant_id_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "event_type", "event_key"],
                name="learning_genevent_idempotency_uniq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=GenerationEventStatus.values),
                name="learning_genevent_status_check",
            ),
            models.CheckConstraint(
                condition=Q(retry_count__gte=0) & Q(retry_count__lte=10),
                name="learning_genevent_retry_check",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status__in=["REJECTED", "FAILED"]) & Q(failure_reason__isnull=False)) |
                    (Q(status="PROCESSED") & Q(failure_reason__isnull=True))
                ),
                name="learning_genevent_failure_check",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "calculation_run"], name="idx_genevent_audit"),
        ]

    def clean(self):
        super().clean()
        if str(self.calculation_run.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between generation event and calculation run.")
        if self.status in [GenerationEventStatus.REJECTED, GenerationEventStatus.FAILED] and not self.failure_reason:
            raise ValidationError("Failed or rejected event must have failure_reason.")
        if self.status == GenerationEventStatus.PROCESSED and self.failure_reason:
            raise ValidationError("Processed event cannot have failure_reason.")
        if len(self.payload_digest) != 64:
            raise ValidationError("Payload digest must be a 64-character hexadecimal SHA-256 string.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("InsightGenerationEvent is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("InsightGenerationEvent records are immutable audit logs and cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.event_type}:{self.event_key}:{self.status}"


# ============================================================================
# P3-VS14: STUDENT LEARNING OPERATIONS, REFLECTION & AI-ASSISTED GROWTH
# Canonical Models conforming to DDL v1.6-CANONICAL & PostgreSQL 17 Force RLS
# ============================================================================

class ReflectionPromptType(models.TextChoices):
    WEEKLY_REVIEW = "WEEKLY_REVIEW", "Weekly Review"
    MILESTONE_RETROSPECTIVE = "MILESTONE_RETROSPECTIVE", "Milestone Retrospective"
    OBSTACLE_ANALYSIS = "OBSTACLE_ANALYSIS", "Obstacle Analysis"
    FREE_REFLECTION = "FREE_REFLECTION", "Free Reflection"


class ReflectionMoodSentiment(models.TextChoices):
    GROWTH_MINDSET = "GROWTH_MINDSET", "Growth Mindset"
    CONFIDENT = "CONFIDENT", "Confident"
    CHALLENGED = "CHALLENGED", "Challenged"
    CURIOUS = "CURIOUS", "Curious"
    NEUTRAL = "NEUTRAL", "Neutral"


class GoalStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    ACHIEVED = "ACHIEVED", "Achieved"
    PAUSED = "PAUSED", "Paused"
    ARCHIVED = "ARCHIVED", "Archived"
    SUPERSEDED = "SUPERSEDED", "Superseded"


class ActionPlanStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    SKIPPED = "SKIPPED", "Skipped"


class SuggestionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending (Moderation Gate)"
    PRESENTED = "PRESENTED", "Presented to Student"
    ACCEPTED = "ACCEPTED", "Accepted by Student"
    DISMISSED = "DISMISSED", "Dismissed by Student"
    WITHDRAWN = "WITHDRAWN", "Withdrawn by Mentor/System"
    SUPERSEDED = "SUPERSEDED", "Superseded by Newer Insight"


class ReflectionAuditAction(models.TextChoices):
    CREATE_REFLECTION = "CREATE_REFLECTION", "Create Reflection"
    RETRACT_REFLECTION = "RETRACT_REFLECTION", "Retract Reflection"
    RESTORE_REFLECTION = "RESTORE_REFLECTION", "Restore Reflection"
    CREATE_GOAL = "CREATE_GOAL", "Create Goal"
    TRANSITION_GOAL_STATUS = "TRANSITION_GOAL_STATUS", "Transition Goal Status"
    CREATE_ACTION_PLAN = "CREATE_ACTION_PLAN", "Create Action Plan"
    UPDATE_ACTION_PLAN = "UPDATE_ACTION_PLAN", "Update Action Plan"
    GENERATE_AI_SUGGESTION = "GENERATE_AI_SUGGESTION", "Generate AI Suggestion"
    MODERATE_AI_SUGGESTION = "MODERATE_AI_SUGGESTION", "Moderate AI Suggestion"
    ACCEPT_AI_SUGGESTION = "ACCEPT_AI_SUGGESTION", "Accept AI Suggestion"
    DISMISS_AI_SUGGESTION = "DISMISS_AI_SUGGESTION", "Dismiss AI Suggestion"
    SUPERSEDE_AI_SUGGESTION = "SUPERSEDE_AI_SUGGESTION", "Supersede AI Suggestion"
    WITHDRAW_AI_SUGGESTION = "WITHDRAW_AI_SUGGESTION", "Withdraw AI Suggestion"
    POST_MENTOR_FEEDBACK = "POST_MENTOR_FEEDBACK", "Post Mentor Feedback"
    RETRACT_MENTOR_FEEDBACK = "RETRACT_MENTOR_FEEDBACK", "Retract Mentor Feedback"


class LearningReflection(models.Model):
    """
    P3-VS14: Student qualitative learning reflection journal.
    Immutable post-creation except for audited retraction.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_reflections",
    )
    student_id = models.UUIDField(db_index=True)
    prompt_type = models.CharField(max_length=32, choices=ReflectionPromptType.choices)
    content = models.TextField()
    mood_sentiment = models.CharField(
        max_length=32,
        choices=ReflectionMoodSentiment.choices,
        default=ReflectionMoodSentiment.NEUTRAL,
    )
    is_retracted = models.BooleanField(default=False)
    retracted_at = models.DateTimeField(null=True, blank=True)
    retraction_reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_learningreflection_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(prompt_type__in=ReflectionPromptType.values),
                name="chk_reflection_prompt_type",
            ),
            models.CheckConstraint(
                condition=Q(mood_sentiment__in=ReflectionMoodSentiment.values),
                name="chk_reflection_mood",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(is_retracted=False) & Q(retracted_at__isnull=True) & Q(retraction_reason__isnull=True)) |
                    (Q(is_retracted=True) & Q(retracted_at__isnull=False) & Q(retraction_reason__isnull=False))
                ),
                name="chk_reflection_retraction_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "-created_at"], name="idx_reflection_tenant_student"),
        ]

    def clean(self):
        super().clean()
        if not self.content or not self.content.strip():
            raise ValidationError("Reflection content cannot be empty.")
        if len(self.content) > 10000:
            raise ValidationError("Reflection content cannot exceed 10,000 characters.")
        from modules.platform_tenant.models import TenantMembership
        if self.tenant_id and self.student_id:
            if not TenantMembership.objects.filter(tenant_id=self.tenant_id, user_id=self.student_id).exists():
                raise ValidationError("Student must belong to the specified tenant.")
        if self.is_retracted and (not self.retracted_at or not self.retraction_reason):
            raise ValidationError("Retracted reflection must have retracted_at and retraction_reason.")
        if not self.is_retracted and (self.retracted_at or self.retraction_reason):
            raise ValidationError("Active reflection cannot have retracted_at or retraction_reason.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.prompt_type}:{self.id}"


class StudentLearningGoal(models.Model):
    """
    P3-VS14: Student personal learning goal lifecycle FSM.
    Enforces active singleton per domain and formative growth principles.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_goals",
    )
    student_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    domain = models.CharField(max_length=64, db_index=True)
    target_milestone = models.ForeignKey(
        "learning.LearningMilestone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="targeted_goals",
    )
    status = models.CharField(
        max_length=32,
        choices=GoalStatus.choices,
        default=GoalStatus.DRAFT,
    )
    target_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_studentlearninggoal_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "domain"],
                condition=Q(status="ACTIVE"),
                name="uq_goal_student_domain_active",
            ),
            models.CheckConstraint(
                condition=Q(status__in=GoalStatus.values),
                name="chk_goal_status",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status="ACHIEVED") & Q(completed_at__isnull=False)) |
                    (~Q(status="ACHIEVED") & Q(completed_at__isnull=True))
                ),
                name="chk_goal_completion_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="idx_goal_tenant_student_status"),
        ]

    def clean(self):
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError("Goal title cannot be empty.")
        if self.target_milestone and str(self.target_milestone.tenant_id) != str(self.tenant_id):
            raise ValidationError("Target milestone tenant must match goal tenant.")
        if self.status == GoalStatus.ACHIEVED and not self.completed_at:
            raise ValidationError("Achieved goal must have completed_at timestamp.")
        if self.status != GoalStatus.ACHIEVED and self.completed_at:
            raise ValidationError("Non-achieved goal cannot have completed_at timestamp.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.domain}:{self.status}:{self.title}"


class GoalActionPlan(models.Model):
    """
    P3-VS14: Actionable sequential steps associated with a learning goal.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="goal_action_plans",
    )
    goal = models.ForeignKey(
        StudentLearningGoal,
        on_delete=models.CASCADE,
        related_name="action_steps",
    )
    step_order = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=500)
    status = models.CharField(
        max_length=32,
        choices=ActionPlanStatus.choices,
        default=ActionPlanStatus.PENDING,
    )
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_goalactionplan_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "goal", "step_order"],
                name="uq_goalactionplan_step",
            ),
            models.CheckConstraint(
                condition=Q(step_order__gte=1),
                name="chk_action_step_order",
            ),
            models.CheckConstraint(
                condition=Q(status__in=ActionPlanStatus.values),
                name="chk_action_status",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status="COMPLETED") & Q(completed_at__isnull=False)) |
                    (~Q(status="COMPLETED") & Q(completed_at__isnull=True))
                ),
                name="chk_action_completed_consistency",
            ),
        ]

    def clean(self):
        super().clean()
        if str(self.goal.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between action plan and goal.")
        if self.step_order < 1:
            raise ValidationError("Step order must be >= 1.")
        if self.status == ActionPlanStatus.COMPLETED and not self.completed_at:
            raise ValidationError("Completed action step must have completed_at timestamp.")
        if self.status != ActionPlanStatus.COMPLETED and self.completed_at:
            raise ValidationError("Non-completed action step cannot have completed_at timestamp.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.goal_id}:step_{self.step_order}:{self.status}"


class AIAssistedGrowthSuggestion(models.Model):
    """
    P3-VS14: Assistive, non-authoritative AI recommendation.
    Enforces moderation gate, explainability invariant, and strict PII scrub.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="ai_growth_suggestions",
    )
    student_id = models.UUIDField(db_index=True)
    source_insight = models.ForeignKey(
        "learning.LearningInsight",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="growth_suggestions",
    )
    generation_run = models.ForeignKey(
        CalculationRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="growth_suggestions",
    )
    suggestion_type = models.CharField(max_length=32)
    recommended_action = models.CharField(max_length=500)
    rationale = models.TextField()
    evidence_context = models.JSONField()
    model_identifier = models.CharField(max_length=64)
    provenance_digest = models.CharField(max_length=64)
    idempotency_key = models.CharField(max_length=128)
    status = models.CharField(
        max_length=32,
        choices=SuggestionStatus.choices,
        default=SuggestionStatus.PENDING,
    )
    is_authoritative = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_aiassistedgrowthsuggestion_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                name="uq_growthsuggestion_idempotency",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id", "suggestion_type"],
                condition=Q(status="PRESENTED"),
                name="uq_suggestion_presented_singleton",
            ),
            models.CheckConstraint(
                condition=Q(status__in=SuggestionStatus.values),
                name="chk_suggestion_status",
            ),
            models.CheckConstraint(
                condition=Q(is_authoritative=False),
                name="chk_suggestion_advisory_invariant",
            ),
            models.CheckConstraint(
                condition=~Q(evidence_context={}),
                name="chk_suggestion_evidence_context",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="idx_suggestion_student_status"),
        ]

    def clean(self):
        super().clean()
        if self.is_authoritative:
            raise ValidationError("AI suggestions must remain non-authoritative (is_authoritative=False).")
        if not self.evidence_context or self.evidence_context == {}:
            raise ValidationError("evidence_context cannot be empty (Explainability First).")
        if not isinstance(self.evidence_context, dict):
            raise ValidationError("evidence_context must be a JSON object.")
        if len(self.rationale.strip()) < 15:
            raise ValidationError("Rationale must be at least 15 characters.")
        if len(self.provenance_digest) != 64:
            raise ValidationError("Provenance digest must be a 64-character SHA-256 hex string.")
        if self.source_insight and str(self.source_insight.tenant_id) != str(self.tenant_id):
            raise ValidationError("Source insight tenant mismatch.")
        if self.generation_run and str(self.generation_run.tenant_id) != str(self.tenant_id):
            raise ValidationError("Generation run tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.suggestion_type}:{self.status}"


class MentorReflectionFeedback(models.Model):
    """
    P3-VS14: Interactive pedagogical guidance and formative feedback from mentor.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="mentor_feedbacks",
    )
    reflection = models.ForeignKey(
        LearningReflection,
        on_delete=models.CASCADE,
        related_name="mentor_feedbacks",
    )
    mentor_id = models.UUIDField(db_index=True)
    feedback_text = models.TextField()
    is_retracted = models.BooleanField(default=False)
    retracted_at = models.DateTimeField(null=True, blank=True)
    retraction_reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_mentorreflectionfeedback_tenant_id",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(is_retracted=False) & Q(retracted_at__isnull=True) & Q(retraction_reason__isnull=True)) |
                    (Q(is_retracted=True) & Q(retracted_at__isnull=False) & Q(retraction_reason__isnull=False))
                ),
                name="chk_feedback_retraction_consistency",
            ),
        ]

    def clean(self):
        super().clean()
        if not self.feedback_text or not self.feedback_text.strip():
            raise ValidationError("Feedback text cannot be empty.")
        if len(self.feedback_text) > 5000:
            raise ValidationError("Feedback text cannot exceed 5000 characters.")
        if str(self.reflection.tenant_id) != str(self.tenant_id):
            raise ValidationError("Tenant mismatch between feedback and reflection.")
        if self.is_retracted and (not self.retracted_at or not self.retraction_reason):
            raise ValidationError("Retracted feedback must specify retraction_reason and retracted_at.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:refl_{self.reflection_id}:mentor_{self.mentor_id}"


class ReflectionAuditLog(models.Model):
    """
    P3-VS14: Forensic append-only audit trail with XOR polymorphic targets
    and Deferrable FK topology (SA-2).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="reflection_audit_logs",
    )
    actor_id = models.UUIDField(db_index=True)
    target_reflection = models.ForeignKey(
        LearningReflection,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_goal = models.ForeignKey(
        StudentLearningGoal,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_feedback = models.ForeignKey(
        MentorReflectionFeedback,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_suggestion = models.ForeignKey(
        AIAssistedGrowthSuggestion,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64, choices=ReflectionAuditAction.choices)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_reflectionauditlog_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(action__in=ReflectionAuditAction.values),
                name="chk_audit_action",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_audit_tenant_actor_time"),
            models.Index(fields=["tenant", "target_reflection"], name="idx_audit_tenant_refl"),
            models.Index(fields=["tenant", "target_goal"], name="idx_audit_tenant_goal"),
            models.Index(fields=["tenant", "target_feedback"], name="idx_audit_tenant_feedback"),
            models.Index(fields=["tenant", "target_suggestion"], name="idx_audit_tenant_sugg"),
        ]

    def clean(self):
        super().clean()
        targets = [self.target_reflection, self.target_goal, self.target_feedback, self.target_suggestion]
        non_null_count = sum(1 for t in targets if t is not None)
        if non_null_count != 1:
            raise ValidationError("Exactly one target entity must be specified (chk_audit_target_xor).")
        for t in targets:
            if t is not None and str(t.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target entity tenant mismatch.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("ReflectionAuditLog is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("ReflectionAuditLog records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.actor_id}:{self.action}:{self.created_at}"

