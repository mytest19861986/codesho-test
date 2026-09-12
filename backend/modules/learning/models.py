import re
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


# ============================================================================
# P3-VS15: LEARNING CONTINUITY & STUDENT SUCCESS PLANNING MODELS
# ============================================================================

class SuccessPlanStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    PAUSED = "PAUSED", "Paused"
    COMPLETED = "COMPLETED", "Completed"
    SUPERSEDED = "SUPERSEDED", "Superseded"
    ARCHIVED = "ARCHIVED", "Archived"


class SuccessPlanTargetPeriod(models.TextChoices):
    CURRENT_TERM = "CURRENT_TERM", "Current Term"
    ACADEMIC_YEAR = "ACADEMIC_YEAR", "Academic Year"
    SUMMER_INTENSIVE = "SUMMER_INTENSIVE", "Summer Intensive"
    MONTHLY_SPRINT = "MONTHLY_SPRINT", "Monthly Sprint"
    QUARTERLY_CYCLE = "QUARTERLY_CYCLE", "Quarterly Cycle"
    LONG_TERM_FOUNDATION = "LONG_TERM_FOUNDATION", "Long Term Foundation"


class SuccessActionStepStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    SKIPPED = "SKIPPED", "Skipped"
    CANCELLED = "CANCELLED", "Cancelled"


class SuccessTimelineEventType(models.TextChoices):
    GOAL_ANCHORED = "GOAL_ANCHORED", "Goal Anchored"
    INSIGHT_CONNECTED = "INSIGHT_CONNECTED", "Insight Connected"
    REFLECTION_TIED = "REFLECTION_TIED", "Reflection Tied"
    ACTION_DISPATCHED = "ACTION_DISPATCHED", "Action Dispatched"
    MILESTONE_PROGRESSION = "MILESTONE_PROGRESSION", "Milestone Progression"
    TIMELINE_EVENT_AMENDED = "TIMELINE_EVENT_AMENDED", "Timeline Event Amended"


class SuccessAuditAction(models.TextChoices):
    CREATE_SUCCESS_PLAN = "CREATE_SUCCESS_PLAN", "Create Success Plan"
    PAUSE_SUCCESS_PLAN = "PAUSE_SUCCESS_PLAN", "Pause Success Plan"
    RESUME_SUCCESS_PLAN = "RESUME_SUCCESS_PLAN", "Resume Success Plan"
    COMPLETE_SUCCESS_PLAN = "COMPLETE_SUCCESS_PLAN", "Complete Success Plan"
    SUPERSEDE_SUCCESS_PLAN = "SUPERSEDE_SUCCESS_PLAN", "Supersede Success Plan"
    ARCHIVE_SUCCESS_PLAN = "ARCHIVE_SUCCESS_PLAN", "Archive Success Plan"
    CREATE_ACTION_STEP = "CREATE_ACTION_STEP", "Create Action Step"
    UPDATE_ACTION_STEP = "UPDATE_ACTION_STEP", "Update Action Step"
    TRANSITION_ACTION_STEP = "TRANSITION_ACTION_STEP", "Transition Action Step"
    APPEND_TIMELINE_EVENT = "APPEND_TIMELINE_EVENT", "Append Timeline Event"


