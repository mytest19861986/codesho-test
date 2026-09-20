import os
import sys
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from django.test import RequestFactory
from modules.learning_loop.views import (
    learning_loop_state_view,
    update_intervention_status_view,
    add_intervention_feedback_view,
    update_parent_briefing_view,
    send_parent_encouragement_view,
)
from modules.platform_tenant.models import TenantMembership

class TestLearningLoopShadowAPIRoutes(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.tenant = MagicMock(id=uuid4())
        self.user = MagicMock(id=uuid4(), is_authenticated=True)

    def test_state_route_denies_unauthenticated_request(self):
        req = self.factory.get("/api/v1/learning-loop/state/")
        req.user = MagicMock(is_authenticated=False)
        req.tenant = None
        req.tenant_membership = None
        resp = learning_loop_state_view(req)
        # Should be forbidden/unauthorized by IsTenantMember
        self.assertEqual(resp.status_code, 403)

    def test_status_update_denies_non_mentor(self):
        req = self.factory.post(
            f"/api/v1/learning-loop/interventions/{uuid4()}/status/",
            {"status": "REVIEWING"},
            content_type="application/json"
        )
        req.user = self.user
        req.tenant = self.tenant
        # Learner trying to execute mentor action
        req.tenant_membership = MagicMock(is_active=True, role=TenantMembership.Role.LEARNER)
        resp = update_intervention_status_view(req, intervention_id=uuid4())
        self.assertEqual(resp.status_code, 403)

    def test_parent_encouragement_denies_non_guardian(self):
        req = self.factory.post(
            f"/api/v1/learning-loop/parent-bridge/{uuid4()}/encouragement/",
            {"message": "بسیار عالی"},
            content_type="application/json"
        )
        req.user = self.user
        req.tenant = self.tenant
        # Mentor trying to send parent praise ribbon
        req.tenant_membership = MagicMock(is_active=True, role=TenantMembership.Role.MENTOR)
        resp = send_parent_encouragement_view(req, learner_id=uuid4())
        self.assertEqual(resp.status_code, 403)

if __name__ == "__main__":
    unittest.main()
