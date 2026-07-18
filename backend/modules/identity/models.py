import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    session_auth_epoch = models.PositiveBigIntegerField(default=1)

    REQUIRED_FIELDS = ["email"]


class PasscodeCredential(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="passcode_credential")
    encoded_hash = models.CharField(max_length=256)
    pepper_id = models.CharField(max_length=64)
    must_change = models.BooleanField(default=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    credential_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    def __repr__(self) -> str:
        return f"PasscodeCredential(user_id={self.user_id!s}, version={self.credential_version})"

    def __str__(self) -> str:
        return f"Passcode credential for user {self.user_id}"


class PasscodeChangeChallenge(models.Model):
    """Dormant, tenant-scoped verifier for a future forced passcode change."""

    class Purpose(models.TextChoices):
        FORCED_PASSCODE_CHANGE = "forced_passcode_change", "Forced passcode change"

    class State(models.TextChoices):
        ACTIVE = "active", "Active"
        CONSUMED = "consumed", "Consumed"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    selector = models.UUIDField(unique=True, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.RESTRICT,
        related_name="passcode_change_challenges",
    )
    credential = models.ForeignKey(
        PasscodeCredential,
        on_delete=models.RESTRICT,
        related_name="passcode_change_challenges",
    )
    credential_version = models.PositiveIntegerField()
    purpose = models.CharField(
        max_length=64,
        choices=Purpose,
        default=Purpose.FORCED_PASSCODE_CHANGE,
    )
    secret_digest = models.BinaryField(max_length=32, null=True, editable=False)
    pepper_id = models.CharField(max_length=64)
    state = models.CharField(max_length=16, choices=State, default=State.ACTIVE)
    issued_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(purpose="forced_passcode_change"),
                name="passcode_change_challenge_purpose_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        state="active",
                        secret_digest__isnull=False,
                        consumed_at__isnull=True,
                        revoked_at__isnull=True,
                        expired_at__isnull=True,
                    )
                    | Q(
                        state="consumed",
                        secret_digest__isnull=True,
                        consumed_at__isnull=False,
                        revoked_at__isnull=True,
                        expired_at__isnull=True,
                    )
                    | Q(
                        state="revoked",
                        secret_digest__isnull=True,
                        consumed_at__isnull=True,
                        revoked_at__isnull=False,
                        expired_at__isnull=True,
                    )
                    | Q(
                        state="expired",
                        secret_digest__isnull=True,
                        consumed_at__isnull=True,
                        revoked_at__isnull=True,
                        expired_at__isnull=False,
                    )
                ),
                name="passcode_change_challenge_state_valid",
            ),
            models.UniqueConstraint(
                fields=["credential", "purpose"],
                condition=Q(state="active"),
                name="one_active_passcode_change_challenge",
            ),
        ]
        indexes = [
            models.Index(
                fields=["tenant", "selector", "purpose", "state"],
                name="passchg_lookup_idx",
            ),
            models.Index(fields=["state", "expires_at"], name="passchg_cleanup_idx"),
        ]

    def __str__(self) -> str:
        return f"Passcode change challenge {self.id}"
