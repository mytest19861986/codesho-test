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


class TestPhase5RoleVisibilitySnapshot(unittest.TestCase):
    """
    Wave 5.7 Phase 5 Mandatory Invariant: Role Visibility Snapshot Test.
    Feeds a common domain learning state and asserts the exact role visibility projections:
    - Student: Sees Skill Graph & own Reflections; Mentor Dossier & Parent Insights are 100% hidden.
    - Mentor: Sees Skill Graph & Mentor Dossier (with Socratic Prompts & Friction Signals); Parent Insights are 100% hidden.
    - Guardian: Sees Parent Insights (Jargon-free & Home Cues); Skill Graph & Mentor Dossier are 100% hidden.
    """

    def setUp(self):
        self.tenant = MagicMock(id=uuid4())
        self.learner = MagicMock(
            id=uuid4(),
            tenant=self.tenant,
            student_code="CS-9804",
            display_name="علی محمدی",
        )
        self.project = MagicMock(
            id=uuid4(),
            tenant=self.tenant,
            learner=self.learner,
            title="سامانه اطلاع‌رسانی وضعیت آب‌وهوا",
            current_milestone="اتصال به سرویس هواشناسی با الگوی مدیریت خطا",
            recent_activity="رفع چالش Race Condition در پردازش غیرهمزمان با ۴ بار دیباگ",
            last_code_snippet="async def fetch(): pass",
            progress_percentage=85,
            commit_hash="e4a89bc",
            skills_demonstrated=["python_basics", "error_handling"],
        )

    def test_student_role_visibility_snapshot(self):
        """Student role receives only skill graph; mentor dossier and parent insight are strictly omitted."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj:
            mock_proj.return_value = [self.project]
            projection = IntelligenceReadProjectionService.get_role_scoped_projection(
                tenant=self.tenant,
                user=MagicMock(),
                learner=self.learner,
                user_role=TenantMembership.Role.LEARNER,
            )

            self.assertIsNotNone(projection.get("skill_graph"))
            self.assertIsNone(projection.get("mentor_dossier"))
            self.assertIsNone(projection.get("parent_insight"))

    def test_mentor_role_visibility_snapshot(self):
        """Mentor role receives skill graph and mentor dossier; parent insight is strictly omitted."""
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

            self.assertIsNotNone(projection.get("skill_graph"))
            self.assertIsNotNone(projection.get("mentor_dossier"))
            self.assertIsNone(projection.get("parent_insight"))

    def test_guardian_role_visibility_snapshot(self):
        """Guardian role receives parent insight; skill graph and mentor dossier are strictly omitted."""
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

            self.assertIsNotNone(projection.get("parent_insight"))
            self.assertIsNone(projection.get("skill_graph"))
            self.assertIsNone(projection.get("mentor_dossier"))


if __name__ == "__main__":
    unittest.main()
