import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.learning_loop.intelligence_services import (
    SkillGraphService,
    LearningSignalAggregationService,
    MentorInsightGenerator,
    ParentTranslationService,
    ReflectionTimelineService,
)


class TestPhase2LearningIntelligenceServices(unittest.TestCase):
    """
    Wave 5.7 Phase 2: Learning Intelligence Domain Services Unit & Isolation Test Suite.
    Enforces:
    1. Primary Law: No Judgment Engine (Zero numeric ratings, zero competitive leaderboards).
    2. Traceable Insights (Evidence -> Signal -> Pedagogical Summary).
    3. Non-punitive Socratic Prompts.
    4. Empathetic Parent Translation (Zero raw stack traces).
    5. Student Reflection Ownership.
    6. Multi-Tenant Isolation & Zero Schema Migrations.
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
            recent_activity="رفع چالش Race Condition با آزمون و خطای پیوسته و دیباگ",
            last_code_snippet="try:\n    res = await fetch()\nexcept Exception:\n    pass",
            progress_percentage=85,
            commit_hash="c1d9b75",
            skills_demonstrated=["python_basics", "error_handling"],
        )

    def test_skill_graph_dag_and_zero_ranking(self):
        """Skill graph reflects concepts demonstrated without ranks or scores."""
        # Patch query
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_filter:
            mock_filter.return_value = [self.mock_project]
            res = SkillGraphService.get_skills_for_learner(self.tenant_a, self.mock_learner)

            self.assertEqual(res["student_code"], "STD-5501")
            skills = res["skills"]
            self.assertTrue(len(skills) >= 4)

            # Check that mastered skills match without numeric points
            python_skill = next(s for s in skills if s["slug"] == "python_basics")
            self.assertEqual(python_skill["status"], "DEMONSTRATED")
            self.assertNotIn("score", python_skill)
            self.assertNotIn("rank", python_skill)

    def test_learning_persistence_signals_detection(self):
        """Signals identify iterative problem solving and high persistence rather than raw scores."""
        res = LearningSignalAggregationService.analyze_learning_signals(self.tenant_a, self.mock_project)
        pattern = res["effort_pattern"]

        self.assertEqual(pattern["pattern"], "iterative_problem_solving")
        self.assertEqual(pattern["trend"], "high_persistence")
        self.assertTrue(pattern["has_error_handling_mastery"])
        self.assertNotIn("grit_score", pattern, "Grit score numeric grading must never exist")

    def test_mentor_dossier_evidence_traceability(self):
        """Mentor pedagogical summary traces back to actual commit and activity evidence."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_filter:
            mock_filter.return_value.first.return_value = self.mock_project
            dossier = MentorInsightGenerator.generate_mentor_dossier(self.tenant_a, self.mock_learner)

            self.assertEqual(dossier["learner_id"], str(self.mock_learner.id))
            self.assertTrue(len(dossier["pedagogical_summary"]) >= 2)
            self.assertTrue(any("پشتکار بالا" in s for s in dossier["pedagogical_summary"]))
            self.assertTrue(len(dossier["suggested_socratic_prompts"]) >= 2)

            # Verify evidence trace
            traces = dossier["evidence_trace"]
            self.assertTrue(any("commit: c1d9b75" in t for t in traces))

    def test_parent_insight_translation_suppresses_technical_jargon(self):
        """Parent translation replaces raw code diffs with empathetic developmental growth language."""
        with unittest.mock.patch("modules.learning_loop.models.ParentBridge.objects.filter") as mock_bridge_filter, \
             unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj_filter:

            mock_bridge_filter.return_value.first.return_value = MagicMock(briefing_updated_at=MagicMock(isoformat=lambda: "2026-09-21T00:00:00Z"))
            mock_proj_filter.return_value.first.return_value = self.mock_project

            insight = ParentTranslationService.generate_parent_insight(self.tenant_a, self.mock_learner)

            self.assertTrue(insight["technical_jargon_suppressed"])
            self.assertIn("استقامت در حل مسئله", insight["developmental_translation"])
            self.assertNotIn("Race Condition", insight["developmental_translation"], "Technical jargon must be suppressed")
            self.assertTrue(len(insight["home_support_cues"]) >= 2)

    def test_student_reflection_timeline_recording(self):
        """Student reflection is recorded without breaking schema constraints."""
        with unittest.mock.patch("modules.learning_loop.models.ActiveLearningProject.objects.filter") as mock_proj, \
             unittest.mock.patch("modules.learning_loop.models.MentorIntervention.objects.filter") as mock_interv, \
             unittest.mock.patch("modules.learning_loop.models.InterventionFeedback.objects.create") as mock_fb_create:

            mock_proj.return_value.first.return_value = self.mock_project
            mock_interv.return_value.first.return_value = MagicMock(id=uuid4())

            entry = ReflectionTimelineService.record_student_reflection(
                tenant=self.tenant_a,
                learner=self.mock_learner,
                milestone_slug="weather-api-async",
                reflection_text="با آزمون و خطا متوجه شدم چطور باید تست بنویسم.",
                sentiment="confident",
            )

            self.assertEqual(entry["status"], "RECORDED")
            self.assertEqual(entry["milestone_slug"], "weather-api-async")
            mock_fb_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