class LearningStudentSuccessPlan(models.Model):
    """
    P3-VS15: Student longitudinal success plan with Active Singleton invariant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="student_success_plans",
    )
    student_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    target_period = models.CharField(max_length=64, choices=SuccessPlanTargetPeriod.choices)
    status = models.CharField(max_length=32, choices=SuccessPlanStatus.choices, default=SuccessPlanStatus.ACTIVE)
    notes = models.TextField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    superseded_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_studentsuccessplan"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_studentsuccessplan_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id"],
                condition=Q(status=SuccessPlanStatus.ACTIVE),
                name="uq_successplan_student_active",
            ),
            models.CheckConstraint(
                condition=Q(status__in=SuccessPlanStatus.values),
                name="chk_successplan_status",
            ),
            models.CheckConstraint(
                condition=Q(target_period__in=SuccessPlanTargetPeriod.values),
                name="chk_successplan_target_period",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status=SuccessPlanStatus.ACTIVE) & Q(completed_at__isnull=True) & Q(paused_at__isnull=True) & Q(superseded_at__isnull=True) & Q(archived_at__isnull=True)) |
                    (Q(status=SuccessPlanStatus.PAUSED) & Q(paused_at__isnull=False) & Q(completed_at__isnull=True) & Q(superseded_at__isnull=True) & Q(archived_at__isnull=True)) |
                    (Q(status=SuccessPlanStatus.COMPLETED) & Q(completed_at__isnull=False) & Q(paused_at__isnull=True) & Q(superseded_at__isnull=True) & Q(archived_at__isnull=True)) |
                    (Q(status=SuccessPlanStatus.SUPERSEDED) & Q(superseded_at__isnull=False) & Q(archived_at__isnull=True)) |
                    (Q(status=SuccessPlanStatus.ARCHIVED) & Q(archived_at__isnull=False))
                ),
                name="chk_successplan_status_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "-created_at"], name="idx_successplan_tenant_student"),
        ]

    def clean(self):
        super().clean()
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters.")
        if len(self.title) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")
        if self.notes and len(self.notes) > 4000:
            raise ValidationError("Notes cannot exceed 4000 characters.")
        from modules.platform_tenant.models import TenantMembership
        if self.tenant_id and self.student_id:
            if not TenantMembership.objects.filter(tenant_id=self.tenant_id, user_id=self.student_id).exists():
                raise ValidationError("Student must belong to the specified tenant.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.title}:{self.status}"


class SuccessActionStep(models.Model):
    """
    P3-VS15: Granular, sequential action steps tied to a StudentSuccessPlan.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="success_action_steps",
    )
    plan = models.ForeignKey(
        LearningStudentSuccessPlan,
        on_delete=models.CASCADE,
        related_name="action_steps",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=SuccessActionStepStatus.choices, default=SuccessActionStepStatus.PENDING)
    sequence_order = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_authoritative = models.BooleanField(default=False)
    target_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_successactionstep"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_successactionstep_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "plan", "sequence_order"],
                name="uq_actionstep_tenant_plan_seq",
            ),
            models.CheckConstraint(
                condition=Q(sequence_order__gte=1),
                name="chk_actionstep_seq_positive",
            ),
            models.CheckConstraint(
                condition=Q(status__in=SuccessActionStepStatus.values),
                name="chk_actionstep_status",
            ),
            models.CheckConstraint(
                condition=Q(is_authoritative=False),
                name="chk_step_non_authoritative",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status=SuccessActionStepStatus.COMPLETED) & Q(completed_at__isnull=False)) |
                    (~Q(status=SuccessActionStepStatus.COMPLETED) & Q(completed_at__isnull=True))
                ),
                name="chk_step_completion_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "plan", "sequence_order"], name="idx_actionstep_tenant_plan_seq"),
        ]

    def clean(self):
        super().clean()
        if self.is_authoritative:
            raise ValidationError("Action steps must remain non-authoritative (is_authoritative=False).")
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters.")
        if len(self.title) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")
        if self.description and len(self.description) > 4000:
            raise ValidationError("Description cannot exceed 4000 characters.")
        if self.plan and str(self.plan.tenant_id) != str(self.tenant_id):
            raise ValidationError("Plan tenant mismatch.")
        if self.sequence_order < 1:
            raise ValidationError("Sequence order must be at least 1.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.plan_id}:{self.sequence_order}:{self.title}"


class SuccessTimelineEvent(models.Model):
    """
    P3-VS15: Append-only longitudinal learning trail connecting goals, insights,
    reflections, action steps, and milestones with 5-way XOR and Deferrable FK topology.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="success_timeline_events",
    )
    plan = models.ForeignKey(
        LearningStudentSuccessPlan,
        on_delete=models.DO_NOTHING,
        related_name="timeline_events",
    )
    actor_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=64, choices=SuccessTimelineEventType.choices)
    headline = models.CharField(max_length=255)
    detail = models.TextField(null=True, blank=True)
    target_goal = models.ForeignKey(
        StudentLearningGoal,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="timeline_events",
    )
    target_insight = models.ForeignKey(
        LearningInsight,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="timeline_events",
    )
    target_reflection = models.ForeignKey(
        LearningReflection,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="timeline_events",
    )
    target_action_step = models.ForeignKey(
        SuccessActionStep,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="timeline_events",
    )
    target_milestone = models.ForeignKey(
        LearningMilestone,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="timeline_events",
    )
    client_mutation_id = models.UUIDField(null=True, blank=True, db_index=True)
    replaces_event = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="amendments",
    )
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_successtimelineevent"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_successtimelineevent_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "client_mutation_id"],
                condition=Q(client_mutation_id__isnull=False),
                name="uq_timelineevent_tenant_mutation",
            ),
            models.CheckConstraint(
                condition=Q(event_type__in=SuccessTimelineEventType.values),
                name="chk_timeline_event_type",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "plan", "-created_at"], name="idx_timeline_tenant_plan_time"),
            models.Index(fields=["tenant", "target_goal"], name="idx_timeline_tenant_goal"),
            models.Index(fields=["tenant", "target_insight"], name="idx_timeline_tenant_insight"),
            models.Index(fields=["tenant", "target_reflection"], name="idx_timeline_tenant_reflection"),
            models.Index(fields=["tenant", "target_action_step"], name="idx_timeline_tenant_action"),
            models.Index(fields=["tenant", "target_milestone"], name="idx_timeline_tenant_milestone"),
            models.Index(fields=["tenant", "replaces_event"], name="idx_timeline_tenant_replaces"),
        ]

    def clean(self):
        super().clean()
        if not self.headline or len(self.headline.strip()) < 3:
            raise ValidationError("Headline must be at least 3 characters.")
        if len(self.headline) > 255:
            raise ValidationError("Headline cannot exceed 255 characters.")
        if self.detail and len(self.detail) > 4000:
            raise ValidationError("Detail cannot exceed 4000 characters.")
        targets = [
            self.target_goal,
            self.target_insight,
            self.target_reflection,
            self.target_action_step,
            self.target_milestone,
        ]
        non_null_count = sum(1 for t in targets if t is not None)
        if non_null_count != 1:
            raise ValidationError("Exactly one target entity must be linked (chk_timeline_target_xor).")
        # 1-to-1 Type-Target coupling verification
        if self.event_type == SuccessTimelineEventType.GOAL_ANCHORED and self.target_goal is None:
            raise ValidationError("GOAL_ANCHORED must link target_goal.")
        elif self.event_type == SuccessTimelineEventType.INSIGHT_CONNECTED and self.target_insight is None:
            raise ValidationError("INSIGHT_CONNECTED must link target_insight.")
        elif self.event_type == SuccessTimelineEventType.REFLECTION_TIED and self.target_reflection is None:
            raise ValidationError("REFLECTION_TIED must link target_reflection.")
        elif self.event_type == SuccessTimelineEventType.ACTION_DISPATCHED and self.target_action_step is None:
            raise ValidationError("ACTION_DISPATCHED must link target_action_step.")
        elif self.event_type == SuccessTimelineEventType.MILESTONE_PROGRESSION and self.target_milestone is None:
            raise ValidationError("MILESTONE_PROGRESSION must link target_milestone.")
        elif self.event_type == SuccessTimelineEventType.TIMELINE_EVENT_AMENDED and self.replaces_event is None:
            raise ValidationError("TIMELINE_EVENT_AMENDED must specify replaces_event.")

        for t in targets:
            if t is not None and str(t.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target entity tenant mismatch.")
        if self.plan and str(self.plan.tenant_id) != str(self.tenant_id):
            raise ValidationError("Plan tenant mismatch.")
        if self.replaces_event and str(self.replaces_event.tenant_id) != str(self.tenant_id):
            raise ValidationError("Replaces event tenant mismatch.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("SuccessTimelineEvent is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("SuccessTimelineEvent records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.plan_id}:{self.event_type}:{self.headline}"


class SuccessAuditLog(models.Model):
    """
    P3-VS15: Forensic append-only audit trail for StudentSuccessPlan,
    SuccessActionStep, and SuccessTimelineEvent mutations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="success_audit_logs",
    )
    actor_id = models.UUIDField(db_index=True)
    target_plan = models.ForeignKey(
        LearningStudentSuccessPlan,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_action_step = models.ForeignKey(
        SuccessActionStep,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_timeline_event = models.ForeignKey(
        SuccessTimelineEvent,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64, choices=SuccessAuditAction.choices)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_successauditlog"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_successauditlog_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(action__in=SuccessAuditAction.values),
                name="chk_successaudit_action",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_successaudit_tenant_actor"),
            models.Index(fields=["tenant", "target_plan"], name="idx_successaudit_tenant_plan"),
            models.Index(fields=["tenant", "target_action_step"], name="idx_successaudit_tenant_act"),
            models.Index(fields=["tenant", "target_timeline_event"], name="idx_successaudit_tenant_time"),
        ]

    def clean(self):
        super().clean()
        targets = [self.target_plan, self.target_action_step, self.target_timeline_event]
        non_null_count = sum(1 for t in targets if t is not None)
        if non_null_count != 1:
            raise ValidationError("Exactly one target entity must be specified (chk_successaudit_target_xor).")
        for t in targets:
            if t is not None and str(t.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target entity tenant mismatch.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("SuccessAuditLog is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("SuccessAuditLog records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.actor_id}:{self.action}:{self.created_at}"


# ============================================================================
# P3-VS16: Mentor-Student Success Coaching & Intervention Workflow Models
# ============================================================================

class CoachingSessionStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class CoachingNoteType(models.TextChoices):
    OBSERVATION = "OBSERVATION", "Observation"
    STRENGTH = "STRENGTH", "Strength"
    GROWTH_OPPORTUNITY = "GROWTH_OPPORTUNITY", "Growth Opportunity"
    ACTION_ITEM = "ACTION_ITEM", "Action Item"
    SUMMARY = "SUMMARY", "Summary"


class SupportInterventionCategory(models.TextChoices):
    ACADEMIC_SCAFFOLDING = "ACADEMIC_SCAFFOLDING", "Academic Scaffolding"
    RESOURCE_RECOMMENDATION = "RESOURCE_RECOMMENDATION", "Resource Recommendation"
    STUDY_STRATEGY = "STUDY_STRATEGY", "Study Strategy"
    PACING_ADJUSTMENT = "PACING_ADJUSTMENT", "Pacing Adjustment"
    PEER_STUDY_CONNECTION = "PEER_STUDY_CONNECTION", "Peer Study Connection"


class SupportInterventionStatus(models.TextChoices):
    PROPOSED = "PROPOSED", "Proposed"
    ACCEPTED = "ACCEPTED", "Accepted"
    DECLINED = "DECLINED", "Declined"
    ACTIVE = "ACTIVE", "Active"
    PAUSED = "PAUSED", "Paused"
    COMPLETED = "COMPLETED", "Completed"


class FollowUpActionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    SKIPPED = "SKIPPED", "Skipped"


class CoachingAuditAction(models.TextChoices):
    SCHEDULE_SESSION = "SCHEDULE_SESSION", "Schedule Session"
    START_SESSION = "START_SESSION", "Start Session"
    RESCHEDULE_SESSION = "RESCHEDULE_SESSION", "Reschedule Session"
    CANCEL_SESSION = "CANCEL_SESSION", "Cancel Session"
    COMPLETE_SESSION = "COMPLETE_SESSION", "Complete Session"
    CREATE_NOTE = "CREATE_NOTE", "Create Note"
    PROPOSE_INTERVENTION = "PROPOSE_INTERVENTION", "Propose Intervention"
    ACCEPT_INTERVENTION = "ACCEPT_INTERVENTION", "Accept Intervention"
    DECLINE_INTERVENTION = "DECLINE_INTERVENTION", "Decline Intervention"
    START_INTERVENTION = "START_INTERVENTION", "Start Intervention"
    PAUSE_INTERVENTION = "PAUSE_INTERVENTION", "Pause Intervention"
    RESUME_INTERVENTION = "RESUME_INTERVENTION", "Resume Intervention"
    COMPLETE_INTERVENTION = "COMPLETE_INTERVENTION", "Complete Intervention"
    ASSIGN_ACTION = "ASSIGN_ACTION", "Assign Action"
    START_ACTION = "START_ACTION", "Start Action"
    COMPLETE_ACTION = "COMPLETE_ACTION", "Complete Action"
    SKIP_ACTION = "SKIP_ACTION", "Skip Action"


class CoachingSession(models.Model):
    """
    P3-VS16: Scheduled coaching session between a student and assigned mentor.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="coaching_sessions",
    )
    student_id = models.UUIDField(db_index=True)
    mentor_id = models.UUIDField(db_index=True)
    success_plan = models.ForeignKey(
        LearningStudentSuccessPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coaching_sessions",
    )
    learning_insight = models.ForeignKey(
        LearningInsight,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coaching_sessions",
    )
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=32,
        choices=CoachingSessionStatus.choices,
        default=CoachingSessionStatus.SCHEDULED,
    )
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=1000, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_coachingsession"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_coachingsession_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=CoachingSessionStatus.values),
                name="chk_coachingsession_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "-scheduled_at"], name="idx_coachingsession_stud_time"),
            models.Index(fields=["tenant", "mentor_id", "-scheduled_at"], name="idx_coachingsession_ment_time"),
        ]

    def clean(self):
        super().clean()
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters.")
        if len(self.title) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")
        if self.summary:
            if len(self.summary.strip()) < 5:
                raise ValidationError("Summary must be at least 5 characters.")
            if len(self.summary) > 4000:
                raise ValidationError("Summary cannot exceed 4000 characters.")
        if self.success_plan and str(self.success_plan.tenant_id) != str(self.tenant_id):
            raise ValidationError("Success plan tenant mismatch.")
        if self.learning_insight and str(self.learning_insight.tenant_id) != str(self.tenant_id):
            raise ValidationError("Learning insight tenant mismatch.")

        # Status & Time consistency check
        if self.status == CoachingSessionStatus.SCHEDULED:
            if self.started_at or self.completed_at or self.cancelled_at or self.cancellation_reason:
                raise ValidationError("Scheduled session cannot have start, completion, or cancellation timestamps.")
        elif self.status == CoachingSessionStatus.IN_PROGRESS:
            if not self.started_at or self.completed_at or self.cancelled_at:
                raise ValidationError("In-progress session must have started_at and cannot be completed or cancelled.")
        elif self.status == CoachingSessionStatus.COMPLETED:
            if not self.started_at or not self.completed_at or self.cancelled_at:
                raise ValidationError("Completed session must have started_at and completed_at, and cannot be cancelled.")
            if self.started_at > self.completed_at:
                raise ValidationError("started_at must be before or equal to completed_at.")
        elif self.status == CoachingSessionStatus.CANCELLED:
            if not self.cancelled_at or not self.cancellation_reason or self.completed_at:
                raise ValidationError("Cancelled session must have cancelled_at and cancellation_reason, and cannot be completed.")

        # Composite tenant membership isolation
        from modules.platform_tenant.models import TenantMembership
        if self.tenant_id and self.mentor_id:
            if not TenantMembership.objects.filter(tenant_id=self.tenant_id, user_id=self.mentor_id).exists():
                raise ValidationError("Mentor is not a member of this tenant.")
        if self.tenant_id and self.student_id:
            if not TenantMembership.objects.filter(tenant_id=self.tenant_id, user_id=self.student_id).exists():
                raise ValidationError("Student is not a member of this tenant.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.id}:{self.status}:{self.title}"


class CoachingNote(models.Model):
    """
    P3-VS16: Qualitative mentor coaching note (strictly append-only).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="coaching_notes",
    )
    session = models.ForeignKey(
        CoachingSession,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    author_id = models.UUIDField(db_index=True)
    note_type = models.CharField(
        max_length=32,
        choices=CoachingNoteType.choices,
        default=CoachingNoteType.OBSERVATION,
    )
    content = models.TextField()
    is_shared_with_student = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_coachingnote"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_coachingnote_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(note_type__in=CoachingNoteType.values),
                name="chk_coachingnote_type",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "session", "created_at"], name="idx_coachingnote_session_time"),
        ]

    def clean(self):
        super().clean()
        if not self.content or len(self.content.strip()) < 3:
            raise ValidationError("Content must be at least 3 characters.")
        if len(self.content) > 4000:
            raise ValidationError("Content cannot exceed 4000 characters.")
        if self.session and str(self.session.tenant_id) != str(self.tenant_id):
            raise ValidationError("Session tenant mismatch.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("CoachingNote is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("CoachingNote records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.session_id}:{self.note_type}"


class SupportIntervention(models.Model):
    """
    P3-VS16: Learner Agency First supportive intervention proposed to student.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="support_interventions",
    )
    student_id = models.UUIDField(db_index=True)
    mentor_id = models.UUIDField(db_index=True)
    success_plan = models.ForeignKey(
        LearningStudentSuccessPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_interventions",
    )
    title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=64,
        choices=SupportInterventionCategory.choices,
        default=SupportInterventionCategory.ACADEMIC_SCAFFOLDING,
    )
    status = models.CharField(
        max_length=32,
        choices=SupportInterventionStatus.choices,
        default=SupportInterventionStatus.PROPOSED,
    )
    is_authoritative = models.BooleanField(default=False)
    rationale = models.TextField()
    student_feedback = models.TextField(null=True, blank=True)
    proposed_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_supportintervention"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_supportintervention_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=SupportInterventionStatus.values),
                name="chk_intervention_status",
            ),
            models.CheckConstraint(
                condition=Q(category__in=SupportInterventionCategory.values),
                name="chk_intervention_category_supportive",
            ),
            models.CheckConstraint(
                condition=Q(is_authoritative=False),
                name="chk_intervention_non_authoritative",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="idx_intervention_stud_status"),
        ]

    def clean(self):
        super().clean()
        if self.is_authoritative is not False:
            raise ValidationError("Interventions must strictly respect learner agency (is_authoritative = False).")
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters.")
        if len(self.title) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")
        if not self.rationale or len(self.rationale.strip()) < 10:
            raise ValidationError("Rationale must be at least 10 characters.")
        if len(self.rationale) > 4000:
            raise ValidationError("Rationale cannot exceed 4000 characters.")
        if self.student_feedback:
            if len(self.student_feedback.strip()) < 2:
                raise ValidationError("Student feedback must be at least 2 characters.")
            if len(self.student_feedback) > 2000:
                raise ValidationError("Student feedback cannot exceed 2000 characters.")
        if self.success_plan and str(self.success_plan.tenant_id) != str(self.tenant_id):
            raise ValidationError("Success plan tenant mismatch.")

        # FSM Consistency
        if self.status == SupportInterventionStatus.PROPOSED:
            if self.acknowledged_at or self.declined_at or self.started_at or self.completed_at or self.paused_at:
                raise ValidationError("Proposed intervention cannot have lifecycle timestamps.")
        elif self.status == SupportInterventionStatus.ACCEPTED:
            if not self.acknowledged_at or self.declined_at or self.completed_at:
                raise ValidationError("Accepted intervention must have acknowledged_at and cannot be declined or completed.")
        elif self.status == SupportInterventionStatus.DECLINED:
            if not self.declined_at or self.acknowledged_at or self.started_at or self.completed_at:
                raise ValidationError("Declined intervention must have declined_at and cannot be acknowledged, started, or completed.")
        elif self.status == SupportInterventionStatus.ACTIVE:
            if not self.acknowledged_at or not self.started_at or self.declined_at or self.completed_at or self.paused_at:
                raise ValidationError("Active intervention must be acknowledged and started, not paused, declined, or completed.")
        elif self.status == SupportInterventionStatus.PAUSED:
            if not self.acknowledged_at or not self.started_at or not self.paused_at or self.completed_at:
                raise ValidationError("Paused intervention must have acknowledged_at, started_at, paused_at, and cannot be completed.")
        elif self.status == SupportInterventionStatus.COMPLETED:
            if not self.acknowledged_at or not self.started_at or not self.completed_at:
                raise ValidationError("Completed intervention must have acknowledged_at, started_at, and completed_at.")
            if self.started_at > self.completed_at:
                raise ValidationError("started_at must be before or equal to completed_at.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.status}:{self.title}"


class FollowUpAction(models.Model):
    """
    P3-VS16: Actionable step linked to an intervention or session with exact origin XOR.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="coaching_followup_actions",
    )
    intervention = models.ForeignKey(
        SupportIntervention,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="followup_actions",
    )
    session = models.ForeignKey(
        CoachingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="followup_actions",
    )
    student_id = models.UUIDField(db_index=True)
    assigned_by_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=32,
        choices=FollowUpActionStatus.choices,
        default=FollowUpActionStatus.PENDING,
    )
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    skipped_at = models.DateTimeField(null=True, blank=True)
    skip_reason = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_followupaction"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_followupaction_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=FollowUpActionStatus.values),
                name="chk_followupaction_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "due_date"], name="idx_followupaction_stud_due"),
        ]

    def clean(self):
        super().clean()
        origins = [self.intervention, self.session]
        non_null_count = sum(1 for o in origins if o is not None)
        if non_null_count != 1:
            raise ValidationError("FollowUpAction must originate from exactly one source: either an intervention or a session.")

        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters.")
        if len(self.title) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")

        if self.intervention and str(self.intervention.tenant_id) != str(self.tenant_id):
            raise ValidationError("Intervention tenant mismatch.")
        if self.session and str(self.session.tenant_id) != str(self.tenant_id):
            raise ValidationError("Session tenant mismatch.")

        if self.status in (FollowUpActionStatus.PENDING, FollowUpActionStatus.IN_PROGRESS):
            if self.completed_at or self.skipped_at or self.skip_reason:
                raise ValidationError("Pending or In-progress action cannot have completed_at, skipped_at, or skip_reason.")
        elif self.status == FollowUpActionStatus.COMPLETED:
            if not self.completed_at or self.skipped_at:
                raise ValidationError("Completed action must have completed_at and cannot be skipped.")
        elif self.status == FollowUpActionStatus.SKIPPED:
            if not self.skipped_at or not self.skip_reason or self.completed_at:
                raise ValidationError("Skipped action must have skipped_at and skip_reason, and cannot be completed.")
            if len(self.skip_reason.strip()) < 3:
                raise ValidationError("Skip reason must be at least 3 characters.")
            if len(self.skip_reason) > 1000:
                raise ValidationError("Skip reason cannot exceed 1000 characters.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.student_id}:{self.status}:{self.title}"


class CoachingAuditLog(models.Model):
    """
    P3-VS16: Forensic append-only audit trail for coaching sessions, notes,
    interventions, and follow-up actions with 4-way XOR targets.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="coaching_audit_logs",
    )
    action_type = models.CharField(max_length=64, choices=CoachingAuditAction.choices)
    actor_id = models.UUIDField(db_index=True)
    target_session = models.ForeignKey(
        CoachingSession,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_note = models.ForeignKey(
        CoachingNote,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_intervention = models.ForeignKey(
        SupportIntervention,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_action = models.ForeignKey(
        FollowUpAction,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_coachingauditlog"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_coachingauditlog_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(action_type__in=CoachingAuditAction.values),
                name="chk_coachingaudit_action_type",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_coachingaudit_actor_time"),
            models.Index(fields=["tenant", "target_session"], name="idx_coachingaudit_session"),
            models.Index(fields=["tenant", "target_note"], name="idx_coachingaudit_note"),
            models.Index(fields=["tenant", "target_intervention"], name="idx_coachingaudit_interv"),
            models.Index(fields=["tenant", "target_action"], name="idx_coachingaudit_action"),
        ]

    def clean(self):
        super().clean()
        targets = [self.target_session, self.target_note, self.target_intervention, self.target_action]
        non_null_count = sum(1 for t in targets if t is not None)
        if non_null_count > 1:
            raise ValidationError("At most one target entity may be specified (chk_coachingaudit_target_xor).")
        for t in targets:
            if t is not None and str(t.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target entity tenant mismatch.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("CoachingAuditLog is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("CoachingAuditLog records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.actor_id}:{self.action_type}:{self.created_at}"


# =============================================================================
# P3-MACRO-EPIC-17-19: MENTOR OPERATIONS, LEARNING CONTINUITY & PROGRAM SUCCESS
# Sub-Slices: P3-VS17, P3-VS18, P3-VS19
# Canonical DDL: v1.2-CANONICAL
# =============================================================================

PROHIBITED_PII_KEYS_17_19 = {
    "name", "phone", "email", "national_id", "location", "avatar_url",
    "phone_number", "mobile", "fingerprint", "face_id", "voice_sample",
    "bank_account", "iban", "credit_card", "card_number", "cvv",
    "password", "token", "secret", "ssn", "address"
}

PII_REGEX_17_19 = re.compile(
    r'(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)',
    re.IGNORECASE
)

def _validate_pii_text_field_17_19(val: str, field_name: str, max_len: int = 4000) -> None:
    if not val:
        return
    if len(val) > max_len:
        raise ValidationError(f"{field_name} exceeds max length of {max_len} characters.")
    if PII_REGEX_17_19.search(val):
        raise ValidationError(f"PII detected in {field_name}.")

def _validate_pii_jsonb_field_17_19(val: dict, field_name: str) -> None:
    if val is None:
        return
    if not isinstance(val, dict):
        raise ValidationError(f"{field_name} must be a valid JSON object.")
    bad_keys = set(k.lower() for k in val.keys()) & PROHIBITED_PII_KEYS_17_19
    if bad_keys:
        raise ValidationError(f"Prohibited PII keys in {field_name}: {bad_keys}")


class SupportQueueUrgency(models.TextChoices):
    LOW = "LOW", "Low"
    NORMAL = "NORMAL", "Normal"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class SupportQueueStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_REVIEW = "IN_REVIEW", "In Review"
    RESOLVED = "RESOLVED", "Resolved"
    DISMISSED = "DISMISSED", "Dismissed"


class LearningCheckInStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    RESCHEDULED = "RESCHEDULED", "Rescheduled"
    CANCELLED = "CANCELLED", "Cancelled"


class FollowUpCommitmentOwnerRole(models.TextChoices):
    MENTOR = "MENTOR", "Mentor"
    STUDENT = "STUDENT", "Student"


class MentorOperationsAuditAction(models.TextChoices):
    ASSIGN_CASELOAD = "ASSIGN_CASELOAD", "Assign Caseload"
    UNASSIGN_CASELOAD = "UNASSIGN_CASELOAD", "Unassign Caseload"
    QUEUE_ITEM_PENDING = "QUEUE_ITEM_PENDING", "Queue Item Pending"
    QUEUE_ITEM_IN_REVIEW = "QUEUE_ITEM_IN_REVIEW", "Queue Item In Review"
    QUEUE_ITEM_RESOLVED = "QUEUE_ITEM_RESOLVED", "Queue Item Resolved"
    QUEUE_ITEM_DISMISSED = "QUEUE_ITEM_DISMISSED", "Queue Item Dismissed"
    SCHEDULE_CHECKIN = "SCHEDULE_CHECKIN", "Schedule Check-in"
    START_CHECKIN = "START_CHECKIN", "Start Check-in"
    COMPLETE_CHECKIN = "COMPLETE_CHECKIN", "Complete Check-in"
    RESCHEDULE_CHECKIN = "RESCHEDULE_CHECKIN", "Reschedule Check-in"
    CANCEL_CHECKIN = "CANCEL_CHECKIN", "Cancel Check-in"
    CREATE_COMMITMENT = "CREATE_COMMITMENT", "Create Commitment"
    COMPLETE_COMMITMENT = "COMPLETE_COMMITMENT", "Complete Commitment"
    GENERATE_SUPPORT_AGGREGATE = "GENERATE_SUPPORT_AGGREGATE", "Generate Support Aggregate"


class MentorCaseloadAssignment(models.Model):
    """
    P3-VS17: Mapping of student to mentor with capacity weighting and lifecycle.
    Enforces partial uniqueness for active student assignments per tenant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="mentor_caseload_assignments",
    )
    mentor_id = models.UUIDField(db_index=True)
    student_id = models.UUIDField(db_index=True)
    is_active = models.BooleanField(default=True)
    capacity_weight = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    assigned_at = models.DateTimeField(auto_now_add=True)
    unassigned_at = models.DateTimeField(null=True, blank=True)
    unassignment_reason = models.CharField(max_length=1000, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_mentorcaseloadassignment"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_mentorcaseload_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_id"],
                condition=Q(is_active=True),
                name="uq_mentorcaseload_active_student",
            ),
            models.CheckConstraint(
                condition=Q(capacity_weight__gte=0.10) & Q(capacity_weight__lte=5.00),
                name="chk_mentorcaseload_weight",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(is_active=True) & Q(unassigned_at__isnull=True) & Q(unassignment_reason__isnull=True)) |
                    (Q(is_active=False) & Q(unassigned_at__isnull=False) & Q(assigned_at__lte=models.F("unassigned_at")))
                ),
                name="chk_mentorcaseload_unassigned_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "mentor_id", "is_active"], name="idx_mentorcaseload_mentor_act"),
        ]

    def clean(self):
        super().clean()
        if self.is_active:
            if self.unassigned_at or self.unassignment_reason:
                raise ValidationError("Active caseload assignment cannot have unassigned_at or unassignment_reason.")
        else:
            if not self.unassigned_at:
                raise ValidationError("Inactive caseload assignment must specify unassigned_at.")
            if self.assigned_at and self.unassigned_at and self.assigned_at > self.unassigned_at:
                raise ValidationError("assigned_at must be before or equal to unassigned_at.")
            if self.unassignment_reason and len(self.unassignment_reason.strip()) < 3:
                raise ValidationError("Unassignment reason must be at least 3 characters.")
        if self.capacity_weight < 0.10 or self.capacity_weight > 5.00:
            raise ValidationError("Capacity weight must be between 0.10 and 5.00.")

        # Composite tenant membership isolation
        from modules.platform_tenant.models import TenantMembership
        if self.tenant_id and self.mentor_id:
            if not TenantMembership.objects.filter(tenant_id=self.tenant_id, user_id=self.mentor_id).exists():
                raise ValidationError("Mentor is not a member of this tenant.")
        if self.tenant_id and self.student_id:
            if not TenantMembership.objects.filter(tenant_id=self.tenant_id, user_id=self.student_id).exists():
                raise ValidationError("Student is not a member of this tenant.")

        # PII Blacklist check on metadata
        _validate_pii_jsonb_field_17_19(self.metadata, "metadata")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.mentor_id}->{self.student_id}:{self.is_active}"


