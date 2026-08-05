import uuid
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    class IdentityMode(models.TextChoices):
        HUMAN = "human", "Human"
        SYNTHETIC = "synthetic", "Synthetic"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(  # type: ignore[assignment]
        max_length=150, unique=True, null=True, blank=True
    )
    email = models.EmailField(unique=True, null=True, blank=True)  # type: ignore[assignment]
    identity_mode = models.CharField(
        max_length=16,
        choices=IdentityMode,
        default=IdentityMode.HUMAN,
        editable=False,
    )
    synthetic_handle = models.UUIDField(null=True, unique=True, editable=False)
    session_auth_epoch = models.PositiveBigIntegerField(default=1)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        identity_mode="human",
                        username__isnull=False,
                        email__isnull=False,
                        synthetic_handle__isnull=True,
                    )
                    | Q(
                        identity_mode="synthetic",
                        username__isnull=True,
                        email__isnull=True,
                        synthetic_handle__isnull=False,
                        is_active=False,
                        is_staff=False,
                        is_superuser=False,
                        first_name="",
                        last_name="",
                    )
                ),
                name="user_identity_mode_fields_consistent",
            )
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            previous = type(self).objects.filter(pk=self.pk).values("identity_mode").first()
            if previous is not None and previous["identity_mode"] != self.identity_mode:
                raise ValidationError("identity mode is immutable")
        super().save(*args, **kwargs)


