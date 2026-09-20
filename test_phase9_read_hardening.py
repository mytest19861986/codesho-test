import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.learning_loop.serializers import SharedLearningStateAggregateSerializer
from modules.learning_loop.permissions import IsTenantMember, IsTenantMentor, IsTenantGuardian
from modules.platform_tenant.models import TenantMembership

class TestPhase9ReadHardening(unittest.TestCase):
    """
    Wave 5.6 Phase 9: Controlled Read Stage 2 — Production Readiness Hardening
    Validates diverse scenarios, edge cases, observability invariants, and security boundaries.
    """

    def setUp(self):
        self.base_student = MagicMock(
            student_code="CS-9804",
            display_name="علی محمدی",
            avatar_key="ali",
            level_title="پایتون پیشرفته",
            streak_days=7,
        )

    def test_scenario_1_learner_with_no_active_project(self):
        """Edge Case 1: Learner enrolled but has not started any active project."""
        data = {
            "student": self.base_student,
            "active_project": None,
            "mentor_intervention": None,
            "parent_bridge": None,
        }
        serializer = SharedLearningStateAggregateSerializer(data)
        out = serializer.data
        self.assertEqual(out["student"]["id"], "CS-9804")
        self.assertIsNone(out["activeProject"])
        self.assertIsNone(out["mentorIntervention"])
        self.assertIsNone(out["parentBridge"])

    def test_scenario_2_learner_with_no_mentor_intervention(self):
        """Edge Case 2: Learner has active project progressing smoothly without mentor intervention."""
        project = MagicMock(
            id="proj-ai-intro",
            title="مقدمه‌ای بر هوش مصنوعی",
            repo_branch="main",
            commit_hash="c0ffee1",
            progress_percentage=45,
            current_milestone="تنظیم محیط توسعه پایتون",
            recent_activity="اجرای موفق اولین اسکریپت",
            last_code_snippet="print('Hello AI')",
            skills_demonstrated=["Python", "CLI"],
        )
        data = {
            "student": self.base_student,
            "active_project": project,
            "mentor_intervention": None,
            "parent_bridge": None,
        }
        serializer = SharedLearningStateAggregateSerializer(data)
        out = serializer.data
        self.assertEqual(out["activeProject"]["id"], "proj-ai-intro")
        self.assertIsNone(out["mentorIntervention"])

    def test_scenario_3_learner_with_multiple_feedbacks(self):
        """Edge Case 3: Learner and mentor have a rich dialogue with multiple feedback items."""
        fb1 = MagicMock(
            id=1,
            sender_role="MENTOR",
            created_at=MagicMock(strftime=lambda fmt: "2026-09-20 10:00"),
            feedback_text="بررسی ساختار کلاس پیشنهاد می‌شود.",
            action_type="HINT",
        )
        fb2 = MagicMock(
            id=2,
            sender_role="STUDENT",
            created_at=MagicMock(strftime=lambda fmt: "2026-09-20 10:15"),
            feedback_text="کلاس پایه بازنویسی شد و متد __init__ اصلاح شد.",
            action_type="REVISION",
        )
        intervention = MagicMock(
            id="int-dialogue-01",
            status="FOLLOW_UP",
            reason="نیاز به راهنمایی در ارث‌بری چندگانه",
            recommended_action="مطالعه مستندات MRO",
            mentor_notes="پیشرفت بسیار خوب بوده است.",
            feedbacks=[fb1, fb2],
        )
        data = {
            "student": self.base_student,
            "active_project": None,
            "mentor_intervention": intervention,
            "parent_bridge": None,
        }
        serializer = SharedLearningStateAggregateSerializer(data)
        out = serializer.data
        feedbacks = out["mentorIntervention"]["feedbacks"]
        self.assertEqual(len(feedbacks), 2)
        self.assertEqual(feedbacks[0]["sender"], "MENTOR")
        self.assertEqual(feedbacks[1]["sender"], "STUDENT")
        self.assertEqual(feedbacks[1]["action_type"], "REVISION")

    def test_scenario_4_parent_without_bridge_or_encouragement(self):
        """Edge Case 4: Parent bridge exists without initial briefing or praise ribbon sent."""
        parent_bridge = MagicMock(
            last_briefing="",
            briefing_updated_at=MagicMock(strftime=lambda fmt: "2026-09-20 08:00"),
            parent_encouragement_sent=False,
            parent_encouragement_message="",
        )
        data = {
            "student": self.base_student,
            "active_project": None,
            "mentor_intervention": None,
            "parent_bridge": parent_bridge,
        }
        serializer = SharedLearningStateAggregateSerializer(data)
        out = serializer.data
        self.assertFalse(out["parentBridge"]["parent_encouragement_sent"])
        self.assertEqual(out["parentBridge"]["parent_encouragement_message"], "")

    def test_scenario_5_mentor_empty_queue_representation(self):
        """Edge Case 5: Resolved mentor intervention leaves queue in clear state."""
        intervention = MagicMock(
            id="int-resolved-01",
            status="RESOLVED",
            reason="ابهام در حلقه‌ها برطرف شد",
            recommended_action="شروع پروژه بعدی",
            mentor_notes="پروژه با موفقیت تحویل شد.",
            feedbacks=[],
        )
        data = {
            "student": self.base_student,
            "active_project": None,
            "mentor_intervention": intervention,
            "parent_bridge": None,
        }
        serializer = SharedLearningStateAggregateSerializer(data)
        out = serializer.data
        self.assertEqual(out["mentorIntervention"]["status"], "RESOLVED")

    def test_security_deep_review_role_escalation_fails_closed(self):
        """Security: Learner role strictly cannot access mentor review mutation endpoints."""
        perm = IsTenantMentor()
        learner_request = MagicMock(
            tenant=MagicMock(id=uuid4()),
            user=MagicMock(is_authenticated=True),
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertFalse(perm.has_permission(learner_request, None))

    def test_security_deep_review_tenant_leakage_prevented(self):
        """Security: Context without valid tenant fails closed."""
        perm = IsTenantMember()
        orphan_request = MagicMock(tenant=None, user=MagicMock(is_authenticated=True))
        self.assertFalse(perm.has_permission(orphan_request, None))

if __name__ == "__main__":
    unittest.main()
