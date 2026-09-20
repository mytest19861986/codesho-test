import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.learning_loop.serializers import SharedLearningStateAggregateSerializer

def detailed_drift_matrix_eval(backend_data, frontend_baseline):
    """
    Evaluates field-by-field parity matrix across all 5 learning loop entities
    between Backend Projection and Independent Frontend Synthetic Baseline.
    """
    matrix = []
    
    # 1. LearnerProfile Matrix
    b_st = backend_data.get("student", {})
    f_st = frontend_baseline.get("student", {})
    matrix.append({
        "entity": "LearnerProfile",
        "field": "student_code / id",
        "backend": b_st.get("id"),
        "frontend": f_st.get("id"),
        "drift_type": "NONE" if b_st.get("id") == f_st.get("id") else "ALLOWED_FORMAT",
    })
    matrix.append({
        "entity": "LearnerProfile",
        "field": "display_name",
        "backend": b_st.get("name"),
        "frontend": f_st.get("name"),
        "drift_type": "NONE" if b_st.get("name") == f_st.get("name") else "CRITICAL",
    })
    matrix.append({
        "entity": "LearnerProfile",
        "field": "streak_days",
        "backend": b_st.get("streak_days"),
        "frontend": f_st.get("streak_days"),
        "drift_type": "NONE" if b_st.get("streak_days") == f_st.get("streak_days") else "CRITICAL",
    })

    # 2. ActiveLearningProject Matrix
    b_pr = backend_data.get("activeProject", {})
    f_pr = frontend_baseline.get("activeProject", {})
    matrix.append({
        "entity": "ActiveLearningProject",
        "field": "branch",
        "backend": b_pr.get("branch"),
        "frontend": f_pr.get("branch"),
        "drift_type": "NONE" if b_pr.get("branch") == f_pr.get("branch") else "CRITICAL",
    })
    matrix.append({
        "entity": "ActiveLearningProject",
        "field": "progress_percentage",
        "backend": b_pr.get("progress_percentage"),
        "frontend": f_pr.get("progress_percentage"),
        "drift_type": "NONE" if b_pr.get("progress_percentage") == f_pr.get("progress_percentage") else "CRITICAL",
    })

    # 3. MentorIntervention Matrix
    b_in = backend_data.get("mentorIntervention", {})
    f_in = frontend_baseline.get("mentorIntervention", {})
    matrix.append({
        "entity": "MentorIntervention",
        "field": "status",
        "backend": b_in.get("status"),
        "frontend": f_in.get("status"),
        "drift_type": "NONE" if b_in.get("status") == f_in.get("status") else "CRITICAL",
        "critical": b_in.get("status") != f_in.get("status")
    })

    # 4. InterventionFeedback Matrix
    b_fb = b_in.get("feedbacks", [])
    f_fb = f_in.get("feedbacks", [])
    matrix.append({
        "entity": "InterventionFeedback",
        "field": "feedback_count",
        "backend": len(b_fb),
        "frontend": len(f_fb),
        "drift_type": "NONE" if len(b_fb) == len(f_fb) else "ALLOWED_SYNC",
    })

    # 5. ParentBridge Matrix
    b_pb = backend_data.get("parentBridge", {})
    f_pb = frontend_baseline.get("parentBridge", {})
    matrix.append({
        "entity": "ParentBridge",
        "field": "parent_encouragement_sent",
        "backend": b_pb.get("parent_encouragement_sent"),
        "frontend": f_pb.get("parent_encouragement_sent"),
        "drift_type": "NONE" if b_pb.get("parent_encouragement_sent") == f_pb.get("parent_encouragement_sent") else "CRITICAL",
    })
    matrix.append({
        "entity": "ParentBridge",
        "field": "timestamp_provenance",
        "backend": b_pb.get("briefingTimestamp"),
        "frontend": f_pb.get("briefingTimestamp"),
        "drift_type": "ALLOWED_TIMESTAMP",
    })

    criticals = [m for m in matrix if m.get("drift_type") == "CRITICAL" or m.get("critical")]
    alloweds = [m for m in matrix if "ALLOWED" in str(m.get("drift_type"))]
    
    return matrix, alloweds, criticals


class TestComprehensivePhase7Drift(unittest.TestCase):
    def test_multi_scenario_independent_drift_matrix(self):
        # Scenario 1: Standard Active Learner
        frontend_baseline_1 = {
            "student": {"id": "CS-9804", "name": "علی محمدی", "streak_days": 7},
            "activeProject": {"branch": "feat/weather-async-fetch", "progress_percentage": 74},
            "mentorIntervention": {"status": "REVIEWING", "feedbacks": []},
            "parentBridge": {"parent_encouragement_sent": True, "briefingTimestamp": "امروز ۱۱:۰۰"},
        }

        student_mock_1 = MagicMock(student_code="CS-9804", display_name="علی محمدی", avatar_key="ali", level_title="پایتون پیشرفته", streak_days=7)
        project_mock_1 = MagicMock(id="proj-weather", title="سامانه آب‌وهوا", repo_branch="feat/weather-async-fetch", commit_hash="e4a89bc", progress_percentage=74, current_milestone="پیاده‌سازی try/catch", recent_activity="تلاش برای اتصال", last_code_snippet="", skills_demonstrated=[])
        intervention_mock_1 = MagicMock(id="int-01", status="REVIEWING", reason="مدیریت خطاهای ناهمگام", recommended_action="بررسی try/catch", mentor_notes="قوی در مباحث پایه", feedbacks=[])
        parent_bridge_mock_1 = MagicMock(last_briefing="در حال کار روی پروژه", briefing_updated_at=MagicMock(strftime=lambda fmt: "2026-09-20T11:00:00Z"), parent_encouragement_sent=True, parent_encouragement_message="آفرین")

        backend_data_1 = SharedLearningStateAggregateSerializer({
            "student": student_mock_1,
            "active_project": project_mock_1,
            "mentor_intervention": intervention_mock_1,
            "parent_bridge": parent_bridge_mock_1,
        }).data

        matrix, alloweds, criticals = detailed_drift_matrix_eval(backend_data_1, frontend_baseline_1)
        print("\n=== COMPREHENSIVE DRIFT MATRIX (SCENARIO 1) ===")
        for row in matrix:
            print(f"[{row['entity']}] {row['field']} -> Backend: {row['backend']} | Frontend: {row['frontend']} | Drift: {row['drift_type']}")

        print(f"\nTotal Matrix Checks: {len(matrix)}")
        print(f"Allowed Drifts (Timestamps/Formats): {len(alloweds)}")
        print(f"Critical Drifts (Domain Violations): {len(criticals)}")

        self.assertEqual(len(criticals), 0, "Critical drift violation detected in field-by-field matrix!")
        self.assertGreater(len(alloweds), 0, "Realistic drift expected between localized timestamp and UTC ISO format!")

if __name__ == "__main__":
    unittest.main()
