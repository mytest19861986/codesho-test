import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import Now


class OutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)
    topic = models.CharField(max_length=160)
    aggregate_type = models.CharField(max_length=100)
    aggregate_id = models.CharField(max_length=100)
    payload = models.JSONField()
    occurred_at = models.DateTimeField(auto_now_add=True)
    available_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["published_at", "available_at"])]

    def __str__(self) -> str:
        return f"{self.topic}:{self.id}"


SECURITY_EVENT_TYPES = (
    "passcode_created",
    "passcode_changed",
    "passcode_verification_failed",
    "account_locked",
    "account_unlocked",
    "abuse_global_alert",
    "temporary_passcode_issued",
    "temporary_passcode_consumed",
    "guardian_reset_started",
    "guardian_reset_completed",
    "authentication_succeeded",
    "authentication_failed",
    "authentication_blocked",
    "session_logged_out",
)
SECURITY_EVENT_OUTCOMES = ("success", "failure", "blocked", "detected")
SECURITY_EVENT_REASON_CODES = (
    "credential_created",
    "credential_changed",
    "verification_mismatch",
    "lock_threshold_reached",
    "lock_cleared",
    "abuse_threshold_reached",
    "temporary_credential_issued",
    "temporary_credential_consumed",
    "guardian_reset_requested",
    "guardian_reset_confirmed",
    "login_succeeded",
    "login_failed",
    "login_blocked",
    "session_logged_out",
)


class IdentitySecurityEvent(models.Model):
    event_id = models.UUIDField(primary_key=True, editable=False)
    event_type = models.CharField(max_length=64)
    outcome = models.CharField(max_length=16)
    reason_code = models.CharField(max_length=128, null=True, blank=True)
    subject_user_id = models.UUIDField(null=True, blank=True)
    actor_user_id = models.UUIDField(null=True, blank=True)
    tenant_id = models.UUIDField(null=True, blank=True)
    credential_version = models.PositiveIntegerField(null=True, blank=True)
    correlation_id = models.UUIDField()
    idempotency_key = models.CharField(max_length=255, null=True, blank=True, unique=True)
    occurred_at = models.DateTimeField(db_default=Now(), editable=False)

    class Meta:
        db_table = "audit.identity_security_event"
        constraints = [
            models.CheckConstraint(
                condition=Q(event_type__in=SECURITY_EVENT_TYPES),
                name="identity_security_event_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(outcome__in=SECURITY_EVENT_OUTCOMES),
                name="identity_security_event_outcome_valid",
            ),
            models.CheckConstraint(
                condition=Q(reason_code__isnull=True)
                | Q(reason_code__in=SECURITY_EVENT_REASON_CODES),
                name="identity_security_event_reason_code_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type}:{self.event_id}"
