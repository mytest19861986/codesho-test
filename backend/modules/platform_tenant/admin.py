import uuid
from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.db.models import Model, QuerySet
from django.http import HttpRequest

from modules.platform_event.security_audit import (
    admin_tenant_access_denied,
    append_security_event,
)

from .models import Tenant, TenantMembership

if TYPE_CHECKING:
    _ModelAdminBase = admin.ModelAdmin[Any]
else:
    _ModelAdminBase = admin.ModelAdmin


class DeniedTenantAdmin(_ModelAdminBase):
    actions = None

    def has_module_permission(self, request: HttpRequest) -> bool:
        self._audit_denied(request)
        return False

    def has_view_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        self._audit_denied(request)
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        self._audit_denied(request)
        return False

    def has_change_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        self._audit_denied(request)
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        self._audit_denied(request)
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).none()

    def _audit_denied(self, request: HttpRequest) -> None:
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
            pass


admin.site.unregister(Tenant) if admin.site.is_registered(Tenant) else None
admin.site.unregister(TenantMembership) if admin.site.is_registered(TenantMembership) else None

admin.site.register(Tenant, DeniedTenantAdmin)
admin.site.register(TenantMembership, DeniedTenantAdmin)
