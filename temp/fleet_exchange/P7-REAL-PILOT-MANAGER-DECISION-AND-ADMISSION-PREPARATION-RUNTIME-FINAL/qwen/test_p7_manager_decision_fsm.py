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
class TestPhase7ManagerDecisionFSMAndRehearsals:
    """
    Authoritative test suite for Phase 7 Manager Decision Ledger & FSM Runtime
    covering rehearsals P7_R1 through P7_R20 and GLM gates F1-F6.
    """

    @pytest.fixture(autouse=True)
    def setup_p7_data(self):
        self.tenant_a = Tenant.objects.create(name="Synthetic P7 Academy A", slug="pilot-p7-synth-a")
        self.tenant_b = Tenant.objects.create(name="Synthetic P7 Academy B", slug="pilot-p7-synth-b")

        self.initiator = User.objects.create(
            username="p7_initiator",
            email="initiator@synthetic.codesho.local",
            is_staff=True,
        )
        self.manager = User.objects.create(
            username="p7_manager",
            email="manager@synthetic.codesho.local",
            is_superuser=True,
        )
        self.non_manager = User.objects.create(
            username="p7_regular_user",
            email="regular@synthetic.codesho.local",
            is_staff=False,
            is_superuser=False,
        )

        self.candidate_id = uuid.uuid4()
        self.rc_id = "git-commit-rc-p7-synthetic-01"
        self.valid_scope = {
            "pilot_code": "SYNTH-P7-PILOT-01",
            "environment": "SYNTHETIC_STAGING",
            "max_students": 25,
            "allowed_modules": ["math", "physics"],
        }
        self.scope_hash = EnterpriseGovernanceService.compute_canonical_scope_hash(self.valid_scope)

    def _create_decision(self, tenant_id=None, creator_id=None):
        return EnterpriseGovernanceService.create_manager_decision(
            tenant_id=tenant_id or self.tenant_a.id,
            candidate_id=self.candidate_id,
            scope_payload=self.valid_scope,
            release_candidate_id=self.rc_id,
            creator_id=creator_id or self.initiator.id,
            decision_notes="Test decision setup",
        )

    def _attach_fresh_evidence(self, decision, domain="SECURITY_AND_COMPLIANCE", freshness=EvidenceFreshnessState.FRESH):
        return EnterpriseGovernanceService.attach_evidence_snapshot(
            tenant_id=decision.tenant_id,
            decision_id=decision.id,
            domain=domain,
            evidence_payload={"mfa_enforced": True, "anti_ranking_verified": True},
            certified_by_id=self.initiator.id,
            freshness_state=freshness,
        )

    # -------------------------------------------------------------------------
    # P7_R1: Canonical GO Path (DRAFT -> EVIDENCE -> DETERMINATION_GO -> TOKEN_ISSUED -> CONSUMED)
    # -------------------------------------------------------------------------
    def test_p7_r1_canonical_go_path(self):
        decision = self._create_decision()
        assert decision.state == ManagerDecisionState.DRAFT
        assert decision.scope_hash == self.scope_hash

        ev = self._attach_fresh_evidence(decision)
        assert ev.freshness_state == EvidenceFreshnessState.FRESH

        now = timezone.now()
        start = now - timedelta(minutes=5)
        end = now + timedelta(hours=2)
        expiry = now + timedelta(hours=1)

        # Manager Determination -> GO
        decision = EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=start,
            activation_window_end=end,
            token_expiry=expiry,
            determination_notes="All 14 gates pass and synthetic bounds verified.",
        )
        assert decision.state == ManagerDecisionState.GO
        assert decision.approver_id == self.manager.id
        assert decision.is_human_manager is True

        # Issue Synthetic Activation Token
        token = EnterpriseGovernanceService.issue_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            operator_id=self.initiator.id,
        )
        assert token.is_consumed is False
        assert token.scope_hash == self.scope_hash

        # Consume Synthetic Activation Token
        consumed = EnterpriseGovernanceService.consume_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            token_value=token.token_value,
            operator_id=self.initiator.id,
            submitted_scope_hash=self.scope_hash,
            submitted_rc_id=self.rc_id,
        )
        assert consumed.is_consumed is True
        assert consumed.consumed_at is not None

    # -------------------------------------------------------------------------
    # P7_R2: Determination NO_GO (Terminal Fail-Closed)
    # -------------------------------------------------------------------------
    def test_p7_r2_determination_no_go(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)

        now = timezone.now()
        decision = EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.NO_GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now,
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
            determination_notes="Failed criteria.",
        )
        assert decision.state == ManagerDecisionState.NO_GO

        # Token issuance must fail closed
        with pytest.raises(ValidationError, match="Decision is not in authorized GO state"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.initiator.id,
            )

    # -------------------------------------------------------------------------
    # P7_R3: Determination DEFER
    # -------------------------------------------------------------------------
    def test_p7_r3_determination_defer(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)

        now = timezone.now()
        decision = EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.DEFER,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now,
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
            determination_notes="Pending schedule clarification.",
        )
        assert decision.state == ManagerDecisionState.DEFER

    # -------------------------------------------------------------------------
    # P7_R4: Non-Human Manager Determination Prohibited (GLM Gate)
    # -------------------------------------------------------------------------
    def test_p7_r4_non_human_manager_determination_prohibited(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)

        now = timezone.now()
        with pytest.raises(ValidationError, match="Automated agents/applications are forbidden"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.GO,
                manager_user_id=self.manager.id,
                is_human_manager=False,  # Automated agent attempt
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # -------------------------------------------------------------------------
    # P7_R5: Self-Approval Prevention (Creator != Manager)
    # -------------------------------------------------------------------------
    def test_p7_r5_self_approval_prohibited(self):
        decision = self._create_decision(creator_id=self.manager.id)
        self._attach_fresh_evidence(decision)

        now = timezone.now()
        with pytest.raises(ValidationError, match="Operator cannot approve own candidate organization decision"):
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

    # -------------------------------------------------------------------------
    # P7_R6: Stale/Expired Evidence Blocks GO Determination
    # -------------------------------------------------------------------------
    def test_p7_r6_stale_evidence_blocks_go_determination(self):
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

    # -------------------------------------------------------------------------
    # P7_R7: Single-Use Token Consumption (Replay Attack Blocked)
    # -------------------------------------------------------------------------
    def test_p7_r7_token_replay_blocked(self):
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
        # 1st consume OK
        EnterpriseGovernanceService.consume_synthetic_activation_token(
            tenant_id=self.tenant_a.id,
            token_value=token.token_value,
            operator_id=self.initiator.id,
            submitted_scope_hash=self.scope_hash,
            submitted_rc_id=self.rc_id,
        )
        # 2nd consume REPLAY DENIED
        with pytest.raises(ValidationError, match="TOKEN_REPLAY"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # -------------------------------------------------------------------------
    # P7_R8: Token Expiration Block
    # -------------------------------------------------------------------------
    def test_p7_r8_token_expiration_block(self):
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
            activation_window_start=now - timedelta(minutes=10),
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

    # -------------------------------------------------------------------------
    # P7_R9: Scope Hash Mismatch Rejection
    # -------------------------------------------------------------------------
    def test_p7_r9_scope_hash_mismatch_rejection(self):
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
        tampered_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        with pytest.raises(ValidationError, match="SCOPE_HASH_MISMATCH"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=tampered_hash,
                submitted_rc_id=self.rc_id,
            )

    # -------------------------------------------------------------------------
    # P7_R10: Release Candidate Mismatch Rejection
    # -------------------------------------------------------------------------
    def test_p7_r10_release_mismatch_rejection(self):
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
                submitted_rc_id="tampered-commit-sha",
            )

    # -------------------------------------------------------------------------
    # P7_R11: Unauthorized Operator Presentation Rejection (Token Transfer Denial)
    # -------------------------------------------------------------------------
    def test_p7_r11_token_transfer_prohibited(self):
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
        # Non-authorized operator attempts to consume
        with pytest.raises(ValidationError, match="TOKEN_TRANSFER"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.non_manager.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # -------------------------------------------------------------------------
    # P7_R12: Manager Revocation Cascades to All Tokens
    # -------------------------------------------------------------------------
    def test_p7_r12_manager_revocation_cascades_to_tokens(self):
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
        # Revoke
        EnterpriseGovernanceService.execute_manager_revocation(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            manager_id=self.manager.id,
            reason="Emergency test stop",
        )
        token.refresh_from_db()
        assert token.is_revoked is True

        with pytest.raises(ValidationError, match="TOKEN_USED_AFTER_REVOCATION"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # -------------------------------------------------------------------------
    # P7_R13: Crypto Shredding & Immutable Receipt (GLM F5)
    # -------------------------------------------------------------------------
    def test_p7_r13_crypto_shredding_and_receipt(self):
        decision = self._create_decision()
        receipt = EnterpriseGovernanceService.execute_tenant_crypto_shredding(
            tenant_id=self.tenant_a.id,
            operator_id=self.manager.id,
            decision_id=decision.id,
        )
        assert receipt.startswith("SHRED-RECEIPT-")

        audit = ManagerDecisionAuditLog.objects.filter(
            tenant_id=self.tenant_a.id,
            action_type="TENANT_CRYPTO_SHREDDED",
        ).first()
        assert audit is not None
        assert audit.shred_receipt == receipt

    # -------------------------------------------------------------------------
    # P7_R14: Canonical Scope Hash Determinism (GLM F3)
    # -------------------------------------------------------------------------
    def test_p7_r14_scope_hash_determinism(self):
        dict_1 = {"z": 10, "a": 1, "m": {"sub": [1, 2, 3]}}
        dict_2 = {"a": 1, "m": {"sub": [1, 2, 3]}, "z": 10}
        assert EnterpriseGovernanceService.compute_canonical_scope_hash(dict_1) == EnterpriseGovernanceService.compute_canonical_scope_hash(dict_2)

    # -------------------------------------------------------------------------
    # P7_R15: Terminal Ledger Immutability via Clean Block
    # -------------------------------------------------------------------------
    def test_p7_r15_terminal_ledger_immutability(self):
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
        decision.decision_notes = "Tampered notes on NO_GO"
        with pytest.raises(ValidationError, match="Terminal decision records cannot be modified"):
            decision.save()

    # -------------------------------------------------------------------------
    # P7_R16: Audit Log Immutability (Delete / Update Prohibited)
    # -------------------------------------------------------------------------
    def test_p7_r16_audit_log_immutability(self):
        audit = ManagerDecisionAuditLog.objects.create(
            tenant_id=self.tenant_a.id,
            action_type="TEST_IMMUTABILITY",
            actor_id=self.manager.id,
            details={"k": "v"},
        )
        with pytest.raises(ValidationError, match="ManagerDecisionAuditLog records cannot be deleted"):
            audit.delete()

        with pytest.raises(ValidationError, match="ManagerDecisionAuditLog records are strictly immutable"):
            audit.action_type = "TAMPERED_ACTION"
            audit.save()

    # -------------------------------------------------------------------------
    # P7_R17: Cross-Tenant Isolation (Decision Query Fail-Closed)
    # -------------------------------------------------------------------------
    def test_p7_r17_cross_tenant_isolation(self):
        decision = self._create_decision()
        with pytest.raises(ManagerDecisionLedger.DoesNotExist):
            EnterpriseGovernanceService.attach_evidence_snapshot(
                tenant_id=self.tenant_b.id,  # Wrong tenant
                decision_id=decision.id,
                domain="SECURITY",
                evidence_payload={},
                certified_by_id=self.initiator.id,
            )

    # -------------------------------------------------------------------------
    # P7_R18: Decision Version Increments for Same Candidate
    # -------------------------------------------------------------------------
    def test_p7_r18_decision_version_increments(self):
        dec_v1 = self._create_decision()
        assert dec_v1.decision_version == 1

        dec_v2 = self._create_decision()
        assert dec_v2.decision_version == 2

    # -------------------------------------------------------------------------
    # P7_R19: Activation Window Violation Denies Token Consumption
    # -------------------------------------------------------------------------
    def test_p7_r19_activation_window_violation(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)

        now = timezone.now()
        # Activation window in future
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

    # -------------------------------------------------------------------------
    # P7_R20: Complete Audit Event Trail
    # -------------------------------------------------------------------------
    def test_p7_r20_complete_audit_event_trail(self):
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

        actions = list(ManagerDecisionAuditLog.objects.filter(decision=decision).values_list("action_type", flat=True))
        assert "DECISION_CREATED" in actions
        assert "EVIDENCE_SNAPSHOT_ATTACHED" in actions
        assert "MANAGER_DETERMINATION_GO" in actions
        assert "TOKEN_ISSUED" in actions
        assert "TOKEN_CONSUMED_SYNTHETIC" in actions
