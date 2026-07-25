import uuid

from django.contrib import admin
from django.core.exceptions import PermissionDenied

from modules.platform_event.security_audit import (
    SecurityAuditError,
    admin_user_action_denied,
    admin_user_viewed,
    append_security_event,
)

from .admin_policy import evaluate_admin_policy
from .models import User


class SafePlatformUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name", "is_active")
    fields = ("id", "email", "first_name", "last_name", "is_active")
    readonly_fields = ("id", "email", "first_name", "last_name", "is_active")
    search_fields = ()
    actions = None

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_module_permission(self, request) -> bool:
        has_list = evaluate_admin_policy(
            request.user, "identity.User", "list", "platform_user_safe"
        )
        has_view = evaluate_admin_policy(
            request.user, "identity.User", "view", "platform_user_safe"
        )
        if not (has_list or has_view):
            self._audit_denied(request)
            return False
        return True

    def has_view_permission(self, request, obj=None) -> bool:
        if obj is not None or (request and hasattr(request, "path") and "change" in request.path):
            action = "view"
        else:
            action = "list"

        allowed = evaluate_admin_policy(
            request.user, "identity.User", action, "platform_user_safe"
        )
        if not allowed:
            self._audit_denied(request, subject_user_id=obj.id if obj else None)
            return False
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Determine if request is targeting changelist or specific object view
        if request and hasattr(request, "path") and "change" in request.path:
            has_perm = evaluate_admin_policy(
                request.user, "identity.User", "view", "platform_user_safe"
            )
        else:
            has_perm = evaluate_admin_policy(
                request.user, "identity.User", "list", "platform_user_safe"
            )
        if not has_perm:
            return qs.none()
        return qs

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id is not None:
            # 1. Strictly enforce View Policy BEFORE object lookup or success audit logging
            has_view_policy = evaluate_admin_policy(
                request.user, "identity.User", "view", "platform_user_safe"
            )
            if not has_view_policy:
                # Audit DENIED attempt and reject immediately
                self._audit_denied(request)
                raise PermissionDenied("View policy required for object access")

            # 2. Retrieve object only after View Policy is confirmed
            try:
                obj = self.get_object(request, object_id)
            except Exception:
                obj = None

            if obj is not None:
                # 3. Must emit audit event before rendering. If append fails, fail-closed!
                try:
                    event = admin_user_viewed(
                        event_id=uuid.uuid4(),
                        correlation_id=uuid.uuid4(),
                        subject_user_id=obj.id,
                        actor_user_id=request.user.id if request.user.is_authenticated else None,
                    )
                    append_security_event(event)
                except SecurityAuditError:
                    raise PermissionDenied("audit logging failed") from None
                except Exception as exc:
                    raise PermissionDenied("audit logging failed") from exc

        return super().changeform_view(request, object_id, form_url, extra_context)

    def _audit_denied(self, request, subject_user_id=None) -> None:
        try:
            actor_id = request.user.id if request.user and request.user.is_authenticated else None
            event = admin_user_action_denied(
                event_id=uuid.uuid4(),
                correlation_id=uuid.uuid4(),
                subject_user_id=subject_user_id,
                actor_user_id=actor_id,
            )
            append_security_event(event)
        except Exception:
            pass


admin.site.unregister(User) if admin.site.is_registered(User) else None
admin.site.register(User, SafePlatformUserAdmin)
