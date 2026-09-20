from rest_framework import permissions
from modules.platform_tenant.models import TenantMembership


class IsTenantMember(permissions.BasePermission):
    """
    Ensure the user has an active membership within the requested tenant.
    """
    def has_permission(self, request, view):
        tenant = getattr(request, "tenant", None)
        if not tenant or not request.user or not request.user.is_authenticated:
            return False
        membership = getattr(request, "tenant_membership", None)
        if not membership:
            membership = TenantMembership.objects.filter(
                tenant=tenant, user=request.user, is_active=True
            ).first()
        return bool(membership and membership.is_active)


class IsTenantMentor(permissions.BasePermission):
    """
    Requires MENTOR, ADMIN, or OWNER role in active tenant.
    """
    def has_permission(self, request, view):
        if not IsTenantMember().has_permission(request, view):
            return False
        membership = getattr(request, "tenant_membership", None)
        if not membership:
            membership = TenantMembership.objects.filter(
                tenant=request.tenant, user=request.user, is_active=True
            ).first()
        return membership and membership.role in [
            TenantMembership.Role.MENTOR,
            TenantMembership.Role.ADMIN,
            TenantMembership.Role.OWNER,
        ]


class IsTenantGuardian(permissions.BasePermission):
    """
    Requires GUARDIAN, ADMIN, or OWNER role in active tenant.
    """
    def has_permission(self, request, view):
        if not IsTenantMember().has_permission(request, view):
            return False
        membership = getattr(request, "tenant_membership", None)
        if not membership:
            membership = TenantMembership.objects.filter(
                tenant=request.tenant, user=request.user, is_active=True
            ).first()
        return membership and membership.role in [
            TenantMembership.Role.GUARDIAN,
            TenantMembership.Role.ADMIN,
            TenantMembership.Role.OWNER,
        ]


class IsTenantLearner(permissions.BasePermission):
    """
    Requires LEARNER role in active tenant.
    """
    def has_permission(self, request, view):
        if not IsTenantMember().has_permission(request, view):
            return False
        membership = getattr(request, "tenant_membership", None)
        if not membership:
            membership = TenantMembership.objects.filter(
                tenant=request.tenant, user=request.user, is_active=True
            ).first()
        return bool(membership and membership.role == TenantMembership.Role.LEARNER)