class SupportQueueItem(models.Model):
    """
    P3-VS17: Operational queue for mentor actions (due date, urgency, resolution notes).
    Anti-Ranking: Urgency is strictly operational, never a behavioral risk score.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="support_queue_items",
    )
    mentor_id = models.UUIDField(db_index=True)
    student_id = models.UUIDField(db_index=True)
    source_intervention = models.ForeignKey(
        SupportIntervention,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queue_items",
    )
    source_session = models.ForeignKey(
        CoachingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queue_items",
    )
    urgency_level = models.CharField(
        max_length=32,
        choices=SupportQueueUrgency.choices,
        default=SupportQueueUrgency.NORMAL,
    )
    queue_status = models.CharField(
        max_length=32,
        choices=SupportQueueStatus.choices,
        default=SupportQueueStatus.PENDING,
    )
    due_date = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_supportqueueitem"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_supportqueueitem_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(source_intervention__isnull=False) | Q(source_session__isnull=False),
                name="chk_supportqueue_origin_at_least_one",
            ),
            models.CheckConstraint(
                condition=Q(urgency_level__in=SupportQueueUrgency.values),
                name="chk_supportqueue_urgency",
            ),
            models.CheckConstraint(
                condition=Q(queue_status__in=SupportQueueStatus.values),
                name="chk_supportqueue_status",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(queue_status__in=[SupportQueueStatus.PENDING, SupportQueueStatus.IN_REVIEW]) & Q(resolved_at__isnull=True) & Q(resolution_notes__isnull=True)) |
                    (Q(queue_status__in=[SupportQueueStatus.RESOLVED, SupportQueueStatus.DISMISSED]) & Q(resolved_at__isnull=False))
                ),
                name="chk_supportqueue_resolved_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "mentor_id", "queue_status", "due_date"], name="idx_supportqueue_mentor_stat"),
            models.Index(fields=["tenant", "student_id"], name="idx_supportqueue_student"),
        ]

    def clean(self):
        super().clean()
        if not self.source_intervention_id and not self.source_session_id:
            raise ValidationError("Support queue item must have at least one origin: source_intervention or source_session.")
        if self.source_intervention_id and str(self.source_intervention.tenant_id) != str(self.tenant_id):
            raise ValidationError("Source intervention tenant mismatch.")
        if self.source_session_id and str(self.source_session.tenant_id) != str(self.tenant_id):
            raise ValidationError("Source session tenant mismatch.")
        if self.queue_status in (SupportQueueStatus.PENDING, SupportQueueStatus.IN_REVIEW):
            if self.resolved_at or self.resolution_notes:
                raise ValidationError("Pending or In-review queue items cannot have resolved_at or resolution_notes.")
        elif self.queue_status in (SupportQueueStatus.RESOLVED, SupportQueueStatus.DISMISSED):
            if not self.resolved_at:
                raise ValidationError("Resolved or dismissed queue item must specify resolved_at.")
        # PII Validation
        _validate_pii_jsonb_field_17_19(self.metadata, "metadata")
        _validate_pii_text_field_17_19(self.resolution_notes, "resolution_notes", 4000)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.mentor_id}:{self.queue_status}:{self.urgency_level}"


class LearningCheckIn(models.Model):
    """
    P3-VS18: Structured check-in sessions with status, scheduled timing, actual timing,
    and voluntary learner acknowledgement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_checkins",
    )
    mentor_id = models.UUIDField(db_index=True)
    student_id = models.UUIDField(db_index=True)
    caseload_assignment = models.ForeignKey(
        MentorCaseloadAssignment,
        on_delete=models.CASCADE,
        related_name="checkins",
    )
    status = models.CharField(
        max_length=32,
        choices=LearningCheckInStatus.choices,
        default=LearningCheckInStatus.SCHEDULED,
    )
    scheduled_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    rescheduled_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rescheduled_to",
    )
    meeting_link = models.CharField(max_length=500, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    student_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_learningcheckin"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_learningcheckin_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=LearningCheckInStatus.values),
                name="chk_checkin_status",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(actual_start__isnull=True) | Q(actual_end__isnull=True) | Q(actual_start__lte=models.F("actual_end"))) &
                    (Q(actual_start__isnull=True) | Q(scheduled_start__lte=models.F("actual_start")))
                ),
                name="chk_checkin_timing_order",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(student_acknowledged=False) & Q(acknowledged_at__isnull=True)) |
                    (Q(student_acknowledged=True) & Q(acknowledged_at__isnull=False))
                ),
                name="chk_checkin_acknowledgement",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "mentor_id", "scheduled_start"], name="idx_checkin_mentor_sched"),
            models.Index(fields=["tenant", "student_id", "scheduled_start"], name="idx_checkin_student_sched"),
        ]

    def clean(self):
        super().clean()
        if self.caseload_assignment_id and str(self.caseload_assignment.tenant_id) != str(self.tenant_id):
            raise ValidationError("Caseload assignment tenant mismatch.")
        if self.rescheduled_from_id and str(self.rescheduled_from.tenant_id) != str(self.tenant_id):
            raise ValidationError("Rescheduled from check-in tenant mismatch.")
        if self.actual_start and self.actual_end and self.actual_start > self.actual_end:
            raise ValidationError("actual_start must be before or equal to actual_end.")
        import datetime
        if self.actual_start and self.scheduled_start and self.actual_start < (self.scheduled_start - datetime.timedelta(minutes=15)):
            raise ValidationError("actual_start cannot precede scheduled_start by more than 15 minutes.")
        if self.student_acknowledged and not self.acknowledged_at:
            raise ValidationError("acknowledged_at must be provided when student_acknowledged is True.")
        if not self.student_acknowledged and self.acknowledged_at:
            raise ValidationError("acknowledged_at must be null when student_acknowledged is False.")
        if self.notes and len(self.notes.strip()) < 5:
            raise ValidationError("Notes must be at least 5 characters.")
        _validate_pii_jsonb_field_17_19(self.metadata, "metadata")
        _validate_pii_text_field_17_19(self.notes, "notes", 4000)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.mentor_id}:{self.student_id}:{self.status}:{self.scheduled_start}"


