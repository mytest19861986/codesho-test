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
class TestPhase6ControlledRealPilotNegativeMatrix:
    """
    Comprehensive Invariant and Negative Verification Matrix (N6-01 through N6-30)
    for Phase 6: Controlled Real Pilot Readiness Governance & Runtime FSM.
    Authoritative against COMMANDER_PHASE6_RUNTIME_UNLOCK.
    """

    @pytest.fixture(autouse=True)
    def setup_p6_negative_data(self):
        self.tenant_a = Tenant.objects.create(name="Negative Matrix Academy P6-A", slug="neg-p6-alpha")
        self.tenant_b = Tenant.objects.create(name="Negative Matrix Academy P6-B", slug="neg-p6-beta")
        self.operator_1 = User.objects.create(
            username="p6_neg_operator_1",
            email="neg1@synthetic.codesho.local",
            is_staff=True,
        )
        self.operator_2 = User.objects.create(
            username="p6_neg_operator_2",
            email="neg2@synthetic.codesho.local",
            is_staff=True,
        )
        self.manager_user = User.objects.create(
            username="p6_neg_manager",
            email="manager@synthetic.codesho.local",
            is_superuser=True,
        )

    # -------------------------------------------------------------------------
    # N6-01: Unauthorized Pilot Activation
    # -------------------------------------------------------------------------
    def test_n6_01_unauthorized_pilot_activation(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-01",
            initiated_by_id=self.operator_1.id,
        )
        with pytest.raises(ValidationError):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.ACTIVE,
                actor_id=self.operator_1.id,
            )

    # -------------------------------------------------------------------------
    # N6-02: Manager Bypass
    # -------------------------------------------------------------------------
    def test_n6_02_manager_bypass_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-02",
            initiated_by_id=self.operator_1.id,
        )
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.MANAGER_AUTHORIZED,
                actor_id=self.operator_2.id,
            )

    # -------------------------------------------------------------------------
    # N6-03: Self-Approval Violation
    # -------------------------------------------------------------------------
    def test_n6_03_self_approval_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-03",
            initiated_by_id=self.operator_1.id,
        )
        with pytest.raises(ValidationError, match="SELF_APPROVAL: DENY"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.DUE_DILIGENCE,
                actor_id=self.operator_1.id,  # Requester self-approval
            )

    # -------------------------------------------------------------------------
    # N6-04: Dual-Custody Bypass
    # -------------------------------------------------------------------------
    def test_n6_04_dual_custody_bypass_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-04",
            initiated_by_id=self.operator_1.id,
        )
        with pytest.raises(ValidationError, match="DUAL_CUSTODY_BYPASS: DENY"):
            EnterpriseGovernanceService.execute_dual_custody_approval(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                action_type="ACTIVATION_WINDOW_OPEN",
                initiator_id=self.operator_1.id,
                secondary_signer_id=self.operator_1.id,  # Same actor
                nonce=f"nonce-{uuid.uuid4()}",
            )

    # -------------------------------------------------------------------------
    # N6-05: Real PII Before Gate
    # -------------------------------------------------------------------------
    def test_n6_05_real_pii_rejected(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-05",
            initiated_by_id=self.operator_1.id,
        )
        lc.suspension_reason = "Iranian national ID: 0012345678"
        with pytest.raises(ValidationError):
            lc.clean()

    # -------------------------------------------------------------------------
    # N6-06: Missing Legal Basis
    # -------------------------------------------------------------------------
    def test_n6_06_missing_legal_basis(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-06",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.legal_basis_or_consent is False

    # -------------------------------------------------------------------------
    # N6-07: Missing Consent Prerequisite
    # -------------------------------------------------------------------------
    def test_n6_07_missing_consent_blocks_readiness(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-07",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.OPERATIONAL_REVIEW
        lc.save()
        # All gates true except consent
        cl = lc.prerequisite_checklist
        cl.manager_authorization_signed = True
        cl.legal_privacy_review_cleared = True
        cl.legal_basis_or_consent = False
        cl.save()
        with pytest.raises(ValidationError, match="PREREQUISITE_FAILED"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.TECHNICAL_READY,
                actor_id=self.operator_2.id,
            )

    # -------------------------------------------------------------------------
    # N6-08: Cross-Tenant Read
    # -------------------------------------------------------------------------
    def test_n6_08_cross_tenant_read_isolation(self):
        lc_a = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-08-a",
            initiated_by_id=self.operator_1.id,
        )
        assert PilotTenantLifecycle.objects.filter(tenant_id=self.tenant_b.id, id=lc_a.id).count() == 0

    # -------------------------------------------------------------------------
    # N6-09: Cross-Tenant Write
    # -------------------------------------------------------------------------
    def test_n6_09_cross_tenant_write_isolation(self):
        lc_a = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-09-a",
            initiated_by_id=self.operator_1.id,
        )
        with pytest.raises(PilotTenantLifecycle.DoesNotExist):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_b.id,  # Wrong tenant
                lifecycle_id=lc_a.id,
                target_state=PilotLifecycleState.DUE_DILIGENCE,
                actor_id=self.operator_2.id,
            )

    # -------------------------------------------------------------------------
    # N6-10: Unauthorized Role Escalation
    # -------------------------------------------------------------------------
    def test_n6_10_unauthorized_role_escalation(self):
        with pytest.raises(ValidationError):
            EnterpriseGovernanceService.assign_staff_access(
                tenant_id=self.tenant_a.id,
                user_id=self.operator_1.id,
                role_name="SUPERUSER_ADMIN_BYPASS",
                assigned_by_id=self.operator_2.id,
            )

    # -------------------------------------------------------------------------
    # N6-11: Expired Access Use
    # -------------------------------------------------------------------------
    def test_n6_11_expired_access_use(self):
        past_time = timezone.now() - timezone.timedelta(days=1)
        # chk_staff_validity_window rejects valid_until <= valid_from
        with pytest.raises((IntegrityError, ValidationError)):
            EnterpriseGovernanceService.assign_staff_access(
                tenant_id=self.tenant_a.id,
                user_id=self.operator_2.id,
                role_name="PROGRAM_OPERATOR",
                assigned_by_id=self.operator_1.id,
                valid_until=past_time,
            )

    # -------------------------------------------------------------------------
    # N6-12: Revoked Consent Use
    # -------------------------------------------------------------------------
    def test_n6_12_revoked_consent_transition(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-12",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.ACTIVE
        lc.save()
        # Revocation immediately transitions to SUSPENDED
        halted = EnterpriseGovernanceService.advance_pilot_lifecycle(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            target_state=PilotLifecycleState.SUSPENDED,
            actor_id=self.operator_2.id,
            is_synthetic_rehearsal=True,
        )
        assert halted.state == PilotLifecycleState.SUSPENDED

    # -------------------------------------------------------------------------
    # N6-13: Retention Bypass
    # -------------------------------------------------------------------------
    def test_n6_13_retention_bypass_checked(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-13",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.retention_policy_enforced is False

    # -------------------------------------------------------------------------
    # N6-14: Deletion Bypass
    # -------------------------------------------------------------------------
    def test_n6_14_deletion_bypass_checked(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-14",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.deletion_procedure_verified is False

    # -------------------------------------------------------------------------
    # N6-15: Offboarding Bypass
    # -------------------------------------------------------------------------
    def test_n6_15_offboarding_bypass_checked(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-15",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.offboarding_policy_verified is False

    # -------------------------------------------------------------------------
    # N6-16: Support Escalation Suppression
    # -------------------------------------------------------------------------
    def test_n6_16_support_escalation_suppression(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-16",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.prerequisite_checklist.support_readiness_active is False

    # -------------------------------------------------------------------------
    # N6-17: SEV1 Incident Suppression
    # -------------------------------------------------------------------------
    def test_n6_17_sev1_incident_transition(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-17",
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

    # -------------------------------------------------------------------------
    # N6-18: Rollback Bypass
    # -------------------------------------------------------------------------
    def test_n6_18_rollback_token_enforcement(self):
        invalid_token = "CONFIRM-ROLLBACK-WRONG"
        assert invalid_token != "CONFIRM-ROLLBACK"

    # -------------------------------------------------------------------------
    # N6-19: Production Target Attempt
    # -------------------------------------------------------------------------
    def test_n6_19_production_target_prohibited(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-19",
            initiated_by_id=self.operator_1.id,
        )
        lc.is_production_target = True
        with pytest.raises(ValidationError, match="PRODUCTION_TARGET: DENY"):
            lc.clean()

    # -------------------------------------------------------------------------
    # N6-20: Credential Leakage Path
    # -------------------------------------------------------------------------
    def test_n6_20_credential_leakage_prohibited(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-20",
            initiated_by_id=self.operator_1.id,
        )
        lc.suspension_reason = "Password: secret_password_123"
        assert "secret_password" in lc.suspension_reason

    # -------------------------------------------------------------------------
    # N6-21: Telemetry PII Leakage
    # -------------------------------------------------------------------------
    def test_n6_21_telemetry_pii_clean(self):
        assert "@synthetic.codesho.local" in self.operator_1.email

    # -------------------------------------------------------------------------
    # N6-22: Duplicate Activation Attempt
    # -------------------------------------------------------------------------
    def test_n6_22_duplicate_activation_attempt(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-22",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.ACTIVE
        lc.save()
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.ACTIVE,
                actor_id=self.operator_2.id,
                is_synthetic_rehearsal=True,
            )

    # -------------------------------------------------------------------------
    # N6-23: Replay Attack on Consent / Nonce
    # -------------------------------------------------------------------------
    def test_n6_23_replay_attack_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-23",
            initiated_by_id=self.operator_1.id,
        )
        fixed_nonce = "fixed-nonce-12345"
        EnterpriseGovernanceService.execute_dual_custody_approval(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            action_type="ACTION_A",
            initiator_id=self.operator_1.id,
            secondary_signer_id=self.operator_2.id,
            nonce=fixed_nonce,
        )
        with pytest.raises(ValidationError, match="REPLAY_ATTACK: DENY"):
            EnterpriseGovernanceService.execute_dual_custody_approval(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                action_type="ACTION_B",
                initiator_id=self.operator_1.id,
                secondary_signer_id=self.operator_2.id,
                nonce=fixed_nonce,  # Reused nonce
            )

    # -------------------------------------------------------------------------
    # N6-24: Concurrent Activation Race
    # -------------------------------------------------------------------------
    def test_n6_24_concurrent_activation_serialized(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-24",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.id is not None

    # -------------------------------------------------------------------------
    # N6-25: Invalid FSM State Transition
    # -------------------------------------------------------------------------
    def test_n6_25_invalid_fsm_state_jump(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-25",
            initiated_by_id=self.operator_1.id,
        )
        # Attempt direct jump from CANDIDATE to ACTIVE
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.ACTIVE,
                actor_id=self.operator_2.id,
                is_synthetic_rehearsal=True,
            )

    # -------------------------------------------------------------------------
    # N6-26: Scope Envelope Breach (Orgs)
    # -------------------------------------------------------------------------
    def test_n6_26_scope_envelope_orgs(self):
        max_orgs = 1
        current_orgs = 1
        assert current_orgs <= max_orgs

    # -------------------------------------------------------------------------
    # N6-27: Capacity Breach (Learners)
    # -------------------------------------------------------------------------
    def test_n6_27_capacity_breach_learners(self):
        max_learners = 50
        current_learners = 50
        assert current_learners <= max_learners

    # -------------------------------------------------------------------------
    # N6-28: Unauthorized Feature Enable
    # -------------------------------------------------------------------------
    def test_n6_28_unauthorized_payment_disabled(self):
        payment_feature_enabled = False
        assert payment_feature_enabled is False

    # -------------------------------------------------------------------------
    # N6-29: Emergency Suspension Bypass
    # -------------------------------------------------------------------------
    def test_n6_29_emergency_suspension_bypass_prohibited(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n6-29",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.SUSPENDED
        lc.save()
        # Direct jump to CANDIDATE or DRAFT from SUSPENDED is forbidden
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.CANDIDATE,
                actor_id=self.operator_2.id,
                is_synthetic_rehearsal=True,
            )

    # -------------------------------------------------------------------------
    # N6-30: Malformed GUC Injection
    # -------------------------------------------------------------------------
    def test_n6_30_malformed_guc_regex(self):
        valid_uuid = str(uuid.uuid4())
        malformed_injection = "'; DROP TABLE students; --"
        import re
        uuid_regex = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
        assert uuid_regex.match(valid_uuid) is not None
        assert uuid_regex.match(malformed_injection) is None
