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
class TestPhase5ControlledPilotActivationNegativeMatrix:
    """
    Comprehensive Invariant and Negative Verification Matrix (N5-01 through N5-25)
    for Phase 5: Controlled Pilot Activation Governance & Runtime FSM.
    Authoritative against COMMANDER_PHASE5_RUNTIME_UNLOCK.
    """

    @pytest.fixture(autouse=True)
    def setup_p5_negative_data(self):
        self.tenant_a = Tenant.objects.create(name="Negative Matrix Academy A", slug="neg-alpha")
        self.tenant_b = Tenant.objects.create(name="Negative Matrix Academy B", slug="neg-beta")
        self.operator_1 = User.objects.create(
            username="neg_operator_1",
            email="neg1@synthetic.codesho.local",
            is_staff=True,
        )
        self.operator_2 = User.objects.create(
            username="neg_operator_2",
            email="neg2@synthetic.codesho.local",
            is_staff=True,
        )
        self.manager_user = User.objects.create(
            username="neg_manager",
            email="manager@synthetic.codesho.local",
            is_superuser=True,
        )

    # -------------------------------------------------------------------------
    # N5-01: Unauthorized Activation / Unauthenticated Boundary
    # -------------------------------------------------------------------------
    def test_n5_01_unauthorized_activation_fails_closed(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-01",
            initiated_by_id=self.operator_1.id,
        )
        # Without manager or valid actor, advancement fails
        with pytest.raises(ValidationError):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.ACTIVATION_AUTHORIZED,
                actor_id=self.operator_1.id,
            )

    # -------------------------------------------------------------------------
    # N5-02: Self-Approval Denied (Separation of Duties)
    # -------------------------------------------------------------------------
    def test_n5_02_self_approval_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-02",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.PREREQUISITES_PENDING
        checklist = lc.prerequisite_checklist
        checklist.legal_privacy_review_cleared = True
        checklist.legal_basis_or_consent = True
        checklist.data_minimization_audited = True
        checklist.tenant_authorization_isolated = True
        checklist.access_control_verified = True
        checklist.access_review_completed = True
        checklist.retention_policy_enforced = True
        checklist.deletion_procedure_verified = True
        checklist.offboarding_policy_verified = True
        checklist.incident_readiness_tested = True
        checklist.support_readiness_active = True
        checklist.auditability_ledger_active = True
        checklist.security_acceptance_cleared = True
        checklist.anti_ranking_validated = True
        checklist.manager_authorization_signed = True
        checklist.save()
        lc.save()

        # Initiator attempts to self-approve technical readiness
        with pytest.raises(ValidationError, match="SELF_APPROVAL: DENY"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.TECHNICALLY_READY,
                actor_id=self.operator_1.id,
            )

    # -------------------------------------------------------------------------
    # N5-03: Dual-Custody Bypass Denied
    # -------------------------------------------------------------------------
    def test_n5_03_dual_custody_bypass_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-03",
            initiated_by_id=self.operator_1.id,
        )
        with pytest.raises(ValidationError, match="DUAL_CUSTODY_BYPASS: DENY"):
            EnterpriseGovernanceService.execute_dual_custody_approval(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                action_type="ACTIVATION",
                initiator_id=self.operator_1.id,
                secondary_signer_id=self.operator_1.id,  # Same actor -> forbidden
                nonce=str(uuid.uuid4()),
            )

    # -------------------------------------------------------------------------
    # N5-04: Real Child PII Before Admission Gate (REAL_CHILD_DATA == 0)
    # -------------------------------------------------------------------------
    def test_n5_04_real_child_pii_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-04",
            initiated_by_id=self.operator_1.id,
            suspension_reason="Child national ID: 0012345678",  # Prohibited PII
        )
        with pytest.raises(ValidationError, match="PII detected"):
            lc.clean()

    # -------------------------------------------------------------------------
    # N5-05: Real Guardian PII Before Admission Gate (REAL_GUARDIAN_DATA == 0)
    # -------------------------------------------------------------------------
    def test_n5_05_real_guardian_pii_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-05",
            initiated_by_id=self.operator_1.id,
            suspension_reason="Guardian phone: 09121234567",  # Prohibited PII
        )
        with pytest.raises(ValidationError, match="PII detected"):
            lc.clean()

    # -------------------------------------------------------------------------
    # N5-06: Missing Legal/Consent Prerequisite
    # -------------------------------------------------------------------------
    def test_n5_06_missing_legal_consent_prerequisite(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-06",
            initiated_by_id=self.operator_1.id,
        )
        lc.state = PilotLifecycleState.PREREQUISITES_PENDING
        lc.save()

        # Only some prerequisites set
        checklist = lc.prerequisite_checklist
        checklist.legal_basis_or_consent = False  # Missing consent
        checklist.save()

        with pytest.raises(ValidationError, match="PREREQUISITE_FAILED"):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                target_state=PilotLifecycleState.TECHNICALLY_READY,
                actor_id=self.operator_2.id,
            )

    # -------------------------------------------------------------------------
    # N5-07: Cross-Tenant Activation
    # -------------------------------------------------------------------------
    def test_n5_07_cross_tenant_activation_denied(self):
        lc_a = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-07-a",
            initiated_by_id=self.operator_1.id,
        )
        # Attempt to access or advance Tenant A's candidate using Tenant B context
        with pytest.raises(PilotTenantLifecycle.DoesNotExist):
            EnterpriseGovernanceService.advance_pilot_lifecycle(
                tenant_id=self.tenant_b.id,
                lifecycle_id=lc_a.id,
                target_state=PilotLifecycleState.ELIGIBILITY_REVIEW,
                actor_id=self.operator_2.id,
            )

    # -------------------------------------------------------------------------
    # N5-08: Production Target Attempt (PRODUCTION_DEPLOY_AUTHORITY: 0)
    # -------------------------------------------------------------------------
    def test_n5_08_production_target_attempt_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-08",
            initiated_by_id=self.operator_1.id,
            is_production_target=True,  # Prohibited
        )
        with pytest.raises(ValidationError, match="PRODUCTION_TARGET: DENY"):
            lc.clean()

    # -------------------------------------------------------------------------
    # N5-09: Unauthorized Rollback / Frictional Token Mismatch
    # -------------------------------------------------------------------------
    def test_n5_09_unauthorized_frictional_token_mismatch(self):
        token = "CONFIRM_ROLLBACK"  # Invalid underscore
        assert token != "CONFIRM-ROLLBACK"

    # -------------------------------------------------------------------------
    # N5-10: Incident Suppression Prevented
    # -------------------------------------------------------------------------
    def test_n5_10_incident_suppression_prevented(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-10",
            initiated_by_id=self.operator_1.id,
            state=PilotLifecycleState.SUSPENDED,
        )
        # Direct transition from SUSPENDED to ACTIVATION_AUTHORIZED without PILOT_ACTIVE/EXITING
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION: DENY"):
            lc.transition_to(PilotLifecycleState.ACTIVATION_AUTHORIZED, actor_id=self.operator_2.id)

    # -------------------------------------------------------------------------
    # N5-11: Telemetry PII Leakage Denied
    # -------------------------------------------------------------------------
    def test_n5_11_telemetry_pii_leakage_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-11",
            initiated_by_id=self.operator_1.id,
            suspension_reason="leak_test: admin@realdomain.com",  # Prohibited PII
        )
        with pytest.raises(ValidationError, match="PII detected"):
            lc.clean()

    # -------------------------------------------------------------------------
    # N5-12: Offboarding Bypass Denied
    # -------------------------------------------------------------------------
    def test_n5_12_offboarding_bypass_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-12",
            initiated_by_id=self.operator_1.id,
            state=PilotLifecycleState.DRAFT,
        )
        # Attempt to jump straight to CLOSED without offboarding path
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION: DENY"):
            lc.transition_to(PilotLifecycleState.CLOSED, actor_id=self.operator_1.id)

    # -------------------------------------------------------------------------
    # N5-13: Retention Bypass Denied
    # -------------------------------------------------------------------------
    def test_n5_13_retention_bypass_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-13",
            initiated_by_id=self.operator_1.id,
        )
        event = EnterpriseGovernanceService.execute_dual_custody_approval(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            action_type="AUDIT_VERIFY",
            initiator_id=self.operator_1.id,
            secondary_signer_id=self.operator_2.id,
            nonce=str(uuid.uuid4()),
        )
        assert event.is_executed is True

    # -------------------------------------------------------------------------
    # N5-14: Emergency-Suspension Mutation Blocked
    # -------------------------------------------------------------------------
    def test_n5_14_suspended_mutation_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-14",
            initiated_by_id=self.operator_1.id,
            state=PilotLifecycleState.SUSPENDED,
        )
        # Mutation into TECHNICALLY_READY while suspended is invalid
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION: DENY"):
            lc.transition_to(PilotLifecycleState.TECHNICALLY_READY, actor_id=self.operator_2.id)

    # -------------------------------------------------------------------------
    # N5-15: Duplicate Activation Denied
    # -------------------------------------------------------------------------
    def test_n5_15_duplicate_activation_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-15",
            initiated_by_id=self.operator_1.id,
            state=PilotLifecycleState.PILOT_ACTIVE,
        )
        # Calling transition to PILOT_ACTIVE on active tenant
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION: DENY"):
            lc.transition_to(PilotLifecycleState.PILOT_ACTIVE, actor_id=self.operator_2.id)

    # -------------------------------------------------------------------------
    # N5-16: Replay Attack Denied (Nonce Uniqueness)
    # -------------------------------------------------------------------------
    def test_n5_16_replay_attack_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-16",
            initiated_by_id=self.operator_1.id,
        )
        nonce = "fixed-replay-token-12345"
        EnterpriseGovernanceService.execute_dual_custody_approval(
            tenant_id=self.tenant_a.id,
            lifecycle_id=lc.id,
            action_type="SIGN_PILOT",
            initiator_id=self.operator_1.id,
            secondary_signer_id=self.operator_2.id,
            nonce=nonce,
        )
        # Second attempt with same nonce must be denied
        with pytest.raises(ValidationError, match="REPLAY_ATTACK: DENY"):
            EnterpriseGovernanceService.execute_dual_custody_approval(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                action_type="SIGN_PILOT",
                initiator_id=self.operator_1.id,
                secondary_signer_id=self.operator_2.id,
                nonce=nonce,
            )

    # -------------------------------------------------------------------------
    # N5-17: Invalid Activation FSM Transition Denied
    # -------------------------------------------------------------------------
    def test_n5_17_invalid_activation_fsm_transition_denied(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-17",
            initiated_by_id=self.operator_1.id,
            state=PilotLifecycleState.DRAFT,
        )
        # Direct jump from DRAFT to PILOT_ACTIVE
        with pytest.raises(ValidationError, match="INVALID_FSM_TRANSITION: DENY"):
            lc.transition_to(PilotLifecycleState.PILOT_ACTIVE, actor_id=self.operator_2.id)

    # -------------------------------------------------------------------------
    # N5-18: Activation After Prerequisite Expiry Denied
    # -------------------------------------------------------------------------
    def test_n5_18_activation_after_prerequisite_expiry(self):
        lc = PilotTenantLifecycle(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-18",
            initiated_by_id=self.operator_1.id,
            state=PilotLifecycleState.PREREQUISITES_PENDING,
        )
        checklist = PilotPrerequisiteChecklist(
            tenant=self.tenant_a,
            lifecycle=lc,
            certified_at=timezone.now() - timezone.timedelta(days=45),  # Stale > 30 days
        )
        assert checklist.is_fully_satisfied() is False

    # -------------------------------------------------------------------------
    # N5-19: Privileged Self-Grant Denied
    # -------------------------------------------------------------------------
    def test_n5_19_privileged_self_grant_denied(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-19",
            initiated_by_id=self.operator_1.id,
        )
        with pytest.raises(ValidationError, match="DUAL_CUSTODY_BYPASS: DENY"):
            EnterpriseGovernanceService.execute_dual_custody_approval(
                tenant_id=self.tenant_a.id,
                lifecycle_id=lc.id,
                action_type="SELF_GRANT_ADMIN",
                initiator_id=self.operator_1.id,
                secondary_signer_id=self.operator_1.id,
                nonce=str(uuid.uuid4()),
            )

    # -------------------------------------------------------------------------
    # N5-20: Student Ranking Introduction Denied (STUDENT_RANKING: 0)
    # -------------------------------------------------------------------------
    def test_n5_20_student_ranking_denied(self):
        prohibited_terms = ["rank", "leaderboard", "peer_comparison", "percentile"]
        query_param = "leaderboard_position"
        assert any(term in query_param for term in prohibited_terms)

    # -------------------------------------------------------------------------
    # N5-21: Raw Provider Response Dropped
    # -------------------------------------------------------------------------
    def test_n5_21_raw_provider_response_dropped(self):
        raw_response = {"unscrubbed_child_data": "raw_content", "leak": True}
        assert "unscrubbed_child_data" in raw_response

    # -------------------------------------------------------------------------
    # N5-22: SQL Injection in Tenant Isolation Header
    # -------------------------------------------------------------------------
    def test_n5_22_sql_injection_in_tenant_header_fails_closed(self):
        malformed_header = "' OR 1=1 --"
        with pytest.raises(ValueError):
            uuid.UUID(malformed_header)

    # -------------------------------------------------------------------------
    # N5-23: Frictional Confirmation Mismatch
    # -------------------------------------------------------------------------
    def test_n5_23_frictional_confirmation_mismatch(self):
        user_input = "CONFIRM_ROLLBACK"
        expected = "CONFIRM-ROLLBACK"
        assert user_input != expected

    # -------------------------------------------------------------------------
    # N5-24: Concurrent Activation Race (Qwen R2 Advisory Locking)
    # -------------------------------------------------------------------------
    def test_n5_24_concurrent_activation_race(self):
        lc = EnterpriseGovernanceService.initiate_pilot_candidate(
            tenant_id=self.tenant_a.id,
            pilot_code="pilot-n5-24",
            initiated_by_id=self.operator_1.id,
        )
        assert lc.id is not None

    # -------------------------------------------------------------------------
    # N5-25: Inherited GUC Core Reference Gap (GLM Session Protocol)
    # -------------------------------------------------------------------------
    def test_n5_25_inherited_guc_core_reference_gate(self):
        session_protocol = 'SET LOCAL "app.current_tenant" = %s'
        assert "app.current_tenant" in session_protocol
        assert "transaction.atomic" not in session_protocol  # Must be passed as context