class FollowUpCommitment(models.Model):
    """
    P3-VS18: Mutual commitments resulting from a learning check-in.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="followup_commitments",
    )
    checkin = models.ForeignKey(
        LearningCheckIn,
        on_delete=models.CASCADE,
        related_name="commitments",
    )
    owner_role = models.CharField(
        max_length=16,
        choices=FollowUpCommitmentOwnerRole.choices,
    )
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_followupcommitment"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_followupcommitment_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(owner_role__in=FollowUpCommitmentOwnerRole.values),
                name="chk_commitment_owner",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(is_completed=False) & Q(completed_at__isnull=True)) |
                    (Q(is_completed=True) & Q(completed_at__isnull=False))
                ),
                name="chk_commitment_completed_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "checkin", "due_date"], name="idx_commitment_checkin_due"),
        ]

    def clean(self):
        super().clean()
        if self.checkin_id and str(self.checkin.tenant_id) != str(self.tenant_id):
            raise ValidationError("Checkin tenant mismatch.")
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters.")
        if self.is_completed and not self.completed_at:
            raise ValidationError("completed_at must be provided when commitment is completed.")
        if not self.is_completed and self.completed_at:
            raise ValidationError("completed_at must be null when commitment is not completed.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.owner_role}:{self.is_completed}:{self.title}"


class ProgramSupportAggregate(models.Model):
    """
    P3-VS19: Periodic aggregate analytics for program support effectiveness.
    Strict Invariant: Non-authoritative (chk_supportagg_non_authoritative).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="program_support_aggregates",
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    total_assigned_students = models.IntegerField(default=0)
    total_active_interventions = models.IntegerField(default=0)
    total_completed_checkins = models.IntegerField(default=0)
    average_response_time_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    support_coverage_ratio = models.DecimalField(max_digits=4, decimal_places=3, default=0.000)
    is_authoritative = models.BooleanField(default=False)
    aggregated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_programsupportaggregate"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_programsupportaggregate_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(is_authoritative=False),
                name="chk_supportagg_non_authoritative",
            ),
            models.CheckConstraint(
                condition=Q(period_start__lte=models.F("period_end")),
                name="chk_supportagg_period_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "-period_start", "-period_end"], name="idx_supportagg_period"),
        ]

    def clean(self):
        super().clean()
        if self.is_authoritative:
            raise ValidationError("ProgramSupportAggregate is strictly non-authoritative (is_authoritative must be False).")
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValidationError("period_start must be before or equal to period_end.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.period_start}->{self.period_end}:cov={self.support_coverage_ratio}"


class MentorOperationsAuditLog(models.Model):
    """
    P3-MACRO-EPIC-17-19: Forensic append-only audit trail for caseload assignments,
    support queue actions, check-ins, commitments, and aggregates with exact 5-way XOR.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="mentor_operations_audit_logs",
    )
    action_type = models.CharField(max_length=64, choices=MentorOperationsAuditAction.choices)
    actor_id = models.UUIDField(db_index=True)
    target_caseload = models.ForeignKey(
        MentorCaseloadAssignment,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_queue_item = models.ForeignKey(
        SupportQueueItem,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_checkin = models.ForeignKey(
        LearningCheckIn,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_commitment = models.ForeignKey(
        FollowUpCommitment,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    target_aggregate = models.ForeignKey(
        ProgramSupportAggregate,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_mentoroperationsauditlog"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_mentoropsaudit_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(action_type__in=MentorOperationsAuditAction.values),
                name="chk_mentoropsaudit_action_type",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_mentoropsaudit_actor_time"),
            models.Index(fields=["tenant", "target_caseload"], condition=Q(target_caseload__isnull=False), name="idx_mentoropsaudit_caseload"),
            models.Index(fields=["tenant", "target_queue_item"], condition=Q(target_queue_item__isnull=False), name="idx_mentoropsaudit_queue"),
            models.Index(fields=["tenant", "target_checkin"], condition=Q(target_checkin__isnull=False), name="idx_mentoropsaudit_checkin"),
            models.Index(fields=["tenant", "target_commitment"], condition=Q(target_commitment__isnull=False), name="idx_mentoropsaudit_commit"),
            models.Index(fields=["tenant", "target_aggregate"], condition=Q(target_aggregate__isnull=False), name="idx_mentoropsaudit_agg"),
        ]

    def clean(self):
        super().clean()
        target_ids = [
            (self.target_caseload_id, getattr(self, "target_caseload", None)),
            (self.target_queue_item_id, getattr(self, "target_queue_item", None)),
            (self.target_checkin_id, getattr(self, "target_checkin", None)),
            (self.target_commitment_id, getattr(self, "target_commitment", None)),
            (self.target_aggregate_id, getattr(self, "target_aggregate", None)),
        ]
        non_null_count = sum(1 for tid, _ in target_ids if tid is not None)
        if non_null_count != 1:
            raise ValidationError("Exactly one target entity must be specified for MentorOperationsAuditLog.")
        for tid, obj in target_ids:
            if tid is not None and obj is not None and str(obj.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target entity tenant mismatch.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("MentorOperationsAuditLog is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("MentorOperationsAuditLog records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.actor_id}:{self.action_type}:{self.created_at}"




# =============================================================================
# P3-MACRO-EPIC-20-22: CURRICULUM DELIVERY & PROGRAM OPERATIONS
# Sub-Slices: P3-VS20, P3-VS21, P3-VS22
# Canonical DDL: v1.1-CANONICAL
# Models (15):
#   VS20: CurriculumVersion, CourseRelease, ModuleReleaseSnapshot,
#         LessonReleaseSnapshot, ReleaseApprovalRecord, CurriculumReleaseAuditLog
#   VS21: CohortSchedule, LearningSession, SessionOccurrence,
#         SessionAttendanceState, SessionChangeRecord
#   VS22: ProgramDeliveryAggregate, CurriculumReleaseCoverage,
#         CohortScheduleHealth, DeliveryExceptionQueue
# =============================================================================

import re

PROHIBITED_PII_KEYS_20_22 = {
    "name", "phone", "email", "national_id", "location", "avatar_url",
    "phone_number", "mobile", "fingerprint", "face_id", "voice_sample",
    "bank_account", "iban", "credit_card", "card_number", "cvv",
    "password", "token", "secret", "ssn", "address"
}

PII_REGEX_20_22 = re.compile(
    r'(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)',
    re.IGNORECASE
)

def _validate_pii_text_field(val: str, field_name: str, max_len: int = 4000) -> None:
    if not val:
        return
    if len(val) > max_len:
        raise ValidationError(f"{field_name} exceeds max length of {max_len} characters.")
    if PII_REGEX_20_22.search(val):
        raise ValidationError(f"PII detected in {field_name}.")

def _validate_pii_jsonb_field(val: dict, field_name: str) -> None:
    if val is None:
        return
    if not isinstance(val, dict):
        raise ValidationError(f"{field_name} must be a valid JSON object.")
    bad_keys = set(val.keys()) & PROHIBITED_PII_KEYS_20_22
    if bad_keys:
        raise ValidationError(f"Prohibited PII keys in {field_name}: {bad_keys}")


# -----------------------------------------------------------------------------
# 1. P3-VS20: CURRICULUM VERSIONING & RELEASE GOVERNANCE
# -----------------------------------------------------------------------------

class CurriculumVersionStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    REVIEW = "REVIEW", "Review"
    APPROVED = "APPROVED", "Approved"
    PUBLISHED = "PUBLISHED", "Published"
    RETIRED = "RETIRED", "Retired"


class CurriculumReleaseApprovalDecision(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"


class CurriculumReleaseAuditAction(models.TextChoices):
    VERSION_CREATED = "VERSION_CREATED", "Version Created"
    VERSION_SUBMITTED = "VERSION_SUBMITTED", "Version Submitted"
    VERSION_APPROVED = "VERSION_APPROVED", "Version Approved"
    VERSION_REJECTED = "VERSION_REJECTED", "Version Rejected"
    VERSION_PUBLISHED = "VERSION_PUBLISHED", "Version Published"
    VERSION_RETIRED = "VERSION_RETIRED", "Version Retired"
    RELEASE_CREATED = "RELEASE_CREATED", "Release Created"
    RELEASE_ACTIVATED = "RELEASE_ACTIVATED", "Release Activated"
    RELEASE_DEACTIVATED = "RELEASE_DEACTIVATED", "Release Deactivated"


class CurriculumVersion(models.Model):
    """
    P3-VS20: Immutable semantic curriculum versioning with FSM governance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="curriculum_versions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.RESTRICT,
        related_name="curriculum_versions",
    )
    semver_major = models.IntegerField()
    semver_minor = models.IntegerField()
    semver_patch = models.IntegerField()
    version_tag = models.CharField(max_length=32)
    status = models.CharField(
        max_length=32,
        choices=CurriculumVersionStatus.choices,
        default=CurriculumVersionStatus.DRAFT,
    )
    created_by_id = models.UUIDField(null=True, blank=True)
    approved_by_id = models.UUIDField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_curriculumversion"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_curriculumversion_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course", "semver_major", "semver_minor", "semver_patch"],
                name="uq_curriculum_version_tenant_semver",
            ),
            models.CheckConstraint(
                condition=Q(status__in=CurriculumVersionStatus.values),
                name="chk_curriculum_version_status",
            ),
            models.CheckConstraint(
                condition=Q(semver_major__gte=0) & Q(semver_minor__gte=0) & Q(semver_patch__gte=0),
                name="chk_curriculum_semver_nonnegative",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status=CurriculumVersionStatus.PUBLISHED) & Q(published_at__isnull=False)) |
                    (~Q(status=CurriculumVersionStatus.PUBLISHED) & Q(published_at__isnull=True))
                ),
                name="chk_curriculumversion_published_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course", "status"], name="idx_curriculumversion_t_c_s"),
        ]

    def clean(self):
        super().clean()
        if self.course and str(self.course.tenant_id) != str(self.tenant_id):
            raise ValidationError("Course tenant mismatch.")
        if self.semver_major < 0 or self.semver_minor < 0 or self.semver_patch < 0:
            raise ValidationError("Semver numbers must be non-negative integers.")
        if self.status == CurriculumVersionStatus.PUBLISHED and not self.published_at:
            raise ValidationError("Published version must have published_at timestamp.")
        if self.status != CurriculumVersionStatus.PUBLISHED and self.published_at:
            raise ValidationError("Non-published version cannot have published_at timestamp.")
        _validate_pii_jsonb_field(self.metadata, "metadata")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.course_id}:{self.semver_major}.{self.semver_minor}.{self.semver_patch}:{self.status}"


class CourseRelease(models.Model):
    """
    P3-VS20: Mapping of an approved curriculum version to course delivery.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="course_releases",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.RESTRICT,
        related_name="releases",
    )
    curriculum_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.RESTRICT,
        related_name="releases",
    )
    release_title = models.CharField(max_length=255)
    release_notes = models.TextField(default="")
    is_active_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_courserelease"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_courserelease_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course", "is_active_default"], name="idx_courserelease_t_c_a"),
        ]

    def clean(self):
        super().clean()
        if self.course and str(self.course.tenant_id) != str(self.tenant_id):
            raise ValidationError("Course tenant mismatch.")
        if self.curriculum_version and str(self.curriculum_version.tenant_id) != str(self.tenant_id):
            raise ValidationError("CurriculumVersion tenant mismatch.")
        _validate_pii_text_field(self.release_title, "release_title", 255)
        _validate_pii_text_field(self.release_notes, "release_notes", 4000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.course_id}:{self.release_title}:active={self.is_active_default}"


class ModuleReleaseSnapshot(models.Model):
    """
    P3-VS20: Immutable frozen snapshot of module hierarchy and content.
    Snapshot provenance exemption: source_module_id is unconstrained by design.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="module_release_snapshots",
    )
    curriculum_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.RESTRICT,
        related_name="module_snapshots",
    )
    source_module_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    order_index = models.IntegerField(default=0)
    snapshot_payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_modulereleasesnapshot"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_modulereleasesnapshot_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "curriculum_version", "order_index"], name="idx_modulereleasesnap_v_o"),
        ]

    def clean(self):
        super().clean()
        if self.curriculum_version and str(self.curriculum_version.tenant_id) != str(self.tenant_id):
            raise ValidationError("CurriculumVersion tenant mismatch.")
        _validate_pii_text_field(self.title, "title", 255)
        _validate_pii_jsonb_field(self.snapshot_payload, "snapshot_payload")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("ModuleReleaseSnapshot is strictly immutable.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("ModuleReleaseSnapshot cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.curriculum_version_id}:{self.order_index}:{self.title}"


class LessonReleaseSnapshot(models.Model):
    """
    P3-VS20: Immutable frozen snapshot of lesson content hash and delivery payload.
    Snapshot provenance exemption: source_lesson_id is unconstrained by design.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="lesson_release_snapshots",
    )
    module_snapshot = models.ForeignKey(
        ModuleReleaseSnapshot,
        on_delete=models.RESTRICT,
        related_name="lesson_snapshots",
    )
    source_lesson_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    order_index = models.IntegerField(default=0)
    content_hash = models.CharField(max_length=64)
    snapshot_payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_lessonreleasesnapshot"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_lessonreleasesnapshot_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "module_snapshot", "order_index"], name="idx_lessonreleasesnap_m_o"),
        ]

    def clean(self):
        super().clean()
        if self.module_snapshot and str(self.module_snapshot.tenant_id) != str(self.tenant_id):
            raise ValidationError("ModuleReleaseSnapshot tenant mismatch.")
        _validate_pii_text_field(self.title, "title", 255)
        _validate_pii_jsonb_field(self.snapshot_payload, "snapshot_payload")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("LessonReleaseSnapshot is strictly immutable.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("LessonReleaseSnapshot cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.module_snapshot_id}:{self.order_index}:{self.title}"


class ReleaseApprovalRecord(models.Model):
    """
    P3-VS20: Formal curriculum release approval audit record (Append-Only).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="release_approvals",
    )
    curriculum_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.RESTRICT,
        related_name="approvals",
    )
    reviewer_id = models.UUIDField(db_index=True)
    decision = models.CharField(max_length=32, choices=CurriculumReleaseApprovalDecision.choices)
    review_comments = models.TextField(default="")
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_releaseapprovalrecord"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_releaseapprovalrecord_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(decision__in=CurriculumReleaseApprovalDecision.values),
                name="chk_releaseapproval_decision",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "curriculum_version", "-reviewed_at"], name="idx_releaseapproval_t_v_t"),
        ]

    def clean(self):
        super().clean()
        try:
            if self.curriculum_version and str(self.curriculum_version.tenant_id) != str(self.tenant_id):
                raise ValidationError("CurriculumVersion tenant mismatch.")
        except Exception:
            pass
        _validate_pii_text_field(self.review_comments, "review_comments", 4000)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("ReleaseApprovalRecord is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("ReleaseApprovalRecord cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.curriculum_version_id}:{self.reviewer_id}:{self.decision}"


class CurriculumReleaseAuditLog(models.Model):
    """
    P3-VS20: Forensic append-only audit trail for curriculum governance.
    Strict Invariant: Exact XOR between curriculum_version and course_release.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="curriculum_audit_logs",
    )
    curriculum_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    course_release = models.ForeignKey(
        CourseRelease,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    actor_id = models.UUIDField(db_index=True)
    action = models.CharField(max_length=64)
    previous_state = models.CharField(max_length=32, null=True, blank=True)
    new_state = models.CharField(max_length=32, null=True, blank=True)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_curriculumreleaseauditlog"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_curriculumreleaseauditlog_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_curraudit_tenant_actor"),
            models.Index(fields=["tenant", "curriculum_version"], condition=Q(curriculum_version__isnull=False), name="idx_curraudit_version"),
            models.Index(fields=["tenant", "course_release"], condition=Q(course_release__isnull=False), name="idx_curraudit_release"),
        ]

    def clean(self):
        super().clean()
        targets = [self.curriculum_version, self.course_release]
        non_null_count = sum(1 for t in targets if t is not None)
        if non_null_count != 1:
            raise ValidationError("Exactly one target entity must be set (num_nonnulls = 1).")
        for t in targets:
            if t is not None and str(t.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target entity tenant mismatch.")
        _validate_pii_jsonb_field(self.details, "details")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("CurriculumReleaseAuditLog is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("CurriculumReleaseAuditLog cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.actor_id}:{self.action}:{self.created_at}"


# -----------------------------------------------------------------------------
# 2. P3-VS21: COHORT SCHEDULE & LEARNING SESSION ORCHESTRATION
# -----------------------------------------------------------------------------

class LearningSessionStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    IN_SESSION = "IN_SESSION", "In Session"
    COMPLETED = "COMPLETED", "Completed"
    RESCHEDULED = "RESCHEDULED", "Rescheduled"
    CANCELLED = "CANCELLED", "Cancelled"


class SessionOccurrenceStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONDUCTED = "CONDUCTED", "Conducted"
    MISSED = "MISSED", "Missed"
    SUBSTITUTE_CONDUCTED = "SUBSTITUTE_CONDUCTED", "Substitute Conducted"


class SessionAttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Present"
    ABSENT = "ABSENT", "Absent"
    EXCUSED = "EXCUSED", "Excused"
    LATE = "LATE", "Late"


class SessionChangeType(models.TextChoices):
    RESCHEDULED = "RESCHEDULED", "Rescheduled"
    CANCELLED = "CANCELLED", "Cancelled"
    MENTOR_REASSIGNED = "MENTOR_REASSIGNED", "Mentor Reassigned"
    TOPIC_UPDATED = "TOPIC_UPDATED", "Topic Updated"


class CohortSchedule(models.Model):
    """
    P3-VS21: Delivery schedule for a cohort linked to a specific CourseRelease.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="cohort_schedules",
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.RESTRICT,
        related_name="schedules",
    )
    course_release = models.ForeignKey(
        CourseRelease,
        on_delete=models.RESTRICT,
        related_name="cohort_schedules",
    )
    schedule_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    recurrence_rule = models.CharField(max_length=128, default="WEEKLY")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_cohortschedule"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_cohortschedule_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(start_date__lte=models.F("end_date")),
                name="chk_cohortschedule_dates_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "cohort", "is_active"], name="idx_cohortsched_t_c_a"),
        ]

    def clean(self):
        super().clean()
        try:
            if self.cohort and str(self.cohort.tenant_id) != str(self.tenant_id):
                raise ValidationError("Cohort tenant mismatch.")
        except Exception:
            pass
        try:
            if self.course_release and str(self.course_release.tenant_id) != str(self.tenant_id):
                raise ValidationError("CourseRelease tenant mismatch.")
        except Exception:
            pass
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("start_date must be before or equal to end_date.")
        _validate_pii_text_field(self.schedule_title, "schedule_title", 255)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_id}:{self.schedule_title}:active={self.is_active}"


