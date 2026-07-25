from unittest.mock import patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from modules.identity.admin import SafePlatformUserAdmin
from modules.identity.admin_policy import evaluate_admin_policy
from modules.identity.models import PlatformOperatorPolicy, User
from modules.platform_event.security_audit import SecurityAuditError
from modules.platform_tenant.admin import DeniedTenantAdmin
from modules.platform_tenant.models import Tenant


@pytest.fixture
def operator_user(db):
    return User.objects.create_user(
        username="operator_user",
        email="operator@example.com",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="admin_super",
        email="super@example.com",
        password="Password123!",
    )


@pytest.fixture
def target_user(db):
    return User.objects.create_user(
        username="target_user",
        email="target@example.com",
        first_name="Target",
        last_name="User",
    )


@pytest.mark.django_db
class TestAdminPolicyEngine:
    def test_unauthenticated_user_denied(self):
        assert not evaluate_admin_policy(None, "identity.User", "list", "platform_user_safe")

    def test_inactive_user_denied(self, operator_user, superuser):
        operator_user.is_active = False
        operator_user.save()
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        assert not evaluate_admin_policy(
            operator_user, "identity.User", "list", "platform_user_safe"
        )

    def test_non_staff_user_denied(self, superuser):
        non_staff = User.objects.create_user(
            username="non_staff", email="ns@example.com", is_staff=False
        )
        PlatformOperatorPolicy.objects.create(
            operator_user=non_staff,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        assert not evaluate_admin_policy(non_staff, "identity.User", "list", "platform_user_safe")

    def test_superuser_without_policy_denied(self, superuser):
        assert not evaluate_admin_policy(superuser, "identity.User", "list", "platform_user_safe")

    def test_revoked_policy_denied(self, operator_user, superuser):
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=False,
            created_by_user=superuser,
            revoked_at=timezone.now(),
            revoked_by_user=superuser,
        )
        assert not evaluate_admin_policy(
            operator_user, "identity.User", "list", "platform_user_safe"
        )

    def test_permitted_policy_allowed(self, operator_user, superuser):
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        assert evaluate_admin_policy(
            operator_user, "identity.User", "list", "platform_user_safe"
        )
        assert not evaluate_admin_policy(
            operator_user, "identity.User", "view", "platform_user_safe"
        )


@pytest.mark.django_db
class TestSafePlatformUserAdmin:
    def test_list_and_view_fields_strictly_five(self):
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        assert admin_obj.list_display == ("id", "email", "first_name", "last_name", "is_active")
        assert admin_obj.fields == ("id", "email", "first_name", "last_name", "is_active")
        assert admin_obj.readonly_fields == ("id", "email", "first_name", "last_name", "is_active")

    def test_mutations_strictly_disabled(self, rf, operator_user):
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get("/")
        request.user = operator_user
        assert not admin_obj.has_add_permission(request)
        assert not admin_obj.has_change_permission(request)
        assert not admin_obj.has_delete_permission(request)
        assert admin_obj.actions is None

    def test_view_audits_and_fails_closed_on_audit_failure(
        self, rf, operator_user, target_user, superuser
    ):
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="view",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get(f"/admin/identity/user/{target_user.id}/change/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        # Failing audit log must raise PermissionDenied!
        with (
            patch(
                "modules.identity.admin.append_security_event",
                side_effect=SecurityAuditError("audit append failed"),
            ),
            pytest.raises(PermissionDenied),
        ):
            admin_obj.changeform_view(request, object_id=str(target_user.id))

    def test_view_audit_event_logged(self, rf, operator_user, target_user, superuser):
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="view",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get(f"/admin/identity/user/{target_user.id}/change/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        with patch("modules.identity.admin.append_security_event") as mock_append:
            admin_obj.changeform_view(request, object_id=str(target_user.id))
            assert mock_append.called
            event = mock_append.call_args[0][0]
            assert event.event_type == "admin_user_viewed"
            assert event.subject_user_id == target_user.id
            assert event.actor_user_id == operator_user.id

    def test_list_only_policy_direct_object_url_denied_and_audited(
        self, rf, operator_user, target_user, superuser
    ):
        """1. list-only policy + direct object URL: request denied, VIEWED=0, ACTION_DENIED=1."""
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get(f"/admin/identity/user/{target_user.id}/change/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        with patch("modules.identity.admin.append_security_event") as mock_append:
            with pytest.raises(PermissionDenied):
                admin_obj.changeform_view(request, object_id=str(target_user.id))

            assert mock_append.call_count == 1
            event = mock_append.call_args[0][0]
            assert event.event_type == "admin_user_action_denied"
            assert event.actor_user_id == operator_user.id

    def test_list_only_policy_existing_object_non_disclosure(
        self, rf, operator_user, target_user, superuser
    ):
        """2. list-only policy + existing object: object existence is not disclosed."""
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get(f"/admin/identity/user/{target_user.id}/change/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        with patch("modules.identity.admin.SafePlatformUserAdmin.get_object") as mock_get_object:
            with pytest.raises(PermissionDenied):
                admin_obj.changeform_view(request, object_id=str(target_user.id))
            # get_object must NOT be called if user lacks View Policy!
            assert not mock_get_object.called

    def test_view_only_policy_direct_object_url_permitted(
        self, rf, operator_user, target_user, superuser
    ):
        """3. view-only policy + direct object URL: permitted, ADMIN_USER_VIEWED emitted once."""
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="view",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get(f"/admin/identity/user/{target_user.id}/change/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        with patch("modules.identity.admin.append_security_event") as mock_append:
            admin_obj.changeform_view(request, object_id=str(target_user.id))
            assert mock_append.call_count == 1
            event = mock_append.call_args[0][0]
            assert event.event_type == "admin_user_viewed"

    def test_list_page_with_list_policy_permitted_no_view_audit(
        self, rf, operator_user, superuser
    ):
        """5. list page with list policy: permitted, no accidental ADMIN_USER_VIEWED event."""
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get("/admin/identity/user/")
        request.user = operator_user

        with patch("modules.identity.admin.append_security_event") as mock_append:
            qs = admin_obj.get_queryset(request)
            assert qs.count() > 0
            assert not mock_append.called

    def test_direct_view_without_policy_denied(self, rf, operator_user, target_user):
        """6. direct view without policy: denied, no success audit."""
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get(f"/admin/identity/user/{target_user.id}/change/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        with patch("modules.identity.admin.append_security_event") as mock_append:
            with pytest.raises(PermissionDenied):
                admin_obj.changeform_view(request, object_id=str(target_user.id))

            assert mock_append.call_count == 1
            event = mock_append.call_args[0][0]
            assert event.event_type == "admin_user_action_denied"


@pytest.mark.django_db
class TestDeniedTenantAdmin:
    def test_tenant_admin_strictly_denies_all_users(self, rf, superuser, operator_user):
        admin_obj = DeniedTenantAdmin(Tenant, AdminSite())
        for user in (superuser, operator_user):
            request = rf.get("/admin/platform_tenant/tenant/")
            request.user = user
            assert not admin_obj.has_module_permission(request)
            assert not admin_obj.has_view_permission(request)
            assert not admin_obj.has_add_permission(request)
            assert not admin_obj.has_change_permission(request)
            assert not admin_obj.has_delete_permission(request)
            assert admin_obj.get_queryset(request).count() == 0
            assert admin_obj.actions is None
