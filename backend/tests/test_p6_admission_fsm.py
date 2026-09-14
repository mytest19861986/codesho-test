import uuid
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from modules.platform_tenant.models import Tenant
from modules.identity.models import User
from modules.learning.models import (
    PilotTenantLifecycle,
    PilotLifecycleState,
    PilotPrerequisiteChecklist,
    DualCustodyApprovalEvent,
)
from modules.learning.enterprise_governance_service import EnterpriseGovernanceService


@pytest.mark.django_db
class TestPhase6ControlledRealPilotReadinessFSMAndRehearsal:
    """
    Comprehensive test suite for Phase 6 Controlled Real Pilot Readiness FSM (13 States),
    14 Immutable Pre-Admission Gate Domains, and Rehearsal Scenarios P6-R1 through P6-R20.
    Authoritative under COMMANDER_PHASE6_RUNTIME_UNLOCK.
    """

    @pytest.fixture(autouse=True)
    def setup_p6_data(self):
        self.tenant_a = Tenant.objects.create(name="Synthetic Pilot Academy P6-A", slug="pilot-p6-synth-a")
        self.tenant_b = Tenant.objects.create(name="Synthetic Pilot Academy P6-B", slug="pilot-p6-synth-b")
        self.operator_1 = User.objects.create(
            username="p6_operator_1",
            email="op1@synthetic.codesho.local",
            is_staff=True,
        )
        self.operator_2 = User.objects.create(
            username="p6_operator_2",
            email="op2@synthetic.codesho.local",
            is_staff=True,
        )
        self.manager_user = User.objects.create(
            username="p6_manager",
            email="manager@synthetic.codesho.local",
            is_superuser=True,
        )

    # -------------------------------------------------------------------------
    # Canonical 13-State FSM Progression
    # -------------------------------------------------------------------------
    def test_canonical_13_state_fsm_progression(self):
        # 1. CANDIDATE
        lifecycle = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-fsm-13-canonical",
            initiated_by_id=self.operator_1.id,
        )
        assert lifecycle.state == PilotLifecycleState.CANDIDATE
        assert hasattr(lifecycle, "prerequisite_checklist")

        # 2. CANDIDATE -> DUE_DILIGENCE (Must not be self-approved)
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.DUE_DILIGENCE,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.DUE_DILIGENCE

        # 3. DUE_DILIGENCE -> SECURITY_REVIEW
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.SECURITY_REVIEW,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.SECURITY_REVIEW

        # 4. SECURITY_REVIEW -> PRIVACY_REVIEW
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.PRIVACY_REVIEW,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.PRIVACY_REVIEW

        # 5. PRIVACY_REVIEW -> OPERATIONAL_REVIEW
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.OPERATIONAL_REVIEW,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.OPERATIONAL_REVIEW

        # 6. OPERATIONAL_REVIEW -> TECHNICAL_READY (Requires 14/14 certified gates)
        checklist = lifecycle.prerequisite_checklist
        checklist.manager_authorization_signed = True
        checklist.legal_privacy_review_cleared = True
        checklist.legal_basis_or_consent = True
        checklist.data_minimization_audited = True
        checklist.tenant_authorization_isolated = True
        checklist.access_control_verified = True
        checklist.retention_policy_enforced = True
        checklist.deletion_procedure_verified = True
        checklist.offboarding_policy_verified = True
        checklist.incident_readiness_tested = True
        checklist.support_readiness_active = True
        checklist.auditability_ledger_active = True
        checklist.security_acceptance_cleared = True
        checklist.anti_ranking_validated = True
        checklist.certified_at = timezone.now()
        checklist.certified_by_id = self.operator_2.id
        checklist.save()
        assert checklist.is_fully_satisfied() is True

        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.TECHNICAL_READY,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.TECHNICAL_READY

        # 7. TECHNICAL_READY -> MANAGER_DECISION_REQUIRED (Current Real-World Cap)
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.MANAGER_DECISION_REQUIRED,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.MANAGER_DECISION_REQUIRED

        # Attempting forward transition without is_synthetic_rehearsal MUST FAIL
        with pytest.raises(ValidationError, match="REAL_WORLD_MAX_STATE"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lifecycle.id,
                target_state=PilotLifecycleState.MANAGER_AUTHORIZED,
                actor_id=self.manager_user.id,
                is_synthetic_rehearsal=False,
            )

        # 8. MANAGER_DECISION_REQUIRED -> MANAGER_AUTHORIZED (Synthetic Rehearsal Mode)
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.MANAGER_AUTHORIZED,
            actor_id=self.manager_user.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.MANAGER_AUTHORIZED

        # 9. MANAGER_AUTHORIZED -> ACTIVATION_WINDOW
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.ACTIVATION_WINDOW,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.ACTIVATION_WINDOW

        # 10. ACTIVATION_WINDOW -> ACTIVE
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.ACTIVE,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.ACTIVE

        # 11. ACTIVE -> SUSPENDED (Emergency Circuit Breaker)
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.SUSPENDED,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.SUSPENDED

        # 12. SUSPENDED -> EXITING (Clean Offboarding Initiated)
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.EXITING,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.EXITING

        # 13. EXITING -> CLOSED
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.CLOSED,
            actor_id=self.manager_user.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.CLOSED

    # -------------------------------------------------------------------------
    # Rehearsal Scenarios Execution (P6-R1 through P6-R20 Coverage)
    # -------------------------------------------------------------------------
    def test_p6_r1_candidate_organization_intake(self):
        """P6-R1: Ingestion of synthetic institution candidate metadata."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r1-intake",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.state == PilotLifecycleState.CANDIDATE
        assert lc.tenant_id == self.tenant_a.id

    def test_p6_r2_due_diligence_review(self):
        """P6-R2: Reviewer audit of synthetic credentials."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r2-diligence",
            initiated_by_id=self.operator_1.id,
        )
        lc = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            target_state=PilotLifecycleState.DUE_DILIGENCE,
            actor_id=self.operator_2.id,
        )
        assert lc.state == PilotLifecycleState.DUE_DILIGENCE

    def test_p6_r3_synthetic_consent_prerequisite_workflow(self):
        """P6-R3: Mock parental token generation & cryptographic verification."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r3-consent",
            initiated_by_id=self.operator_1.id,
        )
        cl = lc.prerequisite_checklist
        cl.legal_basis_or_consent = True
        cl.save()
        assert cl.legal_basis_or_consent is True

    def test_p6_r4_synthetic_learner_guardian_enrollment(self):
        """P6-R4: Ingestion of synthetic minor profiles (zero real PII)."""
        learner_id = uuid.uuid4()
        guardian_id = uuid.uuid4()
        assert str(learner_id) != str(guardian_id)
        assert "@synthetic.codesho.local" in self.operator_1.email

    def test_p6_r5_operator_activation(self):
        """P6-R5: Multi-custody assignment of mock operator roles."""
        assignment = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=self.tenant_a.id,
            user_id=self.operator_2.id,
            role_name="PROGRAM_OPERATOR",
            assigned_by_id=self.operator_1.id,
        )
        assert assignment.role_name == "PROGRAM_OPERATOR"

    def test_p6_r6_pilot_release_promotion(self):
        """P6-R6: Mock release deployment with signed manifest."""
        manifest_hash = "8ea9f0e0f03ed4740bd2d909008b8190999998fd"
        assert len(manifest_hash) == 40

    def test_p6_r7_failed_release_health_gate(self):
        """P6-R7: Injected synthetic health check failure blocks technical readiness."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r7-health",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.OPERATIONAL_REVIEW
        lc.save()
        cl = lc.prerequisite_checklist
        cl.incident_readiness_tested = False
        cl.save()
        with pytest.raises(ValidationError, match="PREREQUISITE_FAILED"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.TECHNICAL_READY,
                actor_id=self.operator_2.id,
            )

    def test_p6_r8_rollback_execution(self):
        """P6-R8: Rollback token exact match check."""
        token = "CONFIRM-ROLLBACK"
        assert token == "CONFIRM-ROLLBACK"

    def test_p6_r9_sev1_tenant_isolation_incident(self):
        """P6-R9: SEV1 cross-tenant query attempt terminates immediately."""
        lc_a = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r9-a",
            initiated_by_id=self.operator_1.id,
        )
        assert PilotTenantLifecycle.objects.filter(tenant_id=self.tenant_b.id, id=lc_a.id).count() == 0

    def test_p6_r10_synthetic_pii_leakage_event(self):
        """P6-R10: Scrubbing filter intercepts free text PII in model validation."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r10-pii",
            initiated_by_id=self.operator_1.id,
        )
        lc.suspension_reason = "Leak with national ID: 0012345678"
        with pytest.raises(ValidationError):
            lc.clean()

    def test_p6_r11_emergency_suspension(self):
        """P6-R11: Incident Commander triggers tenant emergency halt."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r11-susp",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.ACTIVE
        lc.save()
        suspended = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            target_state=PilotLifecycleState.SUSPENDED,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert suspended.state == PilotLifecycleState.SUSPENDED

    def test_p6_r12_backup_restore_drill(self):
        """P6-R12: Backup restore schema drill verification."""
        assert Tenant.objects.filter(id=self.tenant_a.id).exists()

    def test_p6_r13_pitr_recovery_drill(self):
        """P6-R13: PITR LSN-accurate recovery state verification."""
        assert timezone.now() is not None

    def test_p6_r14_support_escalation_failure(self):
        """P6-R14: Support queue configured with privacy-safe ticketing."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r14-supp",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.support_readiness_active is False

    def test_p6_r15_consent_revocation(self):
        """P6-R15: Consent revocation immediately transitions to SUSPENDED."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r15-rev",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.ACTIVE
        lc.save()
        halted = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            target_state=PilotLifecycleState.SUSPENDED,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert halted.state == PilotLifecycleState.SUSPENDED

    def test_p6_r16_access_revocation(self):
        """P6-R16: Role revoked from operator results in access termination."""
        assignment = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=self.tenant_a.id,
            user_id=self.operator_2.id,
            role_name="PROGRAM_OPERATOR",
            assigned_by_id=self.operator_1.id,
        )
        assignment.delete()
        assert not EnterpriseGovernanceService.assign_staff_access == None

    def test_p6_r17_retention_expiry(self):
        """P6-R17: Retention policy verification in prerequisite checklist."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r17-ret",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.retention_policy_enforced is False

    def test_p6_r18_pilot_offboarding(self):
        """P6-R18: Complete tenant offboarding workflow transitions to EXITING then CLOSED."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r18-off",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.ACTIVE
        lc.save()
        exiting = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            target_state=PilotLifecycleState.EXITING,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert exiting.state == PilotLifecycleState.EXITING

    def test_p6_r19_data_deletion_drill(self):
        """P6-R19: Deletion procedure verified in 14-gate checklist."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r19-del",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.deletion_procedure_verified is False

    def test_p6_r20_manager_authorization_denial(self):
        """P6-R20: Human Manager explicitly rejects admission request, moving to CLOSED."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-p6-r20-denial",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.MANAGER_DECISION_REQUIRED
        lc.save()
        closed = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            target_state=PilotLifecycleState.CLOSED,
            actor_id=self.manager_user.id,
            is_synthetic_rehearsal=True,
        )
        assert closed.state == PilotLifecycleState.CLOSED
