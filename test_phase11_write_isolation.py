import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.learning_loop.permissions import IsTenantLearner, IsTenantMentor, IsTenantGuardian, IsTenantMember
from modules.learning_loop.serializers import SubmitEvidenceInputSerializer
from modules.platform_tenant.models import TenantMembership

class TestPhase11WritePathIsolation(unittest.TestCase):
    """
    Wave 5.6 Phase 11: Write Path Implementation in Isolation Test Suite
    Enforces permissions, cross-tenant/cross-learner safety, and transaction-scoped validation.
    """

    def setUp(self):
        self.tenant_a = MagicMock(id=uuid4())
        self.tenant_b = MagicMock(id=uuid4())
        self.learner_user = MagicMock(id=uuid4(), is_authenticated=True)
        self.mentor_user = MagicMock(id=uuid4(), is_authenticated=True)
        self.guardian_user = MagicMock(id=uuid4(), is_authenticated=True)

    def test_permission_learner_can_submit_evidence(self):
        """Learner role in active tenant has permission to submit evidence."""
        perm = IsTenantLearner()
        request = MagicMock(
            tenant=self.tenant_a,
            user=self.learner_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertTrue(perm.has_permission(request, None))

    def test_permission_mentor_denied_evidence_submission(self):
        """Mentor cannot submit evidence on behalf of learner (Role boundary)."""
        perm = IsTenantLearner()
        request = MagicMock(
            tenant=self.tenant_a,
            user=self.mentor_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.MENTOR),
        )
        self.assertFalse(perm.has_permission(request, None))

    def test_permission_guardian_denied_evidence_submission(self):
        """Guardian cannot submit technical learning evidence (Role boundary)."""
        perm = IsTenantLearner()
        request = MagicMock(
            tenant=self.tenant_a,
            user=self.guardian_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.GUARDIAN),
        )
        self.assertFalse(perm.has_permission(request, None))

    def test_permission_cross_tenant_evidence_submission_denied(self):
        """Request targeting different tenant without membership fails closed."""
        perm = IsTenantLearner()
        request = MagicMock(
            tenant=self.tenant_b,
            user=self.learner_user,
            tenant_membership=MagicMock(is_active=False, role=TenantMembership.Role.LEARNER),
        )
        self.assertFalse(perm.has_permission(request, None))

    def test_evidence_serializer_validation_success(self):
        """Valid evidence payload passes serializer."""
        data = {
            "repo_branch": "feat/async-retry",
            "commit_hash": "a1b2c3d",
            "current_milestone": "پیاده‌سازی مکانیزم Retry",
            "recent_activity": "تست در محیط توسعه",
            "last_code_snippet": "async function retry() {}",
            "progress_percentage": 85,
        }
        serializer = SubmitEvidenceInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["progress_percentage"], 85)

    def test_evidence_serializer_validation_invalid_hash(self):
        """Commit hash shorter than 7 chars is rejected."""
        data = {
            "repo_branch": "feat/async-retry",
            "commit_hash": "short",
            "current_milestone": "پیاده‌سازی",
            "recent_activity": "تست",
        }
        serializer = SubmitEvidenceInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("commit_hash", serializer.errors)

    def test_evidence_serializer_validation_invalid_progress(self):
        """Progress percentage above 100 is rejected."""
        data = {
            "repo_branch": "feat/async-retry",
            "commit_hash": "a1b2c3d",
            "current_milestone": "پیاده‌سازی",
            "recent_activity": "تست",
            "progress_percentage": 105,
        }
        serializer = SubmitEvidenceInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("progress_percentage", serializer.errors)

if __name__ == "__main__":
    unittest.main()
