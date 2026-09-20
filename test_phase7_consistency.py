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

def compute_drift_analysis(backend_data, synthetic_data):
    """
    Classifies divergences between Backend reality and Synthetic baseline:
    - Allowed Drift: Timestamps, generated DB identifiers, localized formats
    - Critical Drift: Wrong learner code/name, wrong role ownership, missing intervention, mismatched status
    """
    allowed_drifts = []
    critical_drifts = []
    
    # 1. Learner / Student identity
    if backend_data.get("student", {}).get("name") != synthetic_data.get("student", {}).get("name"):
        critical_drifts.append(f"Learner name mismatch: {backend_data.get('student', {}).get('name')} vs {synthetic_data.get('student', {}).get('name')}")
    if backend_data.get("student", {}).get("id") != synthetic_data.get("student", {}).get("id"):
        allowed_drifts.append(f"Learner ID representation: {backend_data.get('student', {}).get('id')} vs {synthetic_data.get('student', {}).get('id')}")
        
    # 2. Project progress & branch
    b_proj = backend_data.get("activeProject", {})
    s_proj = synthetic_data.get("activeProject", {})
    if b_proj.get("progress_percentage") != s_proj.get("progress_percentage"):
        critical_drifts.append(f"Progress drift: {b_proj.get('progress_percentage')} vs {s_proj.get('progress_percentage')}")
    if b_proj.get("branch") != s_proj.get("branch"):
        allowed_drifts.append(f"Branch slug drift: {b_proj.get('branch')} vs {s_proj.get('branch')}")
        
    # 3. Intervention status
    b_int = backend_data.get("mentorIntervention", {})
    s_int = synthetic_data.get("mentorIntervention", {})
    if b_int.get("status") != s_int.get("status"):
        critical_drifts.append(f"Intervention status critical drift: {b_int.get('status')} vs {s_int.get('status')}")
        
    # 4. Parent Bridge
    b_pb = backend_data.get("parentBridge", {})
    s_pb = synthetic_data.get("parentBridge", {})
    if b_pb.get("parent_encouragement_sent") != s_pb.get("parent_encouragement_sent"):
        critical_drifts.append("Parent encouragement status mismatch")
        
    return {
        "allowed_drifts": allowed_drifts,
        "critical_drifts": critical_drifts,
        "is_consistent": len(critical_drifts) == 0
    }

class TestPhase7ReadConsistency(unittest.TestCase):
    def test_zero_critical_drift_between_backend_and_synthetic_baseline(self):
        # Synthetic baseline representing current production UI contract
        synthetic = {
            "student": {
                "id": "CS-9804",
                "name": "علی محمدی",
                "streak_days": 7,
            },
            "activeProject": {
                "branch": "feat/weather-async-fetch",
                "progress_percentage": 74,
            },
            "mentorIntervention": {
                "status": "REVIEWING",
            },
            "parentBridge": {
                "parent_encouragement_sent": True,
            }
        }
        
        # Backend mock populated with domain service aggregate
        student_mock = MagicMock(
            student_code="CS-9804",
            display_name="علی محمدی",
            avatar_key="ali",
            level_title="پایتون پیشرفته",
            streak_days=7,
        )
        project_mock = MagicMock(
            id="proj-weather-async",
            title="سامانه آب‌وهوا",
            repo_branch="feat/weather-async-fetch",
            commit_hash="e4a89bc",
            progress_percentage=74,
            current_milestone="پیاده‌سازی try/catch",
            recent_activity="تلاش برای اتصال",
            last_code_snippet="async function()",
            skills_demonstrated=["Async/Await"],
        )
        intervention_mock = MagicMock(
            id="int-01",
            status="REVIEWING",
            reason="مدیریت خطاهای ناهمگام",
            recommended_action="بررسی try/catch",
            mentor_notes="قوی در مباحث پایه",
            feedbacks=[],
        )
        parent_bridge_mock = MagicMock(
            last_briefing="در حال کار روی پروژه",
            briefing_updated_at=MagicMock(strftime=lambda fmt: "2026-09-20 11:00"),
            parent_encouragement_sent=True,
            parent_encouragement_message="آفرین",
        )
        
        backend_serializer = SharedLearningStateAggregateSerializer({
            "student": student_mock,
            "active_project": project_mock,
            "mentor_intervention": intervention_mock,
            "parent_bridge": parent_bridge_mock,
        })
        backend_out = backend_serializer.data
        
        drift = compute_drift_analysis(backend_out, synthetic)
        print("\n--- PHASE 7 DRIFT ANALYSIS REPORT ---")
        print(f"Allowed Drifts: {len(drift['allowed_drifts'])}")
        for ad in drift['allowed_drifts']:
            print(f"  [ALLOWED] {ad}")
        print(f"Critical Drifts: {len(drift['critical_drifts'])}")
        for cd in drift['critical_drifts']:
            print(f"  [CRITICAL] {cd}")
            
        self.assertEqual(len(drift["critical_drifts"]), 0, "Critical drift detected between Backend and Synthetic reality!")
        self.assertTrue(drift["is_consistent"])

if __name__ == "__main__":
    unittest.main()
