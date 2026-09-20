import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.learning_loop.permissions import (
    IsPilotTenantOrInternalQualified,
    IsTenantLearner,
    IsTenantMentor,
    IsTenantGuardian,
)
from modules.platform_tenant.models import TenantMembership

class TestPhase15LimitedTenantPilot(unittest.TestCase):
    """
    Wave 5.6 Phase 15: Stage 2 — Limited Tenant Pilot Test Suite
    Enforces that write is permitted ONLY for the designated pilot tenant (learning_write_enabled=True)
    or internal staff, while foreign/unactivated tenants remain strictly locked (fail-closed).
    """

    def setUp(self):
        self.pilot_tenant = MagicMock(id=uuid4(), learning_write_enabled=True)
        self.non_pilot_tenant = MagicMock(id=uuid4(), learning_write_enabled=False)
        self.learner_user = MagicMock(is_authenticated=True, is_staff=False, is_superuser=False, is_internal_test=False)
        self.staff_user = MagicMock(is_authenticated=True, is_staff=True, is_superuser=False)

    def test_pilot_tenant_user_authorized(self):
        """User belonging to designated pilot tenant (learning_write_enabled=True) is authorized."""
        perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(tenant=self.pilot_tenant, user=self.learner_user)
        self.assertTrue(perm.has_permission(req, None))

    def test_non_pilot_tenant_user_denied(self):
        """User belonging to non-pilot tenant (learning_write_enabled=False) is strictly denied (403)."""
        perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(tenant=self.non_pilot_tenant, user=self.learner_user)
        self.assertFalse(perm.has_permission(req, None))

    def test_staff_user_authorized_on_any_tenant(self):
        """Internal staff user is authorized across all tenants for testing/audit."""
        perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(tenant=self.non_pilot_tenant, user=self.staff_user)
        self.assertTrue(perm.has_permission(req, None))

    def test_no_tenant_context_denied(self):
        """Request lacking valid tenant context fails closed immediately."""
        perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(tenant=None, user=self.learner_user)
        self.assertFalse(perm.has_permission(req, None))

    def test_unauthenticated_request_denied(self):
        """Unauthenticated request is strictly denied."""
        perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(tenant=self.pilot_tenant, user=MagicMock(is_authenticated=False))
        self.assertFalse(perm.has_permission(req, None))

    def test_pilot_tenant_dual_gate_learner_allowed(self):
        """Learner in pilot tenant satisfies both role gate and pilot gate."""
        role_perm = IsTenantLearner()
        pilot_perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(
            tenant=self.pilot_tenant,
            user=self.learner_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertTrue(role_perm.has_permission(req, None))
        self.assertTrue(pilot_perm.has_permission(req, None))

    def test_non_pilot_tenant_dual_gate_learner_blocked(self):
        """Learner in non-pilot tenant satisfies role gate but fails pilot gate."""
        role_perm = IsTenantLearner()
        pilot_perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(
            tenant=self.non_pilot_tenant,
            user=self.learner_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertTrue(role_perm.has_permission(req, None))
        self.assertFalse(pilot_perm.has_permission(req, None))

if __name__ == "__main__":
    unittest.main()
