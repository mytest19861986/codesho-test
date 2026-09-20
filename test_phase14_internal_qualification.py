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
    IsInternalQualifiedUser,
    IsTenantLearner,
    IsTenantMentor,
    IsTenantGuardian,
)
from modules.platform_tenant.models import TenantMembership

class TestPhase14InternalWriteQualification(unittest.TestCase):
    """
    Wave 5.6 Phase 14: Stage 1 Internal Qualification — Controlled Write Enablement
    Validates internal test account allowlisting, blocking public real users, and mutation safety.
    """

    def setUp(self):
        self.tenant_id = uuid4()
        self.staff_learner = MagicMock(is_authenticated=True, is_staff=True, is_superuser=False)
        self.staff_mentor = MagicMock(is_authenticated=True, is_staff=True, is_superuser=False)
        self.staff_guardian = MagicMock(is_authenticated=True, is_staff=True, is_superuser=False)
        self.public_real_user = MagicMock(is_authenticated=True, is_staff=False, is_superuser=False, is_internal_test=False)

    def test_internal_qualified_user_staff_allowed(self):
        """Internal staff account is permitted through Stage 1 gate."""
        perm = IsInternalQualifiedUser()
        req = MagicMock(user=self.staff_learner)
        self.assertTrue(perm.has_permission(req, None))

    def test_internal_qualified_user_public_real_user_denied(self):
        """Public real user is strictly blocked by IsInternalQualifiedUser fail-closed."""
        perm = IsInternalQualifiedUser()
        req = MagicMock(user=self.public_real_user)
        self.assertFalse(perm.has_permission(req, None))

    def test_internal_qualified_unauthenticated_denied(self):
        """Unauthenticated user is strictly blocked."""
        perm = IsInternalQualifiedUser()
        req = MagicMock(user=MagicMock(is_authenticated=False))
        self.assertFalse(perm.has_permission(req, None))

    def test_dual_gate_learner_and_internal_staff_passes(self):
        """Learner role who is also internal staff passes both role and stage 1 qualification gates."""
        role_perm = IsTenantLearner()
        stage1_perm = IsInternalQualifiedUser()
        req = MagicMock(
            tenant=MagicMock(id=self.tenant_id),
            user=self.staff_learner,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertTrue(role_perm.has_permission(req, None))
        self.assertTrue(stage1_perm.has_permission(req, None))

    def test_dual_gate_learner_public_real_user_fails(self):
        """Learner role who is a public real user passes role gate but fails Stage 1 internal gate."""
        role_perm = IsTenantLearner()
        stage1_perm = IsInternalQualifiedUser()
        req = MagicMock(
            tenant=MagicMock(id=self.tenant_id),
            user=self.public_real_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertTrue(role_perm.has_permission(req, None))
        self.assertFalse(stage1_perm.has_permission(req, None))

if __name__ == "__main__":
    unittest.main()
