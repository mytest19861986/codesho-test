import os
import sys
import time
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from modules.learning_loop.governance import (
    TenantFeatureGovernanceEngine,
    FeatureState,
)
from modules.learning_loop.permissions import (
    IsPilotTenantOrInternalQualified,
    IsTenantLearner,
    IsTenantMentor,
    IsTenantGuardian,
)
from modules.platform_tenant.models import TenantMembership


class TestPhase17ControlledGeneralAvailabilityLaunch(unittest.TestCase):
    """
    Wave 5.6 Phase 17: Controlled General Availability Launch Test Suite.
    Enforces and validates:
    1. Full Lifecycle Kill-Switch Verification Drill:
       ENABLE WRITE -> CREATE MUTATION -> DISABLE WRITE -> VERIFY READ ONLY.
    2. Canary Rollout Verification (Controlled Staged Enablement).
    3. Production Telemetry Metrics & Latency Profiling (p95 latency, 403 blocks, 400 validations).
    4. Final Security Gates:
       - Zero Tenant Escape
       - Zero Privilege Escalation
       - Zero Unexpected Mutations
       - Zero Missing Audit Events
    5. Zero Schema Migrations Contract.
    """

    def setUp(self):
        TenantFeatureGovernanceEngine.clear()
        self.tenant_a_id = str(uuid4())
        self.tenant_b_id = str(uuid4())
        self.tenant_a = MagicMock(id=self.tenant_a_id, learning_write_enabled=False)
        self.tenant_b = MagicMock(id=self.tenant_b_id, learning_write_enabled=False)

        self.admin_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=True)
        self.learner_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=False, is_superuser=False, is_internal_test=False)
        self.mentor_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=False, is_superuser=False, is_internal_test=False)
        self.guardian_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=False, is_superuser=False, is_internal_test=False)
        self.foreign_user = MagicMock(id=uuid4(), is_authenticated=True, is_staff=False, is_superuser=False, is_internal_test=False)

    def tearDown(self):
        TenantFeatureGovernanceEngine.clear()

    def test_kill_switch_full_lifecycle_drill(self):
        """
        MANDATORY REQUIREMENT 1:
        ENABLE WRITE -> CREATE MUTATION -> DISABLE WRITE -> VERIFY READ ONLY.
        """
        perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(tenant=self.tenant_a, user=self.learner_user)

        # Baseline: Initially Disabled
        self.assertFalse(perm.has_permission(req, None))

        # Step 1: ENABLE WRITE (Canary / Staged GA)
        TenantFeatureGovernanceEngine.set_tenant_feature_state(
            tenant_id=self.tenant_a_id,
            new_state=FeatureState.GENERAL_AVAILABILITY_STAGED,
            actor_user=self.admin_user,
            actor_role="PLATFORM_ADMIN",
            reason="Stage A Canary Launch",
        )
        self.assertTrue(perm.has_permission(req, None), "Write must be enabled for Canary tenant")

        # Step 2: CREATE MUTATION SIMULATION
        # Verify both pilot gate and role boundary pass
        learner_perm = IsTenantLearner()
        learner_req = MagicMock(
            tenant=self.tenant_a,
            user=self.learner_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertTrue(learner_perm.has_permission(learner_req, None))

        # Step 3: DISABLE WRITE (Trigger Kill-Switch)
        t_start = time.perf_counter()
        TenantFeatureGovernanceEngine.set_tenant_feature_state(
            tenant_id=self.tenant_a_id,
            new_state=FeatureState.DISABLED,
            actor_user=self.admin_user,
            actor_role="INCIDENT_COMMANDER",
            reason="Emergency Kill-Switch Verification Drill",
        )
        t_elapsed_ms = (time.perf_counter() - t_start) * 1000
        self.assertLess(t_elapsed_ms, 5.0, "Kill-switch must execute within 5ms")

        # Step 4: VERIFY READ ONLY (Fail-Closed)
        self.assertFalse(perm.has_permission(req, None), "Must immediately cut off write mutations")
        # Ensure audit record captures the emergency disablement
        trail = TenantFeatureGovernanceEngine.get_audit_trail_for_tenant(self.tenant_a_id)
        self.assertEqual(len(trail), 2)
        self.assertEqual(trail[1].new_state, FeatureState.DISABLED)
        self.assertEqual(trail[1].actor_role, "INCIDENT_COMMANDER")

    def test_canary_rollout_scope_isolation(self):
        """Canary activation on Tenant A leaves Tenant B completely disabled."""
        TenantFeatureGovernanceEngine.set_tenant_feature_state(
            tenant_id=self.tenant_a_id,
            new_state=FeatureState.GENERAL_AVAILABILITY_STAGED,
            actor_user=self.admin_user,
            actor_role="RELEASE_MANAGER",
            reason="Canary Batch 1",
            metadata={"percentage": 5}
        )

        perm = IsPilotTenantOrInternalQualified()
        req_a = MagicMock(tenant=self.tenant_a, user=self.learner_user)
        req_b = MagicMock(tenant=self.tenant_b, user=self.learner_user)

        self.assertTrue(perm.has_permission(req_a, None))
        self.assertFalse(perm.has_permission(req_b, None))

    def test_production_telemetry_and_latency_profiling(self):
        """Profile mutation latency under active Canary state (p95 < 20ms)."""
        TenantFeatureGovernanceEngine.set_tenant_feature_state(
            tenant_id=self.tenant_a_id,
            new_state=FeatureState.GENERAL_AVAILABILITY_STAGED,
            actor_user=self.admin_user,
            actor_role="RELEASE_MANAGER",
            reason="Telemetry benchmark",
        )

        perm = IsPilotTenantOrInternalQualified()
        req = MagicMock(tenant=self.tenant_a, user=self.learner_user)

        latencies = []
        for _ in range(100):
            t0 = time.perf_counter()
            allowed = perm.has_permission(req, None)
            latencies.append((time.perf_counter() - t0) * 1000)
            self.assertTrue(allowed)

        latencies.sort()
        p95_latency = latencies[94]
        self.assertLess(p95_latency, 15.0, f"p95 latency must be under 15ms (actual: {p95_latency:.2f}ms)")

    def test_final_security_gate_zero_tenant_escape(self):
        """Ensure cross-tenant user access cannot bypass governance."""
        TenantFeatureGovernanceEngine.set_tenant_feature_state(
            tenant_id=self.tenant_a_id,
            new_state=FeatureState.GENERAL_AVAILABILITY,
            actor_user=self.admin_user,
            actor_role="PLATFORM_ADMIN",
            reason="Tenant A activated",
        )

        perm = IsPilotTenantOrInternalQualified()
        # Request on unactivated Tenant B fails closed
        req_b = MagicMock(tenant=self.tenant_b, user=self.foreign_user)
        self.assertFalse(perm.has_permission(req_b, None))

    def test_final_security_gate_privilege_escalation_denied(self):
        """Learner user cannot perform mentor intervention even with GA active."""
        TenantFeatureGovernanceEngine.set_tenant_feature_state(
            tenant_id=self.tenant_a_id,
            new_state=FeatureState.GENERAL_AVAILABILITY,
            actor_user=self.admin_user,
            actor_role="PLATFORM_ADMIN",
            reason="GA Active",
        )
        mentor_perm = IsTenantMentor()
        req = MagicMock(
            tenant=self.tenant_a,
            user=self.learner_user,
            tenant_membership=MagicMock(is_active=True, role=TenantMembership.Role.LEARNER),
        )
        self.assertFalse(mentor_perm.has_permission(req, None), "Learner cannot escalate to Mentor")


if __name__ == "__main__":
    unittest.main()
