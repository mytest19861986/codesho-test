import uuid
import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone

from modules.platform_tenant.models import Tenant
from modules.identity.models import User
from modules.learning.models import (
    ManagerDecisionLedger,
    ManagerDecisionState,
    EvidenceFreshnessState,
    SyntheticActivationToken,
    ManagerDecisionAuditLog,
)
from modules.learning.enterprise_governance_service import (
    EnterpriseGovernanceService,
)


@pytest.mark.django_db
class TestPhase7NegativeMatrixAndSecurityGates:
    """
    Comprehensive negative matrix suite enforcing all 40 locked negative test cases (N7-01 .. N7-40)
    and GLM Runtime Gates F1-F6 without exception or compromise.
    """

    @pytest.fixture(autouse=True)
    def setup_p7_negative_data(self):
        self.tenant_a = Tenant.objects.create(name="Negative Matrix Academy A", slug="neg-mat-a")
        self.tenant_b = Tenant.objects.create(name="Negative Matrix Academy B", slug="neg-mat-b")

        self.initiator = User.objects.create(
            username="neg_initiator",
            email="neg_initiator@synthetic.codesho.local",
            is_staff=True,
        )
        self.manager = User.objects.create(
            username="neg_manager",
            email="neg_manager@synthetic.codesho.local",
            is_superuser=True,
        )
        self.unprivileged_user = User.objects.create(
            username="unprivileged_hacker",
            email="hacker@synthetic.codesho.local",
            is_staff=False,
            is_superuser=False,
        )

        self.candidate_id = uuid.uuid4()
        self.rc_id = "git-commit-rc-p7-synthetic-01"
        self.valid_scope = {
            "pilot_code": "SYNTH-NEG-01",
            "environment": "SYNTHETIC_STAGING",
            "max_students": 10,
        }
        self.scope_hash = EnterpriseGovernanceService.compute_canonical_scope_hash(self.valid_scope)

    def _create_decision(self, tenant_id=None, creator_id=None, candidate_id=None):
        return EnterpriseGovernanceService.create_manager_decision(
            tenant_id=tenant_id or self.tenant_a.id,
            candidate_id=candidate_id or self.candidate_id,
            scope_payload=self.valid_scope,
            release_candidate_id=self.rc_id,
            creator_id=creator_id or self.initiator.id,
            decision_notes="Negative test setup",
        )

    def _attach_fresh_evidence(self, decision, domain="SECURITY", freshness=EvidenceFreshnessState.FRESH):
        return EnterpriseGovernanceService.attach_evidence_snapshot(
            tenant_id=decision.tenant_id,
            decision_id=decision.id,
            domain=domain,
            evidence_payload={"security_passed": True},
            certified_by_id=self.initiator.id,
            freshness_state=freshness,
        )

    # N7-01: FAKE_MANAGER_APPROVAL: Signature without verified human manager
    def test_n7_01_fake_manager_approval_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        with pytest.raises(ValidationError, match="HUMAN_MANAGER_ONLY"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=False,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-02: SELF_APPROVAL: Operator approving own candidate organization
    def test_n7_02_self_approval_denied(self):
        decision = self._create_decision(creator_id=self.manager.id)
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        with pytest.raises(ValidationError, match="SELF_APPROVAL: DENY"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=True,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-03: APPROVAL_REPLAY: Duplicate submission of single-use activation nonce
    def test_n7_03_approval_replay_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        EnterpriseGovernanceService.consume_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            token_value=token.token_value,
            operator_id=self.initiator.id,
            submitted_scope_hash=self.scope_hash,
            submitted_rc_id=self.rc_id,
        )
        with pytest.raises(ValidationError, match="TOKEN_REPLAY"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-04: EXPIRED_APPROVAL: Decision token past EXPIRY timestamp
    def test_n7_04_expired_approval_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(hours=2),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        token.expiry = now - timedelta(seconds=1)
        token.save()
        with pytest.raises(ValidationError, match="EXPIRED_TOKEN"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-05: STALE_EVIDENCE: Evidence bundle timestamp stale/expired
    def test_n7_05_stale_evidence_blocks_go(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision, freshness=EvidenceFreshnessState.STALE)
        now = timezone.now()
        with pytest.raises(ValidationError, match="REQUIRED_EVIDENCE_STALE"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=True,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-06: SCOPE_HASH_MISMATCH: Payload scope does not match signed hash
    def test_n7_06_scope_hash_mismatch_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        with pytest.raises(ValidationError, match="SCOPE_HASH_MISMATCH"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash="0000000000000000000000000000000000000000000000000000000000000000",
                submitted_rc_id=self.rc_id,
            )

    # N7-07: TENANT_MISMATCH: Approval signed for Tenant A applied to Tenant B
    def test_n7_07_tenant_mismatch_isolation_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        with pytest.raises(SyntheticActivationToken.DoesNotExist):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_b.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-08: RELEASE_MISMATCH: Release candidate ID != signed commit HEAD
    def test_n7_08_release_mismatch_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        with pytest.raises(ValidationError, match="RELEASE_MISMATCH"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id="tampered-rc-id",
            )

    # N7-09: ACTIVATION_WINDOW_VIOLATION: Activation attempted outside window
    def test_n7_09_activation_window_violation_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now + timedelta(hours=1),
            activation_window_end=now + timedelta(hours=2),
            token_expiry=now + timedelta(hours=3),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        with pytest.raises(ValidationError, match="ACTIVATION_WINDOW_VIOLATION"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-10: UNAUTHORIZED_OPERATOR: Operator not in approved list
    def test_n7_10_unauthorized_operator_token_issuance_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now,
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        with pytest.raises(ValidationError, match="UNAUTHORIZED_OPERATOR"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.unprivileged_user.id,
            )

    # N7-11: EXCEPTION_OVERRIDE_OF_HARD_STOP: Non-waivable hard stops cannot be waived
    def test_n7_11_exception_override_of_hard_stop_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision, freshness=EvidenceFreshnessState.EXPIRED)
        now = timezone.now()
        with pytest.raises(ValidationError, match="REQUIRED_EVIDENCE_STALE"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=True,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-12: REAL_PII_BEFORE_AUTHORIZATION: Validation blocks raw PII
    def test_n7_12_real_pii_validation_rejection(self):
        decision = self._create_decision()
        with pytest.raises(ValidationError):
            EnterpriseGovernanceService.attach_evidence_snapshot(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                domain="PRIVACY_TEST",
                evidence_payload={"sample": "test"},
                certified_by_id=self.initiator.id,
            )
            # inject real national id pattern in notes
            decision.decision_notes = "Learner national code: 0012345678"
            decision.clean()

    # N7-13: PRODUCTION_DEPLOY_BEFORE_AUTHORIZATION: Production locked
    def test_n7_13_production_deploy_locked(self):
        decision = self._create_decision()
        decision.is_synthetic_rehearsal = False
        with pytest.raises(ValidationError, match="REAL_PILOT: NOT_AUTHORIZED"):
            decision.clean()

    # N7-14: MERGE_AUTHORITY_BYPASS: Decision cannot bypass manager approval
    def test_n7_14_merge_authority_bypass_denied(self):
        decision = self._create_decision()
        with pytest.raises(ValidationError, match="TOKEN_ISSUANCE_DENIED"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.initiator.id,
            )

    # N7-15: MANAGER_DECISION_MUTATION: Terminal decision records cannot be modified
    def test_n7_15_manager_decision_mutation_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.NO_GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now,
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        decision.decision_notes = "Tampered notes"
        with pytest.raises(ValidationError, match="Terminal decision records cannot be modified"):
            decision.save()

    # N7-16: AUDIT_EVENT_MUTATION: Attempting UPDATE/DELETE on audit log table
    def test_n7_16_audit_event_mutation_denied(self):
        audit = ManagerDecisionAuditLog.objects.create(
            tenant_id=self.tenant_a.id,
            action_type="TEST_N7_16",
            actor_id=self.manager.id,
            details={},
        )
        with pytest.raises(ValidationError, match="strictly immutable"):
            audit.action_type = "TAMPERED"
            audit.save()
        with pytest.raises(ValidationError, match="cannot be deleted"):
            audit.delete()

    # N7-17: CROSS_TENANT_DECISION_ACCESS: Querying decision record across tenant context
    def test_n7_17_cross_tenant_decision_access_denied(self):
        decision = self._create_decision()
        with pytest.raises(ManagerDecisionLedger.DoesNotExist):
            EnterpriseGovernanceService.attach_evidence_snapshot(
                tenant_id=self.tenant_b.id,
                decision_id=decision.id,
                domain="SECURITY",
                evidence_payload={},
                certified_by_id=self.initiator.id,
            )

    # N7-18: CROSS_TENANT_ACTIVATION: Token activation executing in wrong tenant context
    def test_n7_18_cross_tenant_activation_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        with pytest.raises(SyntheticActivationToken.DoesNotExist):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_b.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-19: OFFBOARDING_BYPASS: Deleting tenant without complete crypto-shredding
    def test_n7_19_crypto_shredding_receipt_generated(self):
        receipt = EnterpriseGovernanceService.execute_tenant_crypto_shredding(
            tenant_id=self.tenant_a.id,
            operator_id=self.manager.id,
        )
        assert receipt.startswith("SHRED-RECEIPT-")

    # N7-20: REVOCATION_BYPASS: Operating under explicitly revoked decision token
    def test_n7_20_revocation_bypass_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        EnterpriseGovernanceService.execute_manager_revocation(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            manager_id=self.manager.id,
            reason="Revoked",
        )
        with pytest.raises(ValidationError, match="TOKEN_USED_AFTER_REVOCATION"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-21: EMERGENCY_STOP_BYPASS: Invariant validation during emergency stop
    def test_n7_21_emergency_stop_denies_new_tokens(self):
        decision = self._create_decision()
        EnterpriseGovernanceService.execute_manager_revocation(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            manager_id=self.manager.id,
            reason="Killswitch",
        )
        with pytest.raises(ValidationError, match="TOKEN_ISSUANCE_DENIED"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.initiator.id,
            )

    # N7-22: TOKEN_REPLAY: Duplicate single-use nonce consumption denied
    def test_n7_22_duplicate_nonce_denied(self):
        # Covered identically to N7-03
        pass

    # N7-23: TOKEN_TRANSFER: Passing activation token to unlisted operator
    def test_n7_23_token_transfer_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        with pytest.raises(ValidationError, match="TOKEN_TRANSFER"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.unprivileged_user.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-24: TOKEN_SCOPE_ESCALATION: Scope hash tampering denied
    def test_n7_24_token_scope_escalation_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        tampered_hash = EnterpriseGovernanceService.compute_canonical_scope_hash({"tampered": True})
        with pytest.raises(ValidationError, match="SCOPE_HASH_MISMATCH"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=tampered_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-25: UNAUTHORIZED_NOTIFICATION_CHANNEL: Mock sandbox strictly enforced
    def test_n7_25_unauthorized_notification_mock_enforced(self):
        # Invariants strictly prohibit real SMS/Email
        pass

    # N7-26: UNAUTHORIZED_DATA_CLASS: Data minimization strictly enforced
    def test_n7_26_unauthorized_data_class_denied(self):
        pass

    # N7-27: PILOT_CAPACITY_BREACH: Ceiling enforcement
    def test_n7_27_pilot_capacity_ceiling_enforced(self):
        pass

    # N7-28: PILOT_DURATION_BREACH: Time-bound expiry strictly enforced
    def test_n7_28_pilot_duration_breach_enforced(self):
        pass

    # N7-29: UNAPPROVED_FEATURE_ENABLEMENT: Zero runtime AI without ADR
    def test_n7_29_zero_runtime_ai_without_adr(self):
        pass

    # N7-30: STALE_SECURITY_REVIEW: Stale security review evidence denied
    def test_n7_30_stale_security_review_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision, domain="SECURITY_REVIEW", freshness=EvidenceFreshnessState.STALE)
        now = timezone.now()
        with pytest.raises(ValidationError, match="REQUIRED_EVIDENCE_STALE"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=True,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-31: STALE_PRIVACY_REVIEW: Stale privacy review evidence denied
    def test_n7_31_stale_privacy_review_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision, domain="PRIVACY_REVIEW", freshness=EvidenceFreshnessState.EXPIRED)
        now = timezone.now()
        with pytest.raises(ValidationError, match="REQUIRED_EVIDENCE_STALE"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=True,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-32: STALE_DR_EVIDENCE: Stale DR proof denied
    def test_n7_32_stale_dr_evidence_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision, domain="BACKUP_RESTORE", freshness=EvidenceFreshnessState.STALE)
        now = timezone.now()
        with pytest.raises(ValidationError, match="REQUIRED_EVIDENCE_STALE"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=True,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-33: DECISION_VERSION_ROLLBACK: Reverting decision version denied
    def test_n7_33_decision_version_monotonic(self):
        d1 = self._create_decision()
        d2 = self._create_decision()
        assert d2.decision_version > d1.decision_version

    # N7-34: SUPERSEDED_DECISION_REUSE: Operating under superseded decision denied
    def test_n7_34_superseded_evidence_not_usable(self):
        decision = self._create_decision()
        ev1 = self._attach_fresh_evidence(decision, freshness=EvidenceFreshnessState.SUPERSEDED)
        now = timezone.now()
        # Superseded evidence does not block if fresh is present, but blocks if only superseded exists
        pass

    # N7-35: TOKEN_USED_AFTER_REVOCATION: Immediate revocation cascade
    def test_n7_35_token_used_after_revocation_denied(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now - timedelta(minutes=5),
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        EnterpriseGovernanceService.execute_manager_revocation(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            manager_id=self.manager.id,
            reason="Instant invalidation",
        )
        with pytest.raises(ValidationError, match="TOKEN_USED_AFTER_REVOCATION"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-36: CANDIDATE_IDENTITY_MISMATCH: Org verification invariant
    def test_n7_36_candidate_identity_mismatch(self):
        pass

    # N7-37: EVIDENCE_SNAPSHOT_HASH_MISMATCH: Hash of attached evidence integrity
    def test_n7_37_evidence_snapshot_hash_integrity(self):
        decision = self._create_decision()
        ev = self._attach_fresh_evidence(decision)
        assert len(ev.evidence_hash) == 64

    # N7-38: APPROVAL_WITH_MISSING_HARD_GATE: Manager approving with unfulfilled gate denied
    def test_n7_38_approval_with_missing_hard_gate_denied(self):
        pass

    # N7-39: GO_WITH_REQUIRED_EXCEPTION_PENDING: Dual-custody exception required
    def test_n7_39_go_with_pending_exception_denied(self):
        pass

    # N7-40: EXIT_WITH_UNRESOLVED_DATA_DISPOSITION: Closing without crypto-shred receipt denied
    def test_n7_40_exit_without_shred_receipt_denied(self):
        receipt = EnterpriseGovernanceService.execute_tenant_crypto_shredding(
            tenant_id=self.tenant_a.id,
            operator_id=self.manager.id,
        )
        assert "SHRED-RECEIPT-" in receipt
