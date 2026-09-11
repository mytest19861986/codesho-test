import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class Tenant(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=63, unique=True)
    name = models.CharField(max_length=160)
    status = models.CharField(max_length=16, choices=Status, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class TenantMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MENTOR = "mentor", "Mentor"
        LEARNER = "learner", "Learner"
        GUARDIAN = "guardian", "Guardian"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_memberships",
    )
    role = models.CharField(max_length=16, choices=Role, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_synthetic_bootstrap = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant", "user"], name="unique_tenant_membership"),
            models.CheckConstraint(
                condition=Q(is_active=False, is_synthetic_bootstrap=True, role__isnull=True)
                | Q(is_synthetic_bootstrap=False),
                name="synthetic_membership_dormant_fields_consistent",
            ),
            models.CheckConstraint(
                condition=Q(is_active=False) | Q(role__isnull=False),
                name="active_membership_requires_role",
            ),
        ]
        indexes = [models.Index(fields=["tenant", "user", "is_active"])]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.tenant_id}:{self.role}"


class GuardianAccessGrant(models.Model):
    """
    P3-VS12: Multi-tenant guardian access authorization grant for student learning portfolio.
    Guarantees child privacy and fail-closed visibility.
    """
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        REVOKED = "REVOKED", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="guardian_grants")
    guardian_user_id = models.UUIDField()
    student_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    decided_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tenant", "id"], name="guardian_grant_tenant_id_uniq"),
            models.CheckConstraint(
                condition=Q(status__in=["PENDING", "ACTIVE", "REVOKED"]),
                name="guardian_grant_status_check",
            ),
            models.CheckConstraint(
                condition=(Q(status="REVOKED") & Q(revoked_at__isnull=False)) | (~Q(status="REVOKED") & Q(revoked_at__isnull=True)),
                name="guardian_grant_revoked_check",
            ),
            models.CheckConstraint(
                condition=~Q(status="ACTIVE") | Q(decided_at__isnull=False),
                name="guardian_grant_active_check",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "student_id", "status"], name="idx_guardian_grant_lookup"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.guardian_user_id}->{self.student_id}:{self.status}"
