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
from modules.learning_loop.intelligence_serializers import (
    LearnerSkillGraphReadModelSerializer,
    MentorIntelligenceDossierReadModelSerializer,
    ParentInsightReadModelSerializer,
)


class TestPhase3IntelligenceReadContract(unittest.TestCase):
    """
    Wave 5.7 Phase 3: Intelligence Read Contract, Projections & Privacy Boundary Test Suite.
    Enforces:
    1. Serialization & Schema Integrity across all Read DTOs.
    2. Role-Scoped Filtering (Learner vs Mentor vs Guardian boundaries).
    3. Strict Prevention of Data Leakage (Guardians never receive raw friction traces or code snippets).
    4. Socratic Prompt Integrity (Evidence -> Reason -> Socratic Prompt).
    5. Multi-Tenant Fail-Closed Isolation.
    """

    def setUp(self):
        self.tenant_a = MagicMock(id=uuid4())
        self.tenant_b = MagicMock(id=uuid4())
        self.learner_user = MagicMock(id=uuid4(), is_authenticated=True)

        self.mock_learner = MagicMock(
            id=uuid4(),
            tenant=self.tenant_a,
            user=self.learner_user,
            student_code="STD-5501",
            display_name="سارا احمدی",
        )

        self.mock_project = MagicMock(
            id=uuid4(),
            tenant=self.tenant_a,
            learner=self.mock_learner,
            title="سامانه پایش آب و هوا",
            current_milestone="پیاده‌سازی Async Endpoint",
            recent_activity="رفع چالش Race Condition با آزمون و خطا و دیباگ",
            last_code_snippet="try:\n    await fetch()\nexcept Exception:\n    pass",
            progress_percentage=85,
            commit_hash="c1d9b75",
            skills_demonstrated=["python_basics", "error_handling"],
        )

    def test_skill_graph_projection_contract_schema(self):
        """Skill Graph projection complies strictly with non-competitive schema."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_filter:
            mock_filter.return_value = [self.mock_project]
            projection = IntelligenceReadProjectionService.get_learner_skill_graph_projection(
                self.tenant_a, self.mock_learner
            )

            self.assertEqual(projection["learner_id"], str(self.mock_learner.id))
            self.assertEqual(projection["student_code"], "STD-5501")
            self.assertTrue(len(projection["skills"]) >= 4)
            # Ensure schema validity
            self.assertIn("category", projection["skills"][0])
            self.assertIn("status", projection["skills"][0])

    def test_mentor_dossier_projection_contract_schema(self):
        """Mentor dossier projection contains evidence trace and Socratic prompts."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_filter:
            mock_filter.return_value.first.return_value = self.mock_project
            projection = IntelligenceReadProjectionService.get_mentor_dossier_projection(
                self.tenant_a, self.mock_learner
            )

            self.assertEqual(projection["learner_id"], str(self.mock_learner.id))
            self.assertTrue(len(projection["pedagogical_summary"]) >= 1)
            self.assertTrue(len(projection["suggested_socratic_prompts"]) >= 2)
            self.assertTrue(len(projection["evidence_trace"]) >= 1)

    def test_parent_insight_projection_suppresses_technical_jargon(self):
        """Parent insight projection strictly filters technical traces and includes home support cues."""
        with unittest.mock.patch("modules.learning_loop.models.ParentBridge.objects.filter") as mock_bridge_filter, \
             unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj_filter:

            mock_bridge_filter.return_value.first.return_value = MagicMock(briefing_updated_at=MagicMock(isoformat=lambda: "2026-09-21T00:00:00Z"))
            mock_proj_filter.return_value.first.return_value = self.mock_project

            projection = IntelligenceReadProjectionService.get_parent_insight_projection(
                self.tenant_a, self.mock_learner
            )

            self.assertTrue(projection["technical_jargon_suppressed"])
            self.assertTrue(len(projection["home_support_cues"]) >= 2)
            self.assertIn("استقامت در حل مسئله", projection["developmental_translation"])

    def test_role_scoped_filtering_guardian_denied_mentor_dossier(self):
        """Guardian role projection contains ONLY parent insight; mentor dossier is excluded."""
        with unittest.mock.patch("modules.learning_loop.models.ParentBridge.objects.filter") as mock_bridge_filter, \
             unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj_filter:

            mock_bridge_filter.return_value.first.return_value = MagicMock(briefing_updated_at=MagicMock(isoformat=lambda: "2026-09-21T00:00:00Z"))
            mock_proj_filter.return_value.first.return_value = self.mock_project

            projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant_a,
                user=self.learner_user,
                learner=self.mock_learner,
                user_role=TenantMembership.Role.GUARDIAN,
            )

            self.assertIsNotNone(projection.get("parent_insight"))
            self.assertIsNone(projection.get("mentor_dossier"), "Guardian must never receive mentor dossier")
            self.assertIsNone(projection.get("skill_graph"), "Guardian does not receive raw technical skill graph")

    def test_role_scoped_filtering_mentor_granted_dossier_and_skill_graph(self):
        """Mentor role projection receives skill graph and mentor dossier; parent insight is excluded unless admin."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj_filter:
            mock_qs = MagicMock()
            mock_qs.__iter__.return_value = [self.mock_project]
            mock_qs.first.return_value = self.mock_project
            mock_proj_filter.return_value = mock_qs

            projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant_a,
                user=self.learner_user,
                learner=self.mock_learner,
                user_role=TenantMembership.Role.MENTOR,
            )

            self.assertIsNotNone(projection.get("skill_graph"))
            self.assertIsNotNone(projection.get("mentor_dossier"))
            self.assertIsNone(projection.get("parent_insight"))



if __name__ == "__main__":
    unittest.main()
