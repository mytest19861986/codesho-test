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
