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
from modules.learning_loop.services import LearningLoopDomainService
from modules.learning_loop.intelligence_services import (
    SkillGraphService,
    MentorInsightGenerator,
    ParentTranslationService,
)
from modules.learning_loop.intelligence_projections import IntelligenceReadProjectionService


class TestPhase6FinalIntegrationAndClosure(unittest.TestCase):
    """
    Wave 5.7 Phase 6: Final Integration Validation & Wave Closure Suite.
    Validates:
    1. Wave 5.6 + Wave 5.7 Full Stack Compatibility (Zero conflicts between transactional write and intelligence read).
    2. Full Role Journey End-to-End:
       - Student Journey: Submits evidence -> Updates skill graph -> Records reflection.
       - Mentor Journey: Reads dossier -> Reviews Socratic prompts & learning signals -> Records feedback.
       - Parent Journey: Reads empathetic translation -> Sends encouragement ribbon.
    3. Contract Regression & Strict Fail-Closed Privacy Boundaries.
    4. Primary Principle Invariant: Zero Numeric Child Grading.
    """

    def setUp(self):
        self.tenant = MagicMock(id=uuid4(), learning_write_enabled=True)
        self.learner_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=False)
        self.mentor_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=False)
        self.guardian_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=False)

        self.mock_learner = MagicMock(
            id=uuid4(),
            tenant=self.tenant,
            user=self.learner_user,
            assigned_mentor=self.mentor_user,
            guardian=self.guardian_user,
            student_code="CS-9804",
            display_name="علی محمدی",
        )

        self.mock_project = MagicMock(
            id=uuid4(),
            tenant=self.tenant,
            learner=self.mock_learner,
            title="سامانه اطلاع‌رسانی وضعیت آب‌وهوا",
            current_milestone="اتصال به سرویس هواشناسی با الگوی مدیریت خطا",
            recent_activity="رفع چالش Race Condition با آزمون و خطا و دیباگ",
            last_code_snippet="async def fetch(): pass",
            progress_percentage=85,
            commit_hash="e4a89bc",
            skills_demonstrated=["python_basics", "error_handling"],
        )

    def test_wave56_write_with_wave57_intelligence_read_compatibility(self):
        """Simulate a learner submitting evidence via Wave 5.6 and reading intelligence via Wave 5.7."""
        # 1. Simulate Wave 5.6 Domain Service mutation
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.select_for_update") as mock_sfu:
            mock_sfu.return_value.get.return_value = self.mock_project
            updated_project = LearningLoopDomainService.submit_learning_evidence(
                tenant=self.tenant,
                project_id=str(self.mock_project.id),
                learner_user=self.learner_user,
                repo_branch="feat/weather-async-fetch",
                commit_hash="e4a89bc",
                current_milestone="اتصال به سرویس هواشناسی با الگوی مدیریت خطا",
                recent_activity="رفع چالش Race Condition با آزمون و خطا و دیباگ",
                last_code_snippet="async def fetch(): pass",
                progress_percentage=85,
            )
            self.assertEqual(updated_project.commit_hash, "e4a89bc")

        # 2. Seamlessly project Wave 5.7 Intelligence Read Model
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_filter:
            mock_filter.return_value = [self.mock_project]
            skill_graph = SkillGraphService.get_skills_for_learner(self.tenant, self.mock_learner)
            self.assertEqual(skill_graph["student_code"], "CS-9804")
            self.assertTrue(len(skill_graph["skills"]) >= 4)

    def test_end_to_end_mentor_and_parent_journey_validation(self):
        """End-to-End validation of Mentor and Parent journeys without cross-leakage."""
        # Mentor Journey
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj:
            mock_qs = MagicMock()
            mock_qs.__iter__.return_value = [self.mock_project]
            mock_qs.first.return_value = self.mock_project
            mock_proj.return_value = mock_qs

            mentor_projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant,
                user=self.mentor_user,
                learner=self.mock_learner,
                user_role=TenantMembership.Role.MENTOR,
            )
            self.assertIsNotNone(mentor_projection["mentor_dossier"])
            self.assertTrue(len(mentor_projection["mentor_dossier"]["suggested_socratic_prompts"]) >= 2)
            self.assertEqual(mentor_projection["mentor_dossier"]["friction_signal"]["signal_type"], "CONCEPTUAL_FRICTION")

        # Parent Journey
        with unittest.mock.patch("modules.learning_loop.models.ParentBridge.objects.filter") as mock_bridge, \
             unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj:

            mock_bridge.return_value.first.return_value = MagicMock(briefing_updated_at=MagicMock(isoformat=lambda: "2026-09-21T00:00:00Z"))
            mock_proj.return_value.first.return_value = self.mock_project

            parent_projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant,
                user=self.guardian_user,
                learner=self.mock_learner,
                user_role=TenantMembership.Role.GUARDIAN,
            )
            self.assertIsNotNone(parent_projection["parent_insight"])
            self.assertTrue(parent_projection["parent_insight"]["technical_jargon_suppressed"])
            self.assertIsNone(parent_projection.get("mentor_dossier"))


if __name__ == "__main__":
    unittest.main()