class AdultAgeAttestation(models.Model):
    """Immutable, minimal evidence for an internal synthetic adult subject."""

    class Status(models.TextChoices):
        ADULT_ATTESTED = "adult_attested", "Adult attested"

    class Source(models.TextChoices):
        INTERNAL_TEST_API = "internal_test_api", "Internal test API"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(editable=False)
    subject_id = models.UUIDField(editable=False)
    status = models.CharField(
        max_length=32,
        choices=Status,
        default=Status.ADULT_ATTESTED,
        editable=False,
    )
    policy_version = models.CharField(max_length=64, editable=False)
    source = models.CharField(
        max_length=32,
        choices=Source,
        default=Source.INTERNAL_TEST_API,
        editable=False,
    )
    audit_event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    attested_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "subject_id", "policy_version"],
                name="unique_adult_attestation_per_policy",
            ),
            models.CheckConstraint(
                condition=Q(status="adult_attested"),
                name="adult_attestation_status_valid",
            ),
            models.CheckConstraint(
                condition=Q(source="internal_test_api"),
                name="adult_attestation_source_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"AdultAgeAttestation({self.id})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("adult age attestations are immutable")
        super().save(*args, **kwargs)

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        raise ValidationError("adult age attestations are append-only")


class AdultAttestationProvenance(models.Model):
    """Restricted collection receipt for one internal synthetic attestation."""

    class CollectionContext(models.TextChoices):
        INTERNAL_SYNTHETIC_HARNESS = (
            "internal_synthetic_harness",
            "Internal synthetic harness",
        )

    class ReceiptKind(models.TextChoices):
        SELF_ATTESTATION = "self_attestation", "Self attestation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(editable=False)
    attestation = models.OneToOneField(
        AdultAgeAttestation,
        db_column="attestation_id",
        on_delete=models.PROTECT,
        related_name="+",
        editable=False,
    )
    collection_context = models.CharField(
        max_length=64,
        choices=CollectionContext,
        default=CollectionContext.INTERNAL_SYNTHETIC_HARNESS,
        editable=False,
    )
    receipt_kind = models.CharField(
        max_length=32,
        choices=ReceiptKind,
        default=ReceiptKind.SELF_ATTESTATION,
        editable=False,
    )
    recorded_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(collection_context="internal_synthetic_harness"),
                name="adult_provenance_context_valid",
            ),
            models.CheckConstraint(
                condition=Q(receipt_kind="self_attestation"),
                name="adult_provenance_receipt_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"AdultAttestationProvenance({self.id})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("adult attestation provenance is immutable")
        super().save(*args, **kwargs)

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        raise ValidationError("adult attestation provenance is append-only")


class SyntheticBootstrapRequest(models.Model):
    """Immutable terminal request linking one attestation to one dormant account."""

    class State(models.TextChoices):
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(editable=False)
    attestation = models.ForeignKey(
        AdultAgeAttestation,
        on_delete=models.PROTECT,
        related_name="+",
        editable=False,
    )
    provenance = models.ForeignKey(
        AdultAttestationProvenance,
        on_delete=models.PROTECT,
        related_name="+",
        editable=False,
    )
    idempotency_key = models.UUIDField(editable=False)
    user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="synthetic_bootstrap_requests",
        editable=False,
    )
    membership = models.ForeignKey(
        "platform_tenant.TenantMembership",
        on_delete=models.PROTECT,
        related_name="synthetic_bootstrap_requests",
        editable=False,
    )
    state = models.CharField(
        max_length=16,
        choices=State,
        default=State.COMPLETED,
        editable=False,
    )
    audit_event_id = models.UUIDField(unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "attestation"],
                name="unique_synthetic_request_tenant_attestation",
            ),
            models.UniqueConstraint(
                fields=["tenant_id", "idempotency_key"],
                name="unique_synthetic_request_tenant_idempotency",
            ),
            models.CheckConstraint(
                condition=Q(state="completed"),
                name="synthetic_request_terminal_state_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"SyntheticBootstrapRequest({self.id})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("synthetic bootstrap requests are immutable")
        super().save(*args, **kwargs)

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        raise ValidationError("synthetic bootstrap requests are append-only")


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

    def save(self, *args: Any, **kwargs: Any) -> None:
        if User.objects.filter(pk=self.user_id, identity_mode=User.IdentityMode.SYNTHETIC).exists():
            raise ValidationError("synthetic users cannot receive credentials")
        super().save(*args, **kwargs)


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
    # PostgreSQL migration 0004 enforces an exact 32-byte non-null digest for
    # active rows; SQLite cannot faithfully enforce byte-length constraints.
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


class PlatformOperatorPolicy(models.Model):
    """Platform operator administrative access policy."""

    class ModelLabel(models.TextChoices):
        IDENTITY_USER = "identity.User", "identity.User"
        PLATFORM_TENANT_TENANT = "platform_tenant.Tenant", "platform_tenant.Tenant"
        PLATFORM_TENANT_TENANT_MEMBERSHIP = (
            "platform_tenant.TenantMembership",
            "platform_tenant.TenantMembership",
        )

    class Action(models.TextChoices):
        LIST = "list", "List"
        VIEW = "view", "View"

    class ScopeKind(models.TextChoices):
        PLATFORM_USER_SAFE = "platform_user_safe", "Platform user safe"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator_user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="platform_operator_policies",
    )
    model_label = models.CharField(max_length=128, choices=ModelLabel.choices)
    action = models.CharField(max_length=64, choices=Action.choices)
    scope_kind = models.CharField(max_length=64, choices=ScopeKind.choices)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="created_operator_policies",
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by_user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="revoked_operator_policies",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["operator_user", "model_label", "action", "scope_kind"],
                condition=Q(active=True),
                name="unique_active_operator_policy",
            ),
            models.CheckConstraint(
                condition=Q(
                    model_label__in=[
                        "identity.User",
                        "platform_tenant.Tenant",
                        "platform_tenant.TenantMembership",
                    ]
                ),
                name="operator_policy_model_label_valid",
            ),
            models.CheckConstraint(
                condition=Q(action__in=["list", "view"]),
                name="operator_policy_action_valid",
            ),
            models.CheckConstraint(
                condition=Q(scope_kind__in=["platform_user_safe"]),
                name="operator_policy_scope_kind_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(active=True, revoked_at__isnull=True, revoked_by_user__isnull=True)
                    | Q(active=False, revoked_at__isnull=False, revoked_by_user__isnull=False)
                ),
                name="operator_policy_revocation_consistent",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"PlatformOperatorPolicy({self.operator_user_id}, {self.model_label}, "
            f"{self.action}, {self.scope_kind}, active={self.active})"
        )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Permit creation and one irreversible active-to-revoked transition only.

        PostgreSQL triggers enforce the same rule for queryset and raw-SQL
        paths.  This guard makes ordinary ORM use fail closed before a write.
        """
        if self._state.adding:
            super().save(*args, **kwargs)
            return

        previous = type(self).objects.filter(pk=self.pk).values(
            "operator_user_id",
            "model_label",
            "action",
            "scope_kind",
            "active",
            "created_at",
            "created_by_user_id",
            "revoked_at",
            "revoked_by_user_id",
        ).first()
        if previous is None:
            raise ValidationError("operator policy does not exist")
        if not previous["active"]:
            raise ValidationError("revoked operator policy is immutable")

        if (
            previous["operator_user_id"] != self.operator_user_id
            or previous["model_label"] != self.model_label
            or previous["action"] != self.action
            or previous["scope_kind"] != self.scope_kind
            or previous["created_at"] != self.created_at
            or previous["created_by_user_id"] != self.created_by_user_id
        ):
            raise ValidationError("operator policy grants are immutable")
        if self.active or self.revoked_at is None or self.revoked_by_user_id is None:
            raise ValidationError("operator policy may only be revoked once")

        super().save(*args, **kwargs)

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        raise ValidationError("operator policy rows are append-only")