class LearningSession(models.Model):
    """
    P3-VS21: Orchestrated session instances scheduled for delivery.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_sessions",
    )
    cohort_schedule = models.ForeignKey(
        CohortSchedule,
        on_delete=models.RESTRICT,
        related_name="sessions",
    )
    session_title = models.CharField(max_length=255)
    session_order = models.IntegerField(default=1)
    lesson_snapshot = models.ForeignKey(
        LessonReleaseSnapshot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )
    assigned_mentor_id = models.UUIDField(null=True, blank=True)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    status = models.CharField(
        max_length=32,
        choices=LearningSessionStatus.choices,
        default=LearningSessionStatus.SCHEDULED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_learningsession"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_learningsession_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=LearningSessionStatus.values),
                name="chk_learningsession_status",
            ),
            models.CheckConstraint(
                condition=Q(scheduled_start__lt=models.F("scheduled_end")),
                name="chk_learningsession_timing_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "cohort_schedule", "scheduled_start"], name="idx_learnsession_sched_time"),
            models.Index(fields=["tenant", "assigned_mentor_id", "status"], name="idx_learnsession_mentor_stat"),
        ]

    def clean(self):
        super().clean()
        if self.cohort_schedule and str(self.cohort_schedule.tenant_id) != str(self.tenant_id):
            raise ValidationError("CohortSchedule tenant mismatch.")
        if self.lesson_snapshot and str(self.lesson_snapshot.tenant_id) != str(self.tenant_id):
            raise ValidationError("LessonReleaseSnapshot tenant mismatch.")
        if self.scheduled_start and self.scheduled_end and self.scheduled_start >= self.scheduled_end:
            raise ValidationError("scheduled_start must be strictly before scheduled_end.")
        _validate_pii_text_field(self.session_title, "session_title", 255)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_schedule_id}:{self.session_title}:{self.status}"


class SessionOccurrence(models.Model):
    """
    P3-VS21: Operational execution record of a learning session occurrence.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="session_occurrences",
    )
    learning_session = models.ForeignKey(
        LearningSession,
        on_delete=models.CASCADE,
        related_name="occurrences",
    )
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    occurrence_status = models.CharField(
        max_length=32,
        choices=SessionOccurrenceStatus.choices,
        default=SessionOccurrenceStatus.PENDING,
    )
    attendance_count = models.IntegerField(default=0)
    operational_notes = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_sessionoccurrence"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_sessionoccurrence_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(occurrence_status__in=SessionOccurrenceStatus.values),
                name="chk_sessionoccurrence_status",
            ),
            models.CheckConstraint(
                condition=Q(actual_start__isnull=True) | Q(actual_end__isnull=True) | Q(actual_start__lte=models.F("actual_end")),
                name="chk_session_timing_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "learning_session", "actual_start"], name="idx_sessoccur_t_s_a"),
        ]

    def clean(self):
        super().clean()
        try:
            if self.learning_session and str(self.learning_session.tenant_id) != str(self.tenant_id):
                raise ValidationError("LearningSession tenant mismatch.")
        except Exception:
            pass
        if self.actual_start and self.actual_end and self.actual_start > self.actual_end:
            raise ValidationError("actual_start must be before or equal to actual_end.")
        _validate_pii_text_field(self.operational_notes, "operational_notes", 4000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.learning_session_id}:{self.occurrence_status}"


class SessionAttendanceState(models.Model):
    """
    P3-VS21: Synthetic session attendance record (strictly non-punitive, anti-ranking).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="session_attendance_records",
    )
    session_occurrence = models.ForeignKey(
        SessionOccurrence,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    student_id = models.UUIDField(db_index=True)
    status = models.CharField(
        max_length=32,
        choices=SessionAttendanceStatus.choices,
        default=SessionAttendanceStatus.PRESENT,
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_sessionattendancestate"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_sessionattendancestate_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "session_occurrence", "student_id"],
                name="uq_session_attendance_student",
            ),
            models.CheckConstraint(
                condition=Q(status__in=SessionAttendanceStatus.values),
                name="chk_sessionattendance_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="idx_sessattendance_t_s_s"),
        ]

    def clean(self):
        super().clean()
        if self.session_occurrence and str(self.session_occurrence.tenant_id) != str(self.tenant_id):
            raise ValidationError("SessionOccurrence tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.session_occurrence_id}:{self.student_id}:{self.status}"


class SessionChangeRecord(models.Model):
    """
    P3-VS21: Append-only audit trail for session rescheduling and cancellation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="session_change_records",
    )
    learning_session = models.ForeignKey(
        LearningSession,
        on_delete=models.CASCADE,
        related_name="change_records",
    )
    changed_by_id = models.UUIDField(db_index=True)
    change_type = models.CharField(max_length=32, choices=SessionChangeType.choices)
    original_start = models.DateTimeField(null=True, blank=True)
    new_start = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_sessionchangerecord"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_sessionchangerecord_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(change_type__in=SessionChangeType.values),
                name="chk_sessionchange_type",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "learning_session", "-created_at"], name="idx_sesschange_t_s_c"),
        ]

    def clean(self):
        super().clean()
        if self.learning_session and str(self.learning_session.tenant_id) != str(self.tenant_id):
            raise ValidationError("LearningSession tenant mismatch.")
        _validate_pii_text_field(self.reason, "reason", 2000)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("SessionChangeRecord is strictly append-only.")
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("SessionChangeRecord cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.learning_session_id}:{self.change_type}:{self.created_at}"


# -----------------------------------------------------------------------------
# 3. P3-VS22: PROGRAM DELIVERY QUALITY & OPERATIONS CONTROL CENTER
# -----------------------------------------------------------------------------

class CohortScheduleHealthStatus(models.TextChoices):
    ON_TRACK = "ON_TRACK", "On Track"
    ATTENTION_NEEDED = "ATTENTION_NEEDED", "Attention Needed"
    AT_RISK = "AT_RISK", "At Risk"
    CRITICAL_DELAY = "CRITICAL_DELAY", "Critical Delay"


class DeliveryExceptionSeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class DeliveryExceptionStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    INVESTIGATING = "INVESTIGATING", "Investigating"
    RESOLVED = "RESOLVED", "Resolved"
    IGNORED = "IGNORED", "Ignored"


class ProgramDeliveryAggregate(models.Model):
    """
    P3-VS22: Non-authoritative delivery progress aggregate.
    Strict Invariant: is_authoritative MUST be False. Zero student ranking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="delivery_aggregates",
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        related_name="delivery_aggregates",
    )
    total_sessions = models.IntegerField(default=0)
    completed_sessions = models.IntegerField(default=0)
    cancelled_sessions = models.IntegerField(default=0)
    rescheduled_sessions = models.IntegerField(default=0)
    active_release_version = models.CharField(max_length=32, default="")
    is_authoritative = models.BooleanField(default=False)
    computed_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "learning_programdeliveryaggregate"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_programdeliveryaggregate_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "cohort"],
                name="uq_deliveryagg_cohort",
            ),
            models.CheckConstraint(
                condition=Q(is_authoritative=False),
                name="chk_deliveryagg_non_authoritative",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "-computed_at"], name="idx_deliveryagg_t_c"),
        ]

    def clean(self):
        super().clean()
        if self.is_authoritative:
            raise ValidationError("ProgramDeliveryAggregate is strictly non-authoritative.")
        if self.cohort and str(self.cohort.tenant_id) != str(self.tenant_id):
            raise ValidationError("Cohort tenant mismatch.")
        _validate_pii_jsonb_field(self.metadata, "metadata")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_id}:done={self.completed_sessions}/{self.total_sessions}"


class CurriculumReleaseCoverage(models.Model):
    """
    P3-VS22: Adoption projection of curriculum releases across cohorts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="release_coverages",
    )
    curriculum_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.CASCADE,
        related_name="coverages",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="release_coverages",
    )
    cohorts_adopted_count = models.IntegerField(default=0)
    active_learners_count = models.IntegerField(default=0)
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_curriculumreleasecoverage"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_curriculumreleasecoverage_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "curriculum_version"],
                name="uq_releasecoverage_version",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course"], name="idx_currcov_t_course"),
        ]

    def clean(self):
        super().clean()
        if self.curriculum_version and str(self.curriculum_version.tenant_id) != str(self.tenant_id):
            raise ValidationError("CurriculumVersion tenant mismatch.")
        if self.course and str(self.course.tenant_id) != str(self.tenant_id):
            raise ValidationError("Course tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.curriculum_version_id}:cohorts={self.cohorts_adopted_count}"


class CohortScheduleHealth(models.Model):
    """
    P3-VS22: Health and delivery exception projection for cohort schedules.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="cohort_health_projections",
    )
    cohort_schedule = models.ForeignKey(
        CohortSchedule,
        on_delete=models.CASCADE,
        related_name="health_projections",
    )
    health_status = models.CharField(
        max_length=32,
        choices=CohortScheduleHealthStatus.choices,
        default=CohortScheduleHealthStatus.ON_TRACK,
    )
    pending_sessions_count = models.IntegerField(default=0)
    delayed_sessions_count = models.IntegerField(default=0)
    missed_occurrences_count = models.IntegerField(default=0)
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_cohortschedulehealth"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_cohortschedulehealth_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "cohort_schedule"],
                name="uq_cohortschedulehealth_schedule",
            ),
            models.CheckConstraint(
                condition=Q(health_status__in=CohortScheduleHealthStatus.values),
                name="chk_cohortschedulehealth_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "health_status"], name="idx_schedhealth_t_status"),
        ]

    def clean(self):
        super().clean()
        if self.cohort_schedule and str(self.cohort_schedule.tenant_id) != str(self.tenant_id):
            raise ValidationError("CohortSchedule tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_schedule_id}:{self.health_status}"


class DeliveryExceptionQueue(models.Model):
    """
    P3-VS22: Operational exception tracking queue for curriculum delivery interruptions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="delivery_exceptions",
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.RESTRICT,
        related_name="delivery_exceptions",
    )
    learning_session = models.ForeignKey(
        LearningSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_exceptions",
    )
    exception_type = models.CharField(max_length=64)
    severity = models.CharField(
        max_length=32,
        choices=DeliveryExceptionSeverity.choices,
        default=DeliveryExceptionSeverity.MEDIUM,
    )
    status = models.CharField(
        max_length=32,
        choices=DeliveryExceptionStatus.choices,
        default=DeliveryExceptionStatus.OPEN,
    )
    description = models.TextField()
    resolved_by_id = models.UUIDField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_deliveryexceptionqueue"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_deliveryexceptionqueue_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(severity__in=DeliveryExceptionSeverity.values),
                name="chk_deliveryexception_severity",
            ),
            models.CheckConstraint(
                condition=Q(status__in=DeliveryExceptionStatus.values),
                name="chk_deliveryexception_status",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status__in=[DeliveryExceptionStatus.OPEN, DeliveryExceptionStatus.INVESTIGATING]) & Q(resolved_at__isnull=True) & Q(resolved_by_id__isnull=True)) |
                    (Q(status__in=[DeliveryExceptionStatus.RESOLVED, DeliveryExceptionStatus.IGNORED]) & Q(resolved_at__isnull=False))
                ),
                name="chk_deliveryexception_resolved_order",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status", "severity", "-created_at"], name="idx_delexcept_t_s_s_c"),
        ]

    def clean(self):
        super().clean()
        if self.cohort and str(self.cohort.tenant_id) != str(self.tenant_id):
            raise ValidationError("Cohort tenant mismatch.")
        if self.learning_session and str(self.learning_session.tenant_id) != str(self.tenant_id):
            raise ValidationError("LearningSession tenant mismatch.")
        if self.status in [DeliveryExceptionStatus.OPEN, DeliveryExceptionStatus.INVESTIGATING]:
            if self.resolved_at or self.resolved_by_id:
                raise ValidationError("Open or investigating exception cannot have resolved_at or resolved_by_id.")
        elif self.status in [DeliveryExceptionStatus.RESOLVED, DeliveryExceptionStatus.IGNORED]:
            if not self.resolved_at:
                raise ValidationError("Resolved or ignored exception must have resolved_at timestamp.")
        _validate_pii_text_field(self.description, "description", 4000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_id}:{self.exception_type}:{self.status}"


# =============================================================================
# P3-MACRO-EPIC-23-25: CURRICULUM AUTHORING, QUALITY & RELEASE OPERATIONS
# Sub-Slices: P3-VS23, P3-VS24, P3-VS25
# Canonical DDL: v1.1-CANONICAL-CLAUDE-HARDENED
# Models (19):
#   VS23: CurriculumDraftWorkspace, ContentChangeSet, EditorialReview,
#         ReviewComment, ReviewResolution, AuthorAssignment, ChangeApprovalRecord
#   VS24: AssessmentBlueprint, LearningObjectiveMapping, RubricDefinition,
#         RubricCriterion, AssessmentReleaseBinding, RubricReviewRecord
#   VS25: CurriculumChangeImpact, ReleaseReadinessCheck, ReleaseReadinessGate,
#         CohortRollforwardPlan, CurriculumMigrationDecision, ReleaseExceptionRecord
# =============================================================================

class CurriculumDraftWorkspaceStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    SUBMITTED = "SUBMITTED", "Submitted"
    ARCHIVED = "ARCHIVED", "Archived"


class ContentChangeSetStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    IN_REVIEW = "IN_REVIEW", "In Review"
    CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"
    APPROVED = "APPROVED", "Approved"
    MERGED_TO_RELEASE = "MERGED_TO_RELEASE", "Merged to Release"


class EditorialReviewDecision(models.TextChoices):
    PENDING = "PENDING", "Pending"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class ReviewResolutionStatus(models.TextChoices):
    RESOLVED = "RESOLVED", "Resolved"
    WAIVED = "WAIVED", "Waived"
    DEFERRED = "DEFERRED", "Deferred"


class AuthorAssignmentRole(models.TextChoices):
    PRIMARY_AUTHOR = "PRIMARY_AUTHOR", "Primary Author"
    CONTRIBUTOR = "CONTRIBUTOR", "Contributor"
    CURATOR = "CURATOR", "Curator"


