import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import Q
from modules.platform_tenant.models import Tenant


class TenantScopedModel(models.Model):
    """
    Abstract base model enforcing strict Tenant context ownership.
    Every educational domain aggregate root or entity must belong to a Tenant.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )

    class Meta:
        abstract = True


class LearnerProfile(TenantScopedModel):
    """
    LearnerProfile represents the Learning Identity within a specific Tenant context,
    bound to the authenticated User who holds the LEARNER role.
    This resolves the ambiguity: It is NOT a generic User extension,
    it is the bounded Pedagogical Identity and Progress Tracker.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learner_profiles",
        db_index=True,
    )
    assigned_mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mentored_learners",
    )
    guardian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guarded_learners",
    )
    student_code = models.CharField(max_length=32, db_index=True)
    display_name = models.CharField(max_length=120)
    avatar_key = models.CharField(max_length=64, default="default")
    level_title = models.CharField(max_length=120)
    streak_days = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "learning_loop"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user"],
                name="unique_tenant_learner_profile",
            ),
            models.UniqueConstraint(
                fields=["tenant", "student_code"],
                name="unique_tenant_student_code",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_code"]),
            models.Index(fields=["tenant", "assigned_mentor"]),
            models.Index(fields=["tenant", "guardian"]),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.student_code}) - {self.tenant_id}"


class ActiveLearningProject(TenantScopedModel):
    """
    The active engineering milestone or codebase project on which the Learner is working.
    Captures verifiable code snippets and demonstrated competencies.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.ForeignKey(
        LearnerProfile,
        on_delete=models.CASCADE,
        related_name="projects",
        db_index=True,
    )
    project_slug = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    repo_branch = models.CharField(max_length=100)
    commit_hash = models.CharField(max_length=40)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    current_milestone = models.TextField()
    recent_activity = models.TextField()
    last_code_snippet = models.TextField(blank=True)
    skills_demonstrated = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "learning_loop"
        indexes = [
            models.Index(fields=["tenant", "learner", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} - Learner: {self.learner_id}"


class MentorIntervention(TenantScopedModel):
    """
    Pedagogical intervention triggered by system signal or mentor inspection.
    Follows lifecycle: OPEN -> REVIEWING -> FOLLOW_UP -> RESOLVED.
    """
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        REVIEWING = "REVIEWING", "Reviewing"
        FOLLOW_UP = "FOLLOW_UP", "Follow Up"
        RESOLVED = "RESOLVED", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        ActiveLearningProject,
        on_delete=models.CASCADE,
        related_name="interventions",
        db_index=True,
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recorded_interventions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    reason = models.TextField()
    recommended_action = models.TextField()
    mentor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "learning_loop"
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "project"]),
        ]

    def __str__(self) -> str:
        return f"Intervention [{self.status}] on Project {self.project_id}"


class InterventionFeedback(TenantScopedModel):
    """
    Non-punitive pedagogical guidance and dialogue items attached to an intervention.
    """
    class SenderRole(models.TextChoices):
        MENTOR = "MENTOR", "Mentor"
        STUDENT = "STUDENT", "Student"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervention = models.ForeignKey(
        MentorIntervention,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        db_index=True,
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_feedbacks",
    )
    sender_role = models.CharField(
        max_length=16,
        choices=SenderRole.choices,
    )
    action_type = models.CharField(max_length=64)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "learning_loop"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["tenant", "intervention", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Feedback by {self.sender_role} on {self.intervention_id}"


class ParentBridge(TenantScopedModel):
    """
    Translation layer translating engineering telemetry into humane parental insights.
    Stores last briefing and parental praise/encouragement ribbons.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.OneToOneField(
        LearnerProfile,
        on_delete=models.CASCADE,
        related_name="parent_bridge",
        db_index=True,
    )
    last_briefing = models.TextField()
    briefing_updated_at = models.DateTimeField(auto_now=True)
    parent_encouragement_sent = models.BooleanField(default=False)
    parent_encouragement_message = models.TextField(blank=True)
    encouragement_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "learning_loop"
        indexes = [
            models.Index(fields=["tenant", "learner"]),
        ]

    def __str__(self) -> str:
        return f"ParentBridge for Learner {self.learner_id}"
