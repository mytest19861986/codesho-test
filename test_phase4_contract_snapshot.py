import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.platform_tenant.models import TenantMembership
from modules.learning_loop.intelligence_projections import IntelligenceReadProjectionService


class TestPhase4ProjectionContractSnapshot(unittest.TestCase):
    """
    Wave 5.7 Phase 4 Mandatory Invariant: Projection Contract Snapshot Test.
    Freezes and verifies the exact JSON schema shapes across all role projections
    to ensure future frontend integrations never suffer structural contract drift.
    """

    def setUp(self):
        self.tenant = MagicMock(id=uuid4())
        self.learner = MagicMock(
            id=uuid4(),
            tenant=self.tenant,
            student_code="STD-5501",
            display_name="سارا احمدی",
        )
        self.project = MagicMock(
            id=uuid4(),
            tenant=self.tenant,
            learner=self.learner,
            title="سامانه پایش آب و هوا",
            current_milestone="پیاده‌سازی Async Endpoint",
            recent_activity="رفع چالش با دیباگ",
            last_code_snippet="async def fetch(): pass",
            progress_percentage=85,
            commit_hash="c979ca9",
            skills_demonstrated=["python_basics", "error_handling"],
        )

    def test_student_projection_contract_snapshot_keys(self):
        """Student role projection must contain exact keys: skill_graph without competitive scores."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj:
            mock_proj.return_value = [self.project]
            projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant,
                user=MagicMock(),
                learner=self.learner,
                user_role=TenantMembership.Role.LEARNER,
            )

            self.assertIn("skill_graph", projection)
            sg = projection["skill_graph"]
            self.assertEqual(set(sg.keys()), {"learner_id", "student_code", "skills"})
            for s in sg["skills"]:
                self.assertEqual(set(s.keys()), {"slug", "title", "category", "status", "prerequisites"})
                self.assertNotIn("score", s)
                self.assertNotIn("rank", s)

    def test_mentor_projection_contract_snapshot_keys(self):
        """Mentor role projection must contain exact keys: skill_graph + mentor_dossier."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj:
            mock_qs = MagicMock()
            mock_qs.__iter__.return_value = [self.project]
            mock_qs.first.return_value = self.project
            mock_proj.return_value = mock_qs

            projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant,
                user=MagicMock(),
                learner=self.learner,
                user_role=TenantMembership.Role.MENTOR,
            )

            self.assertIn("mentor_dossier", projection)
            md = projection["mentor_dossier"]
            expected_keys = {
                "learner_id", "student_code", "display_name",
                "pedagogical_summary", "evidence_trace",
                "suggested_socratic_prompts", "friction_signal"
            }
            self.assertEqual(set(md.keys()), expected_keys)

    def test_guardian_projection_contract_snapshot_keys(self):
        """Guardian role projection must contain exact keys: parent_insight without tech traces."""
        with unittest.mock.patch("modules.learning_loop.models.ParentBridge.objects.filter") as mock_bridge, \
             unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj:

            mock_bridge.return_value.first.return_value = MagicMock(briefing_updated_at=MagicMock(isoformat=lambda: "2026-09-21T00:00:00Z"))
            mock_proj.return_value.first.return_value = self.project

            projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant,
                user=MagicMock(),
                learner=self.learner,
                user_role=TenantMembership.Role.GUARDIAN,
            )

            self.assertIn("parent_insight", projection)
            pi = projection["parent_insight"]
            expected_keys = {
                "learner_id", "developmental_translation",
                "home_support_cues", "technical_jargon_suppressed",
                "last_briefing_at"
            }
            self.assertEqual(set(pi.keys()), expected_keys)
            self.assertTrue(pi["technical_jargon_suppressed"])


if __name__ == "__main__":
    unittest.main()