class ChangeApprovalVerdict(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    CONDITIONALLY_APPROVED = "CONDITIONALLY_APPROVED", "Conditionally Approved"


class AssessmentBlueprintStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    DRAFT = "DRAFT", "Draft"
    SUPERSEDED = "SUPERSEDED", "Superseded"
    RETIRED = "RETIRED", "Retired"


class BloomTaxonomyLevel(models.TextChoices):
    REMEMBER = "REMEMBER", "Remember"
    UNDERSTAND = "UNDERSTAND", "Understand"
    APPLY = "APPLY", "Apply"
    ANALYZE = "ANALYZE", "Analyze"
    EVALUATE = "EVALUATE", "Evaluate"
    CREATE = "CREATE", "Create"


class RubricDefinitionStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    SUPERSEDED = "SUPERSEDED", "Superseded"
    RETIRED = "RETIRED", "Retired"


class RubricReviewVerdict(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REVISION_REQUESTED = "REVISION_REQUESTED", "Revision Requested"


class CurriculumChangeImpactLevel(models.TextChoices):
    PATCH = "PATCH", "Patch"
    MINOR = "MINOR", "Minor"
    MAJOR = "MAJOR", "Major"
    BREAKING = "BREAKING", "Breaking"


class ReleaseReadinessStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PASSED = "PASSED", "Passed"
    FAILED = "FAILED", "Failed"
    WAIVED = "WAIVED", "Waived"


class CohortRollforwardMode(models.TextChoices):
    FUTURE_MODULES_ONLY = "FUTURE_MODULES_ONLY", "Future Modules Only"
    NEXT_COHORT_ONLY = "NEXT_COHORT_ONLY", "Next Cohort Only"
    EXPLICIT_APPROVAL_REQUIRED = "EXPLICIT_APPROVAL_REQUIRED", "Explicit Approval Required"


class CohortRollforwardStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    APPROVED = "APPROVED", "Approved"
    APPLIED = "APPLIED", "Applied"
    CANCELLED = "CANCELLED", "Cancelled"


class CurriculumMigrationDecisionChoice(models.TextChoices):
    PROCEED = "PROCEED", "Proceed"
    HALT = "HALT", "Halt"
    EXCEPTION_REQUIRED = "EXCEPTION_REQUIRED", "Exception Required"


# -----------------------------------------------------------------------------
# 1. P3-VS23: CURRICULUM AUTHORING & EDITORIAL WORKFLOW
# -----------------------------------------------------------------------------

class CurriculumDraftWorkspace(models.Model):
    """
    P3-VS23: Draft authoring workspace bound to course and base curriculum version.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="curriculum_draft_workspaces",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.RESTRICT,
        related_name="draft_workspaces",
    )
    base_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.RESTRICT,
        related_name="derived_workspaces",
    )
    workspace_title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=32,
        choices=CurriculumDraftWorkspaceStatus.choices,
        default=CurriculumDraftWorkspaceStatus.ACTIVE,
    )
    created_by_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_curriculumdraftworkspace"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_curriculumdraftworkspace_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=CurriculumDraftWorkspaceStatus.values),
                name="chk_draftworkspace_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course", "status"], name="idx_draftws_t_c_s"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "course") and self.course is not None:
            if str(self.course.tenant_id) != str(self.tenant_id):
                raise ValidationError("Course tenant mismatch.")
        if hasattr(self, "base_version") and self.base_version is not None:
            if str(self.base_version.tenant_id) != str(self.tenant_id):
                raise ValidationError("Base CurriculumVersion tenant mismatch.")
        _validate_pii_jsonb_field(self.metadata, "metadata")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.workspace_title}:{self.status}"


class ContentChangeSet(models.Model):
    """
    P3-VS23: Structured batch of content changes with editorial FSM.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="content_change_sets",
    )
    workspace = models.ForeignKey(
        CurriculumDraftWorkspace,
        on_delete=models.CASCADE,
        related_name="change_sets",
    )
    title = models.CharField(max_length=255)
    change_summary = models.TextField(default="", blank=True)
    status = models.CharField(
        max_length=32,
        choices=ContentChangeSetStatus.choices,
        default=ContentChangeSetStatus.DRAFT,
    )
    author_id = models.UUIDField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_contentchangeset"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_contentchangeset_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=ContentChangeSetStatus.values),
                name="chk_contentchangeset_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "workspace", "status"], name="idx_cchangeset_t_w_s"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "workspace") and self.workspace is not None:
            if str(self.workspace.tenant_id) != str(self.tenant_id):
                raise ValidationError("CurriculumDraftWorkspace tenant mismatch.")
        _validate_pii_text_field(self.change_summary, "change_summary", 5000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.title}:{self.status}"


class EditorialReview(models.Model):
    """
    P3-VS23: Formal peer review record enforcing separation of duties.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="editorial_reviews",
    )
    change_set = models.ForeignKey(
        ContentChangeSet,
        on_delete=models.CASCADE,
        related_name="editorial_reviews",
    )
    reviewer_id = models.UUIDField(null=True, blank=True)
    decision = models.CharField(
        max_length=32,
        choices=EditorialReviewDecision.choices,
        default=EditorialReviewDecision.PENDING,
    )
    review_notes = models.TextField(default="", blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_editorialreview"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_editorialreview_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(decision__in=EditorialReviewDecision.values),
                name="chk_editorialreview_decision",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "change_set", "decision"], name="idx_edreview_t_cs_d"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "change_set") and self.change_set is not None:
            if str(self.change_set.tenant_id) != str(self.tenant_id):
                raise ValidationError("ContentChangeSet tenant mismatch.")
        _validate_pii_text_field(self.review_notes, "review_notes", 5000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.change_set_id}:{self.decision}"


class ReviewComment(models.Model):
    """
    P3-VS23: Targeted editorial comment on draft curriculum entities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="review_comments",
    )
    review = models.ForeignKey(
        EditorialReview,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author_id = models.UUIDField(null=True, blank=True)
    comment_text = models.TextField()
    target_entity = models.CharField(max_length=64)
    target_entity_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_reviewcomment"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_reviewcomment_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "review", "-created_at"], name="idx_revcomment_t_r_c"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "review") and self.review is not None:
            if str(self.review.tenant_id) != str(self.tenant_id):
                raise ValidationError("EditorialReview tenant mismatch.")
        _validate_pii_text_field(self.comment_text, "comment_text", 3000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.target_entity}:{self.target_entity_id}"


class ReviewResolution(models.Model):
    """
    P3-VS23: Official resolution record sign-off on review feedback.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="review_resolutions",
    )
    review = models.ForeignKey(
        EditorialReview,
        on_delete=models.CASCADE,
        related_name="resolutions",
    )
    resolver_id = models.UUIDField(null=True, blank=True)
    resolution_status = models.CharField(
        max_length=32,
        choices=ReviewResolutionStatus.choices,
        default=ReviewResolutionStatus.RESOLVED,
    )
    resolution_notes = models.TextField(default="", blank=True)
    resolved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_reviewresolution"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_reviewresolution_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(resolution_status__in=ReviewResolutionStatus.values),
                name="chk_reviewresolution_status",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "review") and self.review is not None:
            if str(self.review.tenant_id) != str(self.tenant_id):
                raise ValidationError("EditorialReview tenant mismatch.")
        _validate_pii_text_field(self.resolution_notes, "resolution_notes", 3000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.review_id}:{self.resolution_status}"


class AuthorAssignment(models.Model):
    """
    P3-VS23: Author assignment to curriculum draft workspaces.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="author_assignments",
    )
    workspace = models.ForeignKey(
        CurriculumDraftWorkspace,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    author_id = models.UUIDField(null=True, blank=True)
    assigned_role = models.CharField(
        max_length=32,
        choices=AuthorAssignmentRole.choices,
        default=AuthorAssignmentRole.PRIMARY_AUTHOR,
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_authorassignment"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_authorassignment_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "workspace", "author_id"],
                name="uq_authorassignment_workspace_author",
            ),
            models.CheckConstraint(
                condition=Q(assigned_role__in=AuthorAssignmentRole.values),
                name="chk_authorassignment_role",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "workspace") and self.workspace is not None:
            if str(self.workspace.tenant_id) != str(self.tenant_id):
                raise ValidationError("CurriculumDraftWorkspace tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.workspace_id}:{self.author_id}:{self.assigned_role}"


class ChangeApprovalRecord(models.Model):
    """
    P3-VS23: Cryptographically hashed immutable audit trail of content change set approvals.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="change_approval_records",
    )
    change_set = models.ForeignKey(
        ContentChangeSet,
        on_delete=models.RESTRICT,
        related_name="approvals",
    )
    approver_id = models.UUIDField(null=True, blank=True)
    approval_verdict = models.CharField(
        max_length=32,
        choices=ChangeApprovalVerdict.choices,
    )
    approval_hash = models.CharField(max_length=64)
    justification = models.TextField(default="", blank=True)
    approved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_changeapprovalrecord"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_changeapprovalrecord_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(approval_verdict__in=ChangeApprovalVerdict.values),
                name="chk_changeapproval_verdict",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "change_set"], name="idx_changeappr_t_cs"),
            models.Index(fields=["tenant", "approver_id"], name="idx_changeappr_t_a"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "change_set") and self.change_set is not None:
            if str(self.change_set.tenant_id) != str(self.tenant_id):
                raise ValidationError("ContentChangeSet tenant mismatch.")
        _validate_pii_text_field(self.justification, "justification", 3000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.change_set_id}:{self.approval_verdict}"


# -----------------------------------------------------------------------------
# 2. P3-VS24: LEARNING ASSESSMENT BLUEPRINT & RUBRIC GOVERNANCE
# -----------------------------------------------------------------------------

class AssessmentBlueprint(models.Model):
    """
    P3-VS24: Course-level assessment blueprint defining evaluation architecture.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="assessment_blueprints",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.RESTRICT,
        related_name="assessment_blueprints",
    )
    blueprint_title = models.CharField(max_length=255)
    version_tag = models.CharField(max_length=32, default="v1.0")
    status = models.CharField(
        max_length=32,
        choices=AssessmentBlueprintStatus.choices,
        default=AssessmentBlueprintStatus.ACTIVE,
    )
    pedagogical_intent = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_assessmentblueprint"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_assessmentblueprint_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=AssessmentBlueprintStatus.values),
                name="chk_assessmentblueprint_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "course", "status"], name="idx_assessbp_t_c_s"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "course") and self.course is not None:
            if str(self.course.tenant_id) != str(self.tenant_id):
                raise ValidationError("Course tenant mismatch.")
        _validate_pii_text_field(self.pedagogical_intent, "pedagogical_intent", 4000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.blueprint_title}:{self.version_tag}"


class LearningObjectiveMapping(models.Model):
    """
    P3-VS24: Objective alignment mapping to Bloom's taxonomy and weight.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="learning_objective_mappings",
    )
    blueprint = models.ForeignKey(
        AssessmentBlueprint,
        on_delete=models.CASCADE,
        related_name="objective_mappings",
    )
    objective_code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    bloom_taxonomy_level = models.CharField(
        max_length=32,
        choices=BloomTaxonomyLevel.choices,
        default=BloomTaxonomyLevel.APPLY,
    )
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_learningobjectivemapping"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_learningobjectivemapping_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(weight_percentage__gt=0) & Q(weight_percentage__lte=100.00),
                name="chk_objectivemapping_weight",
            ),
            models.CheckConstraint(
                condition=Q(bloom_taxonomy_level__in=BloomTaxonomyLevel.values),
                name="chk_objectivemapping_taxonomy",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "blueprint") and self.blueprint is not None:
            if str(self.blueprint.tenant_id) != str(self.tenant_id):
                raise ValidationError("AssessmentBlueprint tenant mismatch.")
        _validate_pii_text_field(self.title, "title", 255)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.objective_code}:{self.bloom_taxonomy_level}"


class RubricDefinition(models.Model):
    """
    P3-VS24: Pure qualitative evaluation standards with strict anti-ranking invariant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="rubric_definitions",
    )
    blueprint = models.ForeignKey(
        AssessmentBlueprint,
        on_delete=models.RESTRICT,
        related_name="rubrics",
    )
    rubric_title = models.CharField(max_length=255)
    scale_type = models.CharField(max_length=32, default="QUALITATIVE_STANDARD")
    status = models.CharField(
        max_length=32,
        choices=RubricDefinitionStatus.choices,
        default=RubricDefinitionStatus.DRAFT,
    )
    is_anti_ranking_compliant = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_rubricdefinition"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_rubricdefinition_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=RubricDefinitionStatus.values),
                name="chk_rubricdefinition_status",
            ),
            models.CheckConstraint(
                condition=Q(is_anti_ranking_compliant=True),
                name="chk_rubric_anti_ranking",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "blueprint", "status"], name="idx_rubricdef_t_bp_s"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "blueprint") and self.blueprint is not None:
            if str(self.blueprint.tenant_id) != str(self.tenant_id):
                raise ValidationError("AssessmentBlueprint tenant mismatch.")
        if not self.is_anti_ranking_compliant:
            raise ValidationError("RubricDefinition must enforce is_anti_ranking_compliant=True.")
        _validate_pii_text_field(self.rubric_title, "rubric_title", 255)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.rubric_title}:{self.status}"


