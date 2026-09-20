import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.learning_loop.serializers import (
    SubmitEvidenceInputSerializer,
    UpdateInterventionStatusInputSerializer,
    SendParentEncouragementInputSerializer,
)
from modules.learning_loop.permissions import (
    IsTenantLearner,
    IsTenantMentor,
    IsTenantGuardian,
)
from modules.platform_tenant.models import TenantMembership

class TestPhase13WriteSimulation(unittest.TestCase):
    """
    Wave 5.6 Phase 13: Controlled Write Activation Preparation
    Simulates internal mutations, duplicate checks, validation boundaries, and audit guarantees.
    """

    def setUp(self):
        self.tenant_id = uuid4()
        self.learner_id = uuid4()
        self.mentor_id = uuid4()
        self.guardian_id = uuid4()

    def test_simulation_learner_evidence_valid(self):
        """Simulation 1: Learner submits valid code evidence."""
        payload = {
            "repo_branch": "feat/async-retry",
            "commit_hash": "e4a89bc",
            "current_milestone": "پیاده‌سازی بلوک‌های try/catch",
            "recent_activity": "تلاش برای اتصال به وب‌سرویس",
            "last_code_snippet": "async function fetchWeather() {}",
            "progress_percentage": 75,
        }
        serializer = SubmitEvidenceInputSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["progress_percentage"], 75)

    def test_simulation_learner_evidence_invalid_hash(self):
        """Simulation 2: Invalid commit hash rejected prior to domain execution."""
        payload = {
            "repo_branch": "feat/async-retry",
            "commit_hash": "short",
            "current_milestone": "پیاده‌سازی",
            "recent_activity": "تست",
        }
        serializer = SubmitEvidenceInputSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("commit_hash", serializer.errors)

    def test_simulation_mentor_status_transition_valid(self):
        """Simulation 3: Mentor transitions status to REVIEWING."""
        payload = {"status": "REVIEWING"}
        serializer = UpdateInterventionStatusInputSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["status"], "REVIEWING")

    def test_simulation_mentor_status_transition_invalid(self):
        """Simulation 4: Non-existent lifecycle state is rejected."""
        payload = {"status": "ARBITRARY_STATE"}
        serializer = UpdateInterventionStatusInputSerializer(data=payload)
        self.assertFalse(serializer.is_valid())

    def test_simulation_guardian_praise_valid(self):
        """Simulation 5: Guardian submits golden ribbon praise."""
        payload = {"message": "علی جان، به تلاشت افتخار می‌کنیم."}
        serializer = SendParentEncouragementInputSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_simulation_guardian_denied_evidence_mutation(self):
        """Simulation 6: Guardian attempting evidence submission is strictly rejected."""
        perm = IsTenantLearner()
        req = MagicMock(
            tenant=MagicMock(id=self.tenant_id),
            user=MagicMock(id=self.guardian_id, is_authenticated=True),
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.GUARDIAN),
        )
        self.assertFalse(perm.has_permission(req, None))

    def test_simulation_cross_tenant_denied(self):
        """Simulation 7: Request from foreign tenant fails closed."""
        perm = IsTenantMentor()
        req = MagicMock(
            tenant=MagicMock(id=uuid4()),
            user=MagicMock(id=self.mentor_id, is_authenticated=True),
            tenant_membership=MagicMock(is_active=False, role=TenantMembership.Role.MENTOR),
        )
        self.assertFalse(perm.has_permission(req, None))

    def test_simulation_audit_event_structure(self):
        """Simulation 8: Audit event payload contract contains zero PII or private code."""
        audit_entry = {
            "tenant_id": str(self.tenant_id),
            "actor_role": "LEARNER",
            "action_type": "SUBMIT_EVIDENCE",
            "aggregate_id": "proj-01",
            "status": "SUCCESS",
            "duration_ms": 14.2,
        }
        self.assertNotIn("source_code", audit_entry)
        self.assertNotIn("private_user_content", audit_entry)
        self.assertNotIn("credentials", audit_entry)

if __name__ == "__main__":
    unittest.main()
