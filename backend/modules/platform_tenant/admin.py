import uuid

from django.contrib import admin

from modules.platform_event.security_audit import (
    admin_tenant_access_denied,
    append_security_event,
)

from .models import Tenant, TenantMembership


class DeniedTenantAdmin(admin.ModelAdmin):
    actions = None

    def has_module_permission(self, request) -> bool:
        self._audit_denied(request)
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        self._audit_denied(request)
        return False

    def has_add_permission(self, request) -> bool:
        self._audit_denied(request)
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        self._audit_denied(request)
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        self._audit_denied(request)
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def _audit_denied(self, request) -> None:
        try:
            actor_id = request.user.id if request.user and request.user.is_authenticated else None
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
