from unittest.mock import patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError, connection
from django.utils import timezone

from config.platform_admin import (
    DeniedTenantAdmin,
    DeniedTenantMembershipAdmin,
    SafePlatformUserAdmin,
    register_platform_admin,
)
from modules.identity.admin_policy import evaluate_admin_policy
from modules.identity.models import PlatformOperatorPolicy, User
from modules.platform_event.security_audit import SecurityAuditError
from modules.platform_tenant.models import Tenant, TenantMembership


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
class TestCompositionRootRegistration:
    def test_registration_idempotency_and_composition_root(self):
        """Verify registering platform admin from composition root is idempotent."""
        register_platform_admin()
        register_platform_admin()


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

    def test_1_list_policy_permits_changelist(self, rf, operator_user, target_user, superuser):
        """1. list policy permits changelist."""
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

        qs = admin_obj.get_queryset(request)
        assert qs.count() > 0
        assert target_user in qs

    def test_2_list_policy_denies_object_view(self, rf, operator_user, target_user, superuser):
        """2. list policy denies object view."""
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

        with pytest.raises(PermissionDenied):
            admin_obj.changeform_view(request, object_id=str(target_user.id))

    def test_3_view_policy_permits_exact_object_view(
        self, rf, operator_user, target_user, superuser
    ):
        """3. view policy permits exact object view."""
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

        obj = admin_obj.get_object(request, str(target_user.id))
        assert obj == target_user

    def test_4_view_only_policy_does_not_expose_changelist(
        self, rf, operator_user, target_user, superuser
    ):
        """4. view-only policy does not expose changelist."""
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="view",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get("/admin/identity/user/")
        request.user = operator_user

        qs = admin_obj.get_queryset(request)
        assert qs.count() == 0

    def test_5_url_containing_change_outside_object_view_context(
        self, rf, operator_user, superuser
    ):
        """5. URL containing 'change' outside object-view does not alter authorization."""
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.get("/admin/identity/user/?q=change_something")
        request.user = operator_user

        qs = admin_obj.get_queryset(request)
        assert qs.count() > 0

    def test_6_direct_invocation_without_normal_path(self, operator_user, target_user, superuser):
        """6. direct invocation/context without a normal path still applies correct policy."""
        PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="view",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        admin_obj = SafePlatformUserAdmin(User, AdminSite())

        class EmptyRequest:
            user = operator_user

        req = EmptyRequest()
        obj = admin_obj.get_object(req, str(target_user.id))
        assert obj == target_user

    def test_7_denied_attempt_emits_exactly_one_denial_event(
        self, rf, operator_user, target_user, superuser
    ):
        """7. denied attempt emits exactly one denial event."""
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

        with patch("config.platform_admin.append_security_event") as mock_append:
            with pytest.raises(PermissionDenied):
                admin_obj.changeform_view(request, object_id=str(target_user.id))

            assert mock_append.call_count == 1
            event = mock_append.call_args[0][0]
            assert event.event_type == "admin_user_action_denied"

    def test_8_permitted_object_view_emits_exactly_one_viewed_event(
        self, rf, operator_user, target_user, superuser
    ):
        """8. permitted object view emits exactly one viewed event."""
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

        with patch("config.platform_admin.append_security_event") as mock_append:
            admin_obj.changeform_view(request, object_id=str(target_user.id))
            assert mock_append.call_count == 1
            event = mock_append.call_args[0][0]
            assert event.event_type == "admin_user_viewed"

    def test_9_no_object_lookup_occurs_before_view_authorization(
        self, rf, operator_user, target_user, superuser
    ):
        """9. no object lookup occurs before view authorization."""
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

        with patch.object(SafePlatformUserAdmin, "get_object") as mock_get_object:
            with pytest.raises(PermissionDenied):
                admin_obj.changeform_view(request, object_id=str(target_user.id))

            assert not mock_get_object.called

    def test_10_audit_failure_remains_fail_closed(
        self, rf, operator_user, target_user, superuser
    ):
        """10. audit failure remains fail-closed."""
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

        with (
            patch(
                "config.platform_admin.append_security_event",
                side_effect=SecurityAuditError("audit append failed"),
            ),
            pytest.raises(PermissionDenied),
        ):
            admin_obj.changeform_view(request, object_id=str(target_user.id))

    @pytest.mark.parametrize("mutation", ["add", "change", "delete", "action"])
    def test_direct_mutation_posts_emit_one_denial_and_never_view_event(
        self, rf, operator_user, target_user, superuser, mutation
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
        request = rf.post("/admin/identity/user/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        with patch("config.platform_admin.append_security_event") as mock_append, pytest.raises(
            PermissionDenied
        ):
            if mutation == "add":
                admin_obj.add_view(request)
            elif mutation == "change":
                admin_obj.changeform_view(request, object_id=str(target_user.id))
            elif mutation == "delete":
                admin_obj.delete_view(request, object_id=str(target_user.id))
            else:
                admin_obj.changelist_view(request)

        assert mock_append.call_count == 1
        assert mock_append.call_args.args[0].event_type == "admin_user_action_denied"

    def test_denied_mutation_audit_failure_has_no_user_data(self, rf, operator_user, target_user):
        admin_obj = SafePlatformUserAdmin(User, AdminSite())
        request = rf.post(f"/admin/identity/user/{target_user.id}/change/")
        request.user = operator_user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        with patch(
            "config.platform_admin.append_security_event",
            side_effect=SecurityAuditError("audit append failed"),
        ), pytest.raises(PermissionDenied) as exc_info:
            admin_obj.changeform_view(request, object_id=str(target_user.id))

        assert str(target_user.id) not in str(exc_info.value)
        assert target_user.email not in str(exc_info.value)


@pytest.mark.django_db
class TestDeniedTenantAdmin:
    def test_tenant_admin_strictly_denies_all_users(self, rf, superuser, operator_user):
        admin_tenant = DeniedTenantAdmin(Tenant, AdminSite())
        admin_membership = DeniedTenantMembershipAdmin(TenantMembership, AdminSite())
        for admin_obj in (admin_tenant, admin_membership):
            for user in (superuser, operator_user):
                request = rf.get("/")
                request.user = user
                with patch("config.platform_admin.append_security_event"):
                    assert not admin_obj.has_module_permission(request)
                    assert not admin_obj.has_view_permission(request)
                    assert not admin_obj.has_add_permission(request)
                    assert not admin_obj.has_change_permission(request)
                    assert not admin_obj.has_delete_permission(request)
                    assert admin_obj.get_queryset(request).count() == 0
                    assert admin_obj.actions is None


@pytest.mark.django_db
class TestPlatformOperatorPolicyImmutability:
    def test_model_only_allows_one_active_to_revoked_transition(self, operator_user, superuser):
        policy = PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )

        policy.action = "view"
        with pytest.raises(ValidationError):
            policy.save()
        policy.refresh_from_db()

        policy.active = False
        policy.revoked_at = timezone.now()
        policy.revoked_by_user = superuser
        policy.save()

        policy.active = True
        with pytest.raises(ValidationError):
            policy.save()
        with pytest.raises(ValidationError):
            policy.delete()

    @pytest.mark.skipif(connection.vendor != "postgresql", reason="requires PostgreSQL trigger")
    def test_postgresql_rejects_raw_sql_delete_reactivation_and_broadening(
        self, operator_user, superuser
    ):
        policy = PlatformOperatorPolicy.objects.create(
            operator_user=operator_user,
            model_label="identity.User",
            action="list",
            scope_kind="platform_user_safe",
            active=True,
            created_by_user=superuser,
        )
        with connection.cursor() as cursor:
            with pytest.raises(DatabaseError):
                cursor.execute(
                    "DELETE FROM codesho.identity_platformoperatorpolicy WHERE id = %s", [policy.id]
                )
            with pytest.raises(DatabaseError):
                cursor.execute(
                    "UPDATE codesho.identity_platformoperatorpolicy "
                    "SET action = 'view' WHERE id = %s",
                    [policy.id],
                )
            cursor.execute(
                """
                UPDATE codesho.identity_platformoperatorpolicy
                SET active = FALSE, revoked_at = CURRENT_TIMESTAMP, revoked_by_user_id = %s
                WHERE id = %s
                """,
                [superuser.id, policy.id],
            )
            with pytest.raises(DatabaseError):
                cursor.execute(
                    "UPDATE codesho.identity_platformoperatorpolicy "
                    "SET active = TRUE WHERE id = %s",
                    [policy.id],
                )