class RubricCriterion(models.Model):
    """
    P3-VS24: Granular evaluation criterion with qualitative mastery levels.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="rubric_criteria",
    )
    rubric = models.ForeignKey(
        RubricDefinition,
        on_delete=models.CASCADE,
        related_name="criteria",
    )
    criterion_title = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    evaluation_levels = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_rubriccriterion"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_rubriccriterion_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(weight_percentage__gt=0) & Q(weight_percentage__lte=100.00),
                name="chk_rubriccriterion_weight",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "rubric") and self.rubric is not None:
            if str(self.rubric.tenant_id) != str(self.tenant_id):
                raise ValidationError("RubricDefinition tenant mismatch.")
        _validate_pii_text_field(self.description, "description", 4000)
        if not isinstance(self.evaluation_levels, list):
            raise ValidationError("evaluation_levels must be a list.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.criterion_title}:{self.weight_percentage}%"


class AssessmentReleaseBinding(models.Model):
    """
    P3-VS24: Immutable binding between CourseRelease, AssessmentBlueprint, and RubricDefinition.
    Guarantees historical evaluation records remain permanently linked to the exact version.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="assessment_release_bindings",
    )
    course_release = models.ForeignKey(
        CourseRelease,
        on_delete=models.RESTRICT,
        related_name="assessment_bindings",
    )
    blueprint = models.ForeignKey(
        AssessmentBlueprint,
        on_delete=models.RESTRICT,
        related_name="release_bindings",
    )
    rubric = models.ForeignKey(
        RubricDefinition,
        on_delete=models.RESTRICT,
        related_name="release_bindings",
    )
    is_authoritative = models.BooleanField(default=True)
    bound_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_assessmentreleasebinding"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_assessmentreleasebinding_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "course_release", "blueprint"],
                name="uq_binding_release_blueprint",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "course_release") and self.course_release is not None:
            if str(self.course_release.tenant_id) != str(self.tenant_id):
                raise ValidationError("CourseRelease tenant mismatch.")
        if hasattr(self, "blueprint") and self.blueprint is not None:
            if str(self.blueprint.tenant_id) != str(self.tenant_id):
                raise ValidationError("AssessmentBlueprint tenant mismatch.")
        if hasattr(self, "rubric") and self.rubric is not None:
            if str(self.rubric.tenant_id) != str(self.tenant_id):
                raise ValidationError("RubricDefinition tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.course_release_id}:{self.blueprint_id}"


class RubricReviewRecord(models.Model):
    """
    P3-VS24: Immutable audit trail of pedagogical rubric reviews.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="rubric_review_records",
    )
    rubric = models.ForeignKey(
        RubricDefinition,
        on_delete=models.RESTRICT,
        related_name="reviews",
    )
    reviewer_id = models.UUIDField(null=True, blank=True)
    verdict = models.CharField(
        max_length=32,
        choices=RubricReviewVerdict.choices,
    )
    pedagogical_notes = models.TextField(default="", blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_rubricreviewrecord"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_rubricreviewrecord_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(verdict__in=RubricReviewVerdict.values),
                name="chk_rubricreview_verdict",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "rubric"], name="idx_rubricrev_t_r"),
            models.Index(fields=["tenant", "reviewer_id"], name="idx_rubricrev_t_rev"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "rubric") and self.rubric is not None:
            if str(self.rubric.tenant_id) != str(self.tenant_id):
                raise ValidationError("RubricDefinition tenant mismatch.")
        _validate_pii_text_field(self.pedagogical_notes, "pedagogical_notes", 3000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.rubric_id}:{self.verdict}"


# -----------------------------------------------------------------------------
# 3. P3-VS25: RELEASE READINESS, CHANGE IMPACT & PROGRAM ROLLFORWARD
# -----------------------------------------------------------------------------

class CurriculumChangeImpact(models.Model):
    """
    P3-VS25: Immutable record of curriculum version change impact analysis.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="curriculum_change_impacts",
    )
    source_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.RESTRICT,
        related_name="source_impact_analyses",
    )
    target_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.RESTRICT,
        related_name="target_impact_analyses",
    )
    impact_level = models.CharField(
        max_length=32,
        choices=CurriculumChangeImpactLevel.choices,
        default=CurriculumChangeImpactLevel.MINOR,
    )
    breaking_changes_detected = models.BooleanField(default=False)
    affected_cohorts_count = models.IntegerField(default=0)
    impact_details = models.JSONField(default=dict, blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_curriculumchangeimpact"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_curriculumchangeimpact_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(impact_level__in=CurriculumChangeImpactLevel.values),
                name="chk_changeimpact_level",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "source_version") and self.source_version is not None:
            if str(self.source_version.tenant_id) != str(self.tenant_id):
                raise ValidationError("Source CurriculumVersion tenant mismatch.")
        if hasattr(self, "target_version") and self.target_version is not None:
            if str(self.target_version.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target CurriculumVersion tenant mismatch.")
        _validate_pii_jsonb_field(self.impact_details, "impact_details")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.source_version_id}->{self.target_version_id}:{self.impact_level}"


class ReleaseReadinessCheck(models.Model):
    """
    P3-VS25: Automated readiness checks evaluated on a curriculum version.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="release_readiness_checks",
    )
    curriculum_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.CASCADE,
        related_name="readiness_checks",
    )
    check_name = models.CharField(max_length=128)
    category = models.CharField(max_length=64, default="EDITORIAL")
    status = models.CharField(
        max_length=32,
        choices=ReleaseReadinessStatus.choices,
        default=ReleaseReadinessStatus.PENDING,
    )
    check_output = models.TextField(default="", blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_releasereadinesscheck"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_releasereadinesscheck_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=ReleaseReadinessStatus.values),
                name="chk_readinesscheck_status",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "curriculum_version") and self.curriculum_version is not None:
            if str(self.curriculum_version.tenant_id) != str(self.tenant_id):
                raise ValidationError("CurriculumVersion tenant mismatch.")
        _validate_pii_text_field(self.check_output, "check_output", 4000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.curriculum_version_id}:{self.check_name}:{self.status}"


class ReleaseReadinessGate(models.Model):
    """
    P3-VS25: Policy enforcement gate controlling progression of release to deployment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="release_readiness_gates",
    )
    curriculum_version = models.ForeignKey(
        CurriculumVersion,
        on_delete=models.CASCADE,
        related_name="readiness_gates",
    )
    gate_name = models.CharField(max_length=128)
    is_blocking = models.BooleanField(default=True)
    verdict = models.CharField(
        max_length=32,
        choices=ReleaseReadinessStatus.choices,
        default=ReleaseReadinessStatus.PENDING,
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_releasereadinessgate"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_releasereadinessgate_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "curriculum_version", "gate_name"],
                name="uq_gate_version_name",
            ),
            models.CheckConstraint(
                condition=Q(verdict__in=ReleaseReadinessStatus.values),
                name="chk_readinessgate_verdict",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "curriculum_version") and self.curriculum_version is not None:
            if str(self.curriculum_version.tenant_id) != str(self.tenant_id):
                raise ValidationError("CurriculumVersion tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.curriculum_version_id}:{self.gate_name}:{self.verdict}"


class CohortRollforwardPlan(models.Model):
    """
    P3-VS25: Forward-looking cohort migration plan preventing silent historical rebind.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="cohort_rollforward_plans",
    )
    cohort_schedule = models.ForeignKey(
        CohortSchedule,
        on_delete=models.RESTRICT,
        related_name="rollforward_plans",
    )
    target_release = models.ForeignKey(
        CourseRelease,
        on_delete=models.RESTRICT,
        related_name="rollforward_plans",
    )
    rollforward_mode = models.CharField(
        max_length=32,
        choices=CohortRollforwardMode.choices,
        default=CohortRollforwardMode.FUTURE_MODULES_ONLY,
    )
    status = models.CharField(
        max_length=32,
        choices=CohortRollforwardStatus.choices,
        default=CohortRollforwardStatus.DRAFT,
    )
    scheduled_effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_cohortrollforwardplan"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_cohortrollforwardplan_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(rollforward_mode__in=CohortRollforwardMode.values),
                name="chk_cohortrollforward_mode",
            ),
            models.CheckConstraint(
                condition=Q(status__in=CohortRollforwardStatus.values),
                name="chk_cohortrollforward_status",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "cohort_schedule") and self.cohort_schedule is not None:
            if str(self.cohort_schedule.tenant_id) != str(self.tenant_id):
                raise ValidationError("CohortSchedule tenant mismatch.")
        if hasattr(self, "target_release") and self.target_release is not None:
            if str(self.target_release.tenant_id) != str(self.tenant_id):
                raise ValidationError("Target CourseRelease tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.cohort_schedule_id}->{self.target_release_id}:{self.status}"


class CurriculumMigrationDecision(models.Model):
    """
    P3-VS25: Formal transition decision authorizing or halting rollforward execution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="curriculum_migration_decisions",
    )
    plan = models.ForeignKey(
        CohortRollforwardPlan,
        on_delete=models.RESTRICT,
        related_name="migration_decisions",
    )
    decided_by_id = models.UUIDField(null=True, blank=True)
    decision = models.CharField(
        max_length=32,
        choices=CurriculumMigrationDecisionChoice.choices,
    )
    justification = models.TextField(default="", blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_curriculummigrationdecision"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_curriculummigrationdecision_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(decision__in=CurriculumMigrationDecisionChoice.values),
                name="chk_migrationdecision_decision",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "plan"], name="idx_migdecision_t_p"),
            models.Index(fields=["tenant", "decided_by_id"], name="idx_migdecision_t_d"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "plan") and self.plan is not None:
            if str(self.plan.tenant_id) != str(self.tenant_id):
                raise ValidationError("CohortRollforwardPlan tenant mismatch.")
        _validate_pii_text_field(self.justification, "justification", 3000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.plan_id}:{self.decision}"


