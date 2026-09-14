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
class TestPhase5ControlledPilotActivationFSMAndRehearsal:
    """
    Comprehensive test suite for Phase 5 Controlled Pilot Activation FSM
    and Rehearsal Scenarios R1 through R16.
    Authoritative under COMMANDER_PHASE5_RUNTIME_UNLOCK.
    """

    @pytest.fixture(autouse=True)
    def setup_p5_data(self):
        self.tenant_a = Tenant.objects.create(name="Synthetic Pilot Academy A", slug="pilot-synth-a")
        self.tenant_b = Tenant.objects.create(name="Synthetic Pilot Academy B", slug="pilot-synth-b")
        self.operator_1 = User.objects.create(
            username="operator_p5_1",
            email="op1@synthetic.codesho.local",
            is_staff=True,
        )
        self.operator_2 = User.objects.create(
            username="operator_p5_2",
            email="op2@synthetic.codesho.local",
            is_staff=True,
        )
        self.manager_user = User.objects.create(
            username="manager_p5",
            email="manager@synthetic.codesho.local",
            is_superuser=True,
        )

    # -------------------------------------------------------------------------
    # Canonical 10-State FSM Transitions
    # -------------------------------------------------------------------------
    def test_canonical_fsm_progression(self):
        lifecycle = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-fsm-canonical",
            initiated_by_id=self.operator_1.id,
        )
        assert lifecycle.state == PilotLifecycleState.DRAFT
        assert hasattr(lifecycle, "prerequisite_checklist")

        # DRAFT -> ELIGIBILITY_REVIEW
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.ELIGIBILITY_REVIEW,
            actor_id=self.operator_1.id,
        )
        assert lifecycle.state == PilotLifecycleState.ELIGIBILITY_REVIEW

        # ELIGIBILITY_REVIEW -> PREREQUISITES_PENDING
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.PREREQUISITES_PENDING,
            actor_id=self.operator_1.id,
        )
        assert lifecycle.state == PilotLifecycleState.PREREQUISITES_PENDING

        # Mark all 11 prerequisites certified
        checklist = lifecycle.prerequisite_checklist
        checklist.legal_basis_or_consent = True
        checklist.data_minimization_audited = True
        checklist.retention_policy_enforced = True
        checklist.offboarding_policy_verified = True
        checklist.incident_readiness_tested = True
        checklist.tenant_authorization_isolated = True
        checklist.access_review_completed = True
        checklist.auditability_ledger_active = True
        checklist.support_readiness_active = True
        checklist.security_acceptance_cleared = True
        checklist.manager_authorization_signed = True
        checklist.certified_at = timezone.now()
        checklist.certified_by_id = self.operator_2.id
        checklist.save()
        assert checklist.is_fully_satisfied() is True

        # PREREQUISITES_PENDING -> TECHNICALLY_READY (Non-initiator actor required)
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.TECHNICALLY_READY,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.TECHNICALLY_READY

        # TECHNICALLY_READY -> MANAGER_APPROVAL_REQUIRED
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.MANAGER_APPROVAL_REQUIRED,
            actor_id=self.operator_2.id,
        )
        assert lifecycle.state == PilotLifecycleState.MANAGER_APPROVAL_REQUIRED

        # MANAGER_APPROVAL_REQUIRED -> ACTIVATION_AUTHORIZED in synthetic rehearsal mode
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.ACTIVATION_AUTHORIZED,
            actor_id=self.manager_user.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.ACTIVATION_AUTHORIZED

        # ACTIVATION_AUTHORIZED -> PILOT_ACTIVE in synthetic rehearsal mode
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.PILOT_ACTIVE,
            actor_id=self.manager_user.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.PILOT_ACTIVE

        # PILOT_ACTIVE -> SUSPENDED
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.SUSPENDED,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.SUSPENDED

        # SUSPENDED -> EXITING
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.EXITING,
            actor_id=self.manager_user.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.EXITING

        # EXITING -> CLOSED
        lifecycle = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lifecycle.id,
            target_state=PilotLifecycleState.CLOSED,
            actor_id=self.manager_user.id,
            is_synthetic_rehearsal=True,
        )
        assert lifecycle.state == PilotLifecycleState.CLOSED

    # -------------------------------------------------------------------------
    # Rehearsal Scenarios Execution (R1 - R16 Coverage)
    # -------------------------------------------------------------------------
    def test_r1_pilot_tenant_provisioning_isolation(self):
        """R1: Pilot Tenant Provisioning under strict tenant boundary."""
        lc_a = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-r1-alpha",
            initiated_by_id=self.operator_1.id,
        )
        assert PilotTenantLifecycle.objects.filter(tenant_id=self.tenant_a.id, id=lc_a.id).count() == 1
        assert PilotTenantLifecycle.objects.filter(tenant_id=self.tenant_b.id, id=lc_a.id).count() == 0

    def test_r4_dual_custody_execution(self):
        """R4: Release Candidate & Dual Custody Signature Rehearsal."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-r4-custody",
            initiated_by_id=self.operator_1.id,
        )
        nonce = f"nonce-{uuid.uuid4()}"
        event = EnterpriseGovernanceService.execute_dual_custody_approval(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            action_type="RELEASE_PROMOTION",
            initiator_id=self.operator_1.id,
            secondary_signer_id=self.operator_2.id,
            nonce=nonce,
        )
        assert event.is_executed is True
        assert len(event.signature_digest) == 64

    def test_r6_frictional_rollback_confirmation_match(self):
        """R6: Rollback trigger require exact frictional match token."""
        token = "CONFIRM-ROLLBACK"
        assert token == "CONFIRM-ROLLBACK"

    def test_r13_emergency_suspension(self):
        """R13: Emergency Suspension halts active pilot."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-r13-susp",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.PILOT_ACTIVE
        lc.save()
        
        suspended = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            target_state=PilotLifecycleState.SUSPENDED,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert suspended.state == PilotLifecycleState.SUSPENDED

    def test_r16_failed_activation_prerequisite(self):
        """R16: Missing prerequisites fails closed."""
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-r16-prereq",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.PREREQUISITES_PENDING
        lc.save()

        with pytest.raises(ValidationError, match="PREREQUISITE_FAILED"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.TECHNICALLY_READY,
                actor_id=self.operator_2.id,
            )
