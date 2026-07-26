import uuid
from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse

from modules.identity.admin_policy import evaluate_admin_policy
from modules.identity.models import User
from modules.platform_event.security_audit import (
    SecurityAuditError,
    admin_tenant_access_denied,
    admin_user_action_denied,
    admin_user_viewed,
    append_security_event,
)
from modules.platform_tenant.models import Tenant, TenantMembership

if TYPE_CHECKING:
    _UserAdminBase = admin.ModelAdmin[User]
    _TenantAdminBase = admin.ModelAdmin[Tenant]
    _TenantMembershipAdminBase = admin.ModelAdmin[TenantMembership]
else:
    _UserAdminBase = admin.ModelAdmin
    _TenantAdminBase = admin.ModelAdmin
    _TenantMembershipAdminBase = admin.ModelAdmin


class SafePlatformUserAdmin(_UserAdminBase):
    list_display = ("id", "email", "first_name", "last_name", "is_active")
    fields = ("id", "email", "first_name", "last_name", "is_active")
    readonly_fields = ("id", "email", "first_name", "last_name", "is_active")
    search_fields = ()
    actions = None

    def __init__(self, model: type[User], admin_site: admin.AdminSite) -> None:
        super().__init__(model, admin_site)
        self._allowed_lookup_requests: set[int] = set()

    def has_add_permission(self, request: HttpRequest) -> bool:
        if request.method == "POST":
            self._audit_denied(request)
        return False

    def has_change_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        if request.method == "POST":
            self._audit_denied(request, subject_user_id=obj.id if obj else None)
        return False

    def has_delete_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        if request.method == "POST":
            self._audit_denied(request, subject_user_id=obj.id if obj else None)
        return False

    def has_module_permission(self, request: HttpRequest) -> bool:
        has_list = evaluate_admin_policy(
            getattr(request, "user", None), "identity.User", "list", "platform_user_safe"
        )
        has_view = evaluate_admin_policy(
            getattr(request, "user", None), "identity.User", "view", "platform_user_safe"
        )
        if not (has_list or has_view):
            self._audit_denied(request)
            return False
        return True

    def has_view_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        action = "view" if obj is not None else "list"

        allowed = evaluate_admin_policy(
            getattr(request, "user", None), "identity.User", action, "platform_user_safe"
        )
        if not allowed:
            self._audit_denied(request, subject_user_id=obj.id if obj else None)
            return False
        return True

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        qs = super().get_queryset(request)
        user = getattr(request, "user", None)
        has_list = evaluate_admin_policy(user, "identity.User", "list", "platform_user_safe")
        has_view = evaluate_admin_policy(user, "identity.User", "view", "platform_user_safe")

        if has_list:
            return qs

        if has_view and id(request) in self._allowed_lookup_requests:
            return qs

        return qs.none()

    def get_object(
        self, request: HttpRequest, object_id: str, from_field: str | None = None
    ) -> User | None:
        has_view = evaluate_admin_policy(
            getattr(request, "user", None), "identity.User", "view", "platform_user_safe"
        )
        if not has_view:
            return None

        self._allowed_lookup_requests.add(id(request))
        try:
            return super().get_object(request, object_id, from_field=from_field)
        finally:
            self._allowed_lookup_requests.discard(id(request))

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        if object_id is not None:
            if request.method == "POST":
                self._audit_denied(request)
                raise PermissionDenied("administrative mutations are disabled")
            # 1. Strictly enforce View Policy BEFORE object lookup or success audit logging
            user = getattr(request, "user", None)
            has_view_policy = evaluate_admin_policy(
                user, "identity.User", "view", "platform_user_safe"
            )
            if not has_view_policy:
                # Audit DENIED attempt and reject immediately
                self._audit_denied(request)
                raise PermissionDenied("View policy required for object access")

            # 2. Retrieve object only after View Policy is confirmed
            obj = self.get_object(request, object_id)

            if obj is not None:
                # 3. Must emit audit event before rendering. If append fails, fail-closed!
                actor_id = (
                    getattr(user, "id", None)
                    if user and getattr(user, "is_authenticated", False)
                    else None
                )
                try:
                    event = admin_user_viewed(
                        event_id=uuid.uuid4(),
                        correlation_id=uuid.uuid4(),
                        subject_user_id=obj.id,
                        actor_user_id=actor_id,
                    )
                    append_security_event(event)
                except SecurityAuditError:
                    raise PermissionDenied("audit logging failed") from None
                except Exception as exc:
                    raise PermissionDenied("audit logging failed") from exc

        return super().changeform_view(request, object_id, form_url, extra_context)

    def add_view(
        self,
        request: HttpRequest,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        if request.method == "POST":
            self._audit_denied(request)
            raise PermissionDenied("administrative mutations are disabled")
        return super().add_view(request, form_url, extra_context)

    def delete_view(
        self,
        request: HttpRequest,
        object_id: str,
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        self._audit_denied(request)
        raise PermissionDenied("administrative mutations are disabled")

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        if request.method == "POST":
            self._audit_denied(request)
            raise PermissionDenied("administrative mutations are disabled")
        return super().changelist_view(request, extra_context)

    def _audit_denied(
        self, request: HttpRequest, subject_user_id: uuid.UUID | None = None
    ) -> None:
        if request.META.get("_codesho_admin_denial_audited"):
            return
        request.META["_codesho_admin_denial_audited"] = True
        try:
            user = getattr(request, "user", None)
            actor_id = (
                getattr(user, "id", None)
                if user and getattr(user, "is_authenticated", False)
                else None
            )
            event = admin_user_action_denied(
                event_id=uuid.uuid4(),
                correlation_id=uuid.uuid4(),
                subject_user_id=subject_user_id,
                actor_user_id=actor_id,
            )
            append_security_event(event)
        except Exception:
            raise PermissionDenied("administrative access denied") from None


class BaseDeniedTenantAdminMixin:
    def _audit_denied(self, request: HttpRequest) -> None:
        if request.META.get("_codesho_admin_denial_audited"):
            return
        request.META["_codesho_admin_denial_audited"] = True
        try:
            user = getattr(request, "user", None)
            actor_id = (
                getattr(user, "id", None)
                if user and getattr(user, "is_authenticated", False)
                else None
            )
            event = admin_tenant_access_denied(
                event_id=uuid.uuid4(),
                correlation_id=uuid.uuid4(),
                actor_user_id=actor_id,
            )
            append_security_event(event)
        except Exception:
            raise PermissionDenied("administrative access denied") from None


class DeniedTenantAdmin(_TenantAdminBase, BaseDeniedTenantAdminMixin):
    actions = None

    def has_module_permission(self, request: HttpRequest) -> bool:
        self._audit_denied(request)
        return False

    def has_view_permission(self, request: HttpRequest, obj: Tenant | None = None) -> bool:
        self._audit_denied(request)
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        self._audit_denied(request)
        return False

    def has_change_permission(self, request: HttpRequest, obj: Tenant | None = None) -> bool:
        self._audit_denied(request)
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Tenant | None = None) -> bool:
        self._audit_denied(request)
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Tenant]:
        return super().get_queryset(request).none()


class DeniedTenantMembershipAdmin(_TenantMembershipAdminBase, BaseDeniedTenantAdminMixin):
    actions = None

    def has_module_permission(self, request: HttpRequest) -> bool:
        self._audit_denied(request)
        return False

    def has_view_permission(
        self, request: HttpRequest, obj: TenantMembership | None = None
    ) -> bool:
        self._audit_denied(request)
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        self._audit_denied(request)
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: TenantMembership | None = None
    ) -> bool:
        self._audit_denied(request)
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: TenantMembership | None = None
    ) -> bool:
        self._audit_denied(request)
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[TenantMembership]:
        return super().get_queryset(request).none()


def register_platform_admin() -> None:
    if admin.site.is_registered(User):
        admin.site.unregister(User)
    if admin.site.is_registered(Tenant):
        admin.site.unregister(Tenant)
    if admin.site.is_registered(TenantMembership):
        admin.site.unregister(TenantMembership)

    admin.site.register(User, SafePlatformUserAdmin)
    admin.site.register(Tenant, DeniedTenantAdmin)
    admin.site.register(TenantMembership, DeniedTenantMembershipAdmin)


register_platform_admin()