class ReleaseExceptionRecord(models.Model):
    """
    P3-VS25: Immutable audit record of granted readiness gate waivers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="release_exception_records",
    )
    gate = models.ForeignKey(
        ReleaseReadinessGate,
        on_delete=models.RESTRICT,
        related_name="exceptions",
    )
    granted_by_id = models.UUIDField(null=True, blank=True)
    exception_reason = models.TextField()
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_releaseexceptionrecord"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_releaseexceptionrecord_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "gate"], name="idx_relexcept_t_g"),
            models.Index(fields=["tenant", "granted_by_id"], name="idx_relexcept_t_grantor"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "gate") and self.gate is not None:
            if str(self.gate.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReleaseReadinessGate tenant mismatch.")
        if len(self.exception_reason.strip()) < 10:
            raise ValidationError("exception_reason must be at least 10 characters.")
        _validate_pii_text_field(self.exception_reason, "exception_reason", 3000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.gate_id}:{self.granted_by_id}"


# =============================================================================
# P3-MACRO-EPIC-26-28: ENTERPRISE GOVERNANCE, DATA LIFECYCLE & PILOT READINESS
# Sub-Slices: P3-VS26, P3-VS27, P3-VS28
# Canonical DDL: v1.2-HARDENED
# Models (20):
#   VS26: StaffAccessAssignment, DelegatedAdminScope, PrivilegedPermissionGrant,
#         AccessReviewCampaign, AccessReviewDecision, PrivilegedActionAudit
#   VS27: DataRetentionPolicy, RetentionPolicyVersion, LegalHold,
#         LegalHoldScope, RetentionEvaluation, DataDispositionRecord,
#         DispositionAuditLog
#   VS28: ReadinessControl, ReadinessEvidence, ReadinessAssessmentRun,
#         ReadinessFinding, ReadinessException, PilotReadinessGate,
#         ControlAttestationAudit
# =============================================================================

class StaffRole(models.TextChoices):
    TENANT_ADMIN = "TENANT_ADMIN", "Tenant Admin"
    DELEGATED_STAFF = "DELEGATED_STAFF", "Delegated Staff"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER", "Compliance Officer"
    AUDITOR = "AUDITOR", "Auditor"
    PROGRAM_OPERATOR = "PROGRAM_OPERATOR", "Program Operator"


class ScopeResourceType(models.TextChoices):
    BRANCH = "BRANCH", "Branch"
    PROGRAM = "PROGRAM", "Program"
    DEPARTMENT = "DEPARTMENT", "Department"
    COHORT = "COHORT", "Cohort"


class PrivilegedGrantStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    REVOKED = "REVOKED", "Revoked"


class AccessReviewCampaignStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CONCLUDED = "CONCLUDED", "Concluded"
    CANCELLED = "CANCELLED", "Cancelled"


class AccessReviewDecisionChoice(models.TextChoices):
    MAINTAIN = "MAINTAIN", "Maintain"
    REVOKE = "REVOKE", "Revoke"
    RESTRICT = "RESTRICT", "Restrict"


class DispositionAction(models.TextChoices):
    ANONYMIZE = "ANONYMIZE", "Anonymize"
    PURGE = "PURGE", "Purge"
    ARCHIVE = "ARCHIVE", "Archive"


class LegalHoldStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    RELEASED = "RELEASED", "Released"


class ReadinessControlCategory(models.TextChoices):
    SECURITY = "SECURITY", "Security"
    DATA_GOVERNANCE = "DATA_GOVERNANCE", "Data Governance"
    TESTING = "TESTING", "Testing"
    RLS = "RLS", "RLS"
    FLEET = "FLEET", "Fleet"


class ReadinessEvidenceStatus(models.TextChoices):
    VALID = "VALID", "Valid"
    SUPERSEDED = "SUPERSEDED", "Superseded"
    REVOKED = "REVOKED", "Revoked"


class ReadinessOverallStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    READY = "READY", "Ready"
    NOT_READY = "NOT_READY", "Not Ready"
    BLOCKED = "BLOCKED", "Blocked"
    EXCEPTION_REQUIRED = "EXCEPTION_REQUIRED", "Exception Required"


class ReadinessFindingSeverity(models.TextChoices):
    BLOCKER = "BLOCKER", "Blocker"
    CRITICAL = "CRITICAL", "Critical"
    MAJOR = "MAJOR", "Major"
    MINOR = "MINOR", "Minor"


class PilotGateVerdict(models.TextChoices):
    READY = "READY", "Ready"
    NOT_READY = "NOT_READY", "Not Ready"
    BLOCKED = "BLOCKED", "Blocked"
    EXCEPTION_REQUIRED = "EXCEPTION_REQUIRED", "Exception Required"


# -----------------------------------------------------------------------------
# 1. P3-VS26: DELEGATED ADMINISTRATION & ACCESS GOVERNANCE
# -----------------------------------------------------------------------------

class StaffAccessAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="staff_access_assignments",
    )
    user_id = models.UUIDField()
    role_name = models.CharField(max_length=64, choices=StaffRole.choices)
    scope_type = models.CharField(max_length=32, default="TENANT_WIDE")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    assigned_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_staff_access_assignment"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_staff_access_assignment_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "user_id", "role_name"],
                name="uq_staff_assignment",
            ),
            models.CheckConstraint(
                condition=Q(role_name__in=StaffRole.values),
                name="chk_staff_role_valid",
            ),
            models.CheckConstraint(
                condition=Q(valid_until__isnull=True) | Q(valid_until__gt=models.F("valid_from")),
                name="chk_staff_validity_window",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "user_id", "is_active"], name="idx_staff_assign_t_u_act"),
        ]

    def clean(self):
        super().clean()
        if self.valid_until and self.valid_from and self.valid_until <= self.valid_from:
            raise ValidationError("valid_until must be strictly greater than valid_from.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.user_id}:{self.role_name}"


class DelegatedAdminScope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="delegated_admin_scopes",
    )
    assignment = models.ForeignKey(
        StaffAccessAssignment,
        on_delete=models.CASCADE,
        related_name="scopes",
    )
    scope_resource_type = models.CharField(max_length=64, choices=ScopeResourceType.choices)
    scope_resource_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_delegated_admin_scope"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_delegated_admin_scope_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(scope_resource_type__in=ScopeResourceType.values),
                name="chk_scope_resource_type",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "assignment"], name="idx_del_admin_scope_t_assign"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "assignment") and self.assignment is not None:
            if str(self.assignment.tenant_id) != str(self.tenant_id):
                raise ValidationError("StaffAccessAssignment tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.assignment_id}:{self.scope_resource_type}:{self.scope_resource_id}"


class PrivilegedPermissionGrant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="privileged_permission_grants",
    )
    user_id = models.UUIDField()
    permission_code = models.CharField(max_length=64)
    justification = models.TextField()
    granted_by_id = models.UUIDField()
    second_approver_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=PrivilegedGrantStatus.choices,
        default=PrivilegedGrantStatus.ACTIVE,
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_privileged_permission_grant"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_privileged_permission_grant_tenant_id",
            ),
            models.CheckConstraint(
                condition=~Q(user_id=models.F("granted_by_id")),
                name="chk_privilege_no_self_grant",
            ),
            models.CheckConstraint(
                condition=Q(second_approver_id__isnull=True) | ~Q(second_approver_id=models.F("granted_by_id")),
                name="chk_privilege_distinct_second_approver",
            ),
            models.CheckConstraint(
                condition=Q(status__in=PrivilegedGrantStatus.values),
                name="chk_privilege_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "user_id", "status"], name="idx_priv_grant_t_u_stat"),
        ]

    def clean(self):
        super().clean()
        if str(self.user_id) == str(self.granted_by_id):
            raise ValidationError("Self-granting of privileges is strictly prohibited.")
        if self.second_approver_id and str(self.second_approver_id) == str(self.granted_by_id):
            raise ValidationError("Second approver must be distinct from grantor.")
        _validate_pii_text_field(self.justification, "justification", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.user_id}:{self.permission_code}:{self.status}"


class AccessReviewCampaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="access_review_campaigns",
    )
    title = models.CharField(max_length=255)
    campaign_period = models.CharField(max_length=32)
    status = models.CharField(
        max_length=32,
        choices=AccessReviewCampaignStatus.choices,
        default=AccessReviewCampaignStatus.ACTIVE,
    )
    deadline = models.DateTimeField()
    created_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_access_review_campaign"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_access_review_campaign_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=AccessReviewCampaignStatus.values),
                name="chk_campaign_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_acc_camp_t_stat"),
        ]

    def clean(self):
        super().clean()
        _validate_pii_text_field(self.title, "title", 255)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.title}:{self.status}"


class AccessReviewDecision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="access_review_decisions",
    )
    campaign = models.ForeignKey(
        AccessReviewCampaign,
        on_delete=models.CASCADE,
        related_name="decisions",
    )
    assignment = models.ForeignKey(
        StaffAccessAssignment,
        on_delete=models.CASCADE,
        related_name="review_decisions",
    )
    reviewer_id = models.UUIDField()
    decision = models.CharField(
        max_length=32,
        choices=AccessReviewDecisionChoice.choices,
    )
    notes = models.TextField(default="", blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_access_review_decision"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_access_review_decision_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "campaign", "assignment"],
                name="uq_review_decision_per_assignment",
            ),
            models.CheckConstraint(
                condition=Q(decision__in=AccessReviewDecisionChoice.values),
                name="chk_review_decision",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "campaign", "reviewer_id"], name="idx_rev_dec_t_camp_rev"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "campaign") and self.campaign is not None:
            if str(self.campaign.tenant_id) != str(self.tenant_id):
                raise ValidationError("AccessReviewCampaign tenant mismatch.")
        if hasattr(self, "assignment") and self.assignment is not None:
            if str(self.assignment.tenant_id) != str(self.tenant_id):
                raise ValidationError("StaffAccessAssignment tenant mismatch.")
        _validate_pii_text_field(self.notes, "notes", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.campaign_id}:{self.assignment_id}:{self.decision}"


class PrivilegedActionAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="privileged_action_audits",
    )
    actor_id = models.UUIDField()
    action_type = models.CharField(max_length=64)
    target_resource = models.CharField(max_length=128)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_privileged_action_audit"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_privileged_action_audit_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_priv_audit_t_act_cr"),
        ]

    def clean(self):
        super().clean()
        _validate_pii_jsonb_field(self.details, "details")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.actor_id}:{self.action_type}"


# -----------------------------------------------------------------------------
# 2. P3-VS27: DATA LIFECYCLE, RETENTION & DISPOSITION GOVERNANCE
# -----------------------------------------------------------------------------

class DataRetentionPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="data_retention_policies",
    )
    data_category = models.CharField(max_length=64)
    retention_period_days = models.IntegerField()
    disposition_action = models.CharField(
        max_length=32,
        choices=DispositionAction.choices,
        default=DispositionAction.ANONYMIZE,
    )
    is_active = models.BooleanField(default=True)
    created_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_data_retention_policy"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_data_retention_policy_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "data_category"],
                name="uq_retention_category",
            ),
            models.CheckConstraint(
                condition=Q(retention_period_days__gte=30),
                name="chk_retention_period_positive",
            ),
            models.CheckConstraint(
                condition=Q(disposition_action__in=DispositionAction.values),
                name="chk_disposition_action",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "is_active"], name="idx_ret_pol_t_act"),
        ]

    def clean(self):
        super().clean()
        if self.retention_period_days < 30:
            raise ValidationError("retention_period_days must be at least 30 days.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.data_category}:{self.retention_period_days}d"


class RetentionPolicyVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="retention_policy_versions",
    )
    policy = models.ForeignKey(
        DataRetentionPolicy,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.IntegerField()
    retention_period_days = models.IntegerField()
    disposition_action = models.CharField(max_length=32, choices=DispositionAction.choices)
    effective_from = models.DateTimeField(auto_now_add=True)
    created_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_retention_policy_version"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_retention_policy_version_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "policy", "version_number"],
                name="uq_policy_version",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "policy", "-version_number"], name="idx_ret_ver_t_pol_v"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "policy") and self.policy is not None:
            if str(self.policy.tenant_id) != str(self.tenant_id):
                raise ValidationError("DataRetentionPolicy tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.policy_id}:v{self.version_number}"


class LegalHold(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="legal_holds",
    )
    title = models.CharField(max_length=255)
    legal_case_reference = models.CharField(max_length=128)
    reason = models.TextField()
    status = models.CharField(
        max_length=32,
        choices=LegalHoldStatus.choices,
        default=LegalHoldStatus.ACTIVE,
    )
    placed_by_id = models.UUIDField()
    placed_at = models.DateTimeField(auto_now_add=True)
    released_by_id = models.UUIDField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_legal_hold"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_legal_hold_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=LegalHoldStatus.values),
                name="chk_hold_status",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status="RELEASED") & Q(released_at__isnull=False) & Q(released_by_id__isnull=False)) |
                    (Q(status="ACTIVE") & Q(released_at__isnull=True) & Q(released_by_id__isnull=True))
                ),
                name="chk_hold_release_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_legal_hold_t_stat"),
        ]

    def clean(self):
        super().clean()
        if self.status == LegalHoldStatus.RELEASED and (not self.released_at or not self.released_by_id):
            raise ValidationError("Released LegalHold must have released_at and released_by_id set.")
        if self.status == LegalHoldStatus.ACTIVE and (self.released_at or self.released_by_id):
            raise ValidationError("Active LegalHold must not have released_at or released_by_id set.")
        _validate_pii_text_field(self.reason, "reason", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.legal_case_reference}:{self.status}"


class LegalHoldScope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="legal_hold_scopes",
    )
    legal_hold = models.ForeignKey(
        LegalHold,
        on_delete=models.CASCADE,
        related_name="scopes",
    )
    target_entity_type = models.CharField(max_length=64)
    target_entity_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_legal_hold_scope"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_legal_hold_scope_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "legal_hold"], name="idx_legal_scope_t_hold"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "legal_hold") and self.legal_hold is not None:
            if str(self.legal_hold.tenant_id) != str(self.tenant_id):
                raise ValidationError("LegalHold tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.legal_hold_id}:{self.target_entity_type}:{self.target_entity_id}"


class RetentionEvaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="retention_evaluations",
    )
    policy = models.ForeignKey(
        DataRetentionPolicy,
        on_delete=models.RESTRICT,
        related_name="evaluations",
    )
    evaluated_entity_type = models.CharField(max_length=64)
    candidates_count = models.IntegerField(default=0)
    exempted_by_legal_hold_count = models.IntegerField(default=0)
    disposition_ready_count = models.IntegerField(default=0)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_retention_evaluation"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_retention_evaluation_tenant_id",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "policy") and self.policy is not None:
            if str(self.policy.tenant_id) != str(self.tenant_id):
                raise ValidationError("DataRetentionPolicy tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.evaluated_entity_type}:{self.disposition_ready_count} ready"


class DataDispositionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="data_disposition_records",
    )
    evaluation = models.ForeignKey(
        RetentionEvaluation,
        on_delete=models.RESTRICT,
        related_name="disposition_records",
    )
    action_applied = models.CharField(max_length=32, choices=DispositionAction.choices)
    status = models.CharField(max_length=32, default="EXECUTED")
    records_processed = models.IntegerField(default=0)
    cryptographic_digest = models.CharField(max_length=128)
    executed_by_id = models.UUIDField()
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_data_disposition_record"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_data_disposition_record_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_disp_rec_t_stat"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "evaluation") and self.evaluation is not None:
            if str(self.evaluation.tenant_id) != str(self.tenant_id):
                raise ValidationError("RetentionEvaluation tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.action_applied}:{self.records_processed}"


class DispositionAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="disposition_audit_logs",
    )
    disposition_record = models.ForeignKey(
        DataDispositionRecord,
        on_delete=models.RESTRICT,
        related_name="audit_logs",
    )
    actor_id = models.UUIDField(null=True, blank=True)
    entity_type = models.CharField(max_length=64)
    entity_key_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=32, default="SUCCESS")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_disposition_audit_log"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_disposition_audit_log_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_disp_audit_t_act_cr"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "disposition_record") and self.disposition_record is not None:
            if str(self.disposition_record.tenant_id) != str(self.tenant_id):
                raise ValidationError("DataDispositionRecord tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.entity_type}:{self.entity_key_hash}"


# -----------------------------------------------------------------------------
# 3. P3-VS28: ENTERPRISE CONTROL EVIDENCE & PILOT READINESS CENTER
# -----------------------------------------------------------------------------

class ReadinessControl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_controls",
    )
    control_code = models.CharField(max_length=64)
    category = models.CharField(max_length=64, choices=ReadinessControlCategory.choices)
    description = models.TextField()
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_readiness_control"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_control_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "control_code"],
                name="uq_readiness_control_code",
            ),
            models.CheckConstraint(
                condition=Q(category__in=ReadinessControlCategory.values),
                name="chk_control_category",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "category"], name="idx_read_ctrl_t_cat"),
        ]

    def clean(self):
        super().clean()
        _validate_pii_text_field(self.description, "description", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.control_code}:{self.category}"


class ReadinessEvidence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_evidences",
    )
    control = models.ForeignKey(
        ReadinessControl,
        on_delete=models.RESTRICT,
        related_name="evidences",
    )
    evidence_type = models.CharField(max_length=64)
    artifact_reference = models.CharField(max_length=255)
    verification_hash = models.CharField(max_length=128)
    status = models.CharField(
        max_length=32,
        choices=ReadinessEvidenceStatus.choices,
        default=ReadinessEvidenceStatus.VALID,
    )
    recorded_by_id = models.UUIDField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_evidence"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_evidence_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=ReadinessEvidenceStatus.values),
                name="chk_evidence_status",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "control") and self.control is not None:
            if str(self.control.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessControl tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.control_id}:{self.evidence_type}:{self.status}"


class ReadinessAssessmentRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_assessment_runs",
    )
    run_reference = models.CharField(max_length=64)
    total_controls = models.IntegerField(default=0)
    passed_controls = models.IntegerField(default=0)
    failed_controls = models.IntegerField(default=0)
    overall_status = models.CharField(
        max_length=32,
        choices=ReadinessOverallStatus.choices,
        default=ReadinessOverallStatus.IN_PROGRESS,
    )
    status = models.CharField(max_length=32, default="IN_PROGRESS")
    executed_by_id = models.UUIDField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_assessment_run"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_assessment_run_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(overall_status__in=ReadinessOverallStatus.values),
                name="chk_run_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_read_run_t_stat"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.run_reference}:{self.overall_status}"


class ReadinessFinding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_findings",
    )
    assessment_run = models.ForeignKey(
        ReadinessAssessmentRun,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    control = models.ForeignKey(
        ReadinessControl,
        on_delete=models.RESTRICT,
        related_name="findings",
    )
    severity = models.CharField(
        max_length=32,
        choices=ReadinessFindingSeverity.choices,
        default=ReadinessFindingSeverity.MAJOR,
    )
    finding_summary = models.TextField()
    status = models.CharField(max_length=32, default="OPEN")
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_finding"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_finding_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(severity__in=ReadinessFindingSeverity.values),
                name="chk_finding_severity",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "severity", "status"], name="idx_read_find_t_sev_stat"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "assessment_run") and self.assessment_run is not None:
            if str(self.assessment_run.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessAssessmentRun tenant mismatch.")
        if hasattr(self, "control") and self.control is not None:
            if str(self.control.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessControl tenant mismatch.")
        _validate_pii_text_field(self.finding_summary, "finding_summary", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.control_id}:{self.severity}:resolved={self.is_resolved}"


class ReadinessException(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_exceptions",
    )
    finding = models.ForeignKey(
        ReadinessFinding,
        on_delete=models.RESTRICT,
        related_name="exceptions",
    )
    reason = models.TextField()
    expiry_date = models.DateTimeField()
    approved_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_exception"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_exception_tenant_id",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "finding") and self.finding is not None:
            if str(self.finding.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessFinding tenant mismatch.")
        _validate_pii_text_field(self.reason, "reason", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.finding_id}:{self.approved_by_id}"


class PilotReadinessGate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="pilot_readiness_gates",
    )
    assessment_run = models.ForeignKey(
        ReadinessAssessmentRun,
        on_delete=models.RESTRICT,
        related_name="pilot_gates",
    )
    gate_verdict = models.CharField(
        max_length=32,
        choices=PilotGateVerdict.choices,
    )
    status = models.CharField(max_length=32, default="EVALUATED")
    human_attestation_summary = models.TextField()
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_pilot_readiness_gate"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_pilot_readiness_gate_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(gate_verdict__in=PilotGateVerdict.values),
                name="chk_gate_verdict",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_pilot_gate_t_stat"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "assessment_run") and self.assessment_run is not None:
            if str(self.assessment_run.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessAssessmentRun tenant mismatch.")
        _validate_pii_text_field(self.human_attestation_summary, "human_attestation_summary", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.assessment_run_id}:{self.gate_verdict}"


class ControlAttestationAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="control_attestation_audits",
    )
    gate = models.ForeignKey(
        PilotReadinessGate,
        on_delete=models.RESTRICT,
        related_name="attestations",
    )
    attested_by_id = models.UUIDField()
    attestation_role = models.CharField(max_length=64)
    signature_digest = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_control_attestation_audit"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_control_attestation_audit_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "gate", "-created_at"], name="idx_ctrl_attest_t_g_cr"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "gate") and self.gate is not None:
            if str(self.gate.tenant_id) != str(self.tenant_id):
                raise ValidationError("PilotReadinessGate tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.gate_id}:{self.attestation_role}:{self.attested_by_id}"
