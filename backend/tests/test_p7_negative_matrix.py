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
    Negative Security Matrix and Strict Boundary Enforcement (N7-01 to N7-40)
    Validating GLM Gates F1-F6 and Absolute Prohibitions.
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

    def _create_decision(self, tenant_id=None, creator_id=None):
        return EnterpriseGovernanceService.create_manager_decision(
            tenant_id=tenant_id or self.tenant_a.id,
            candidate_id=self.candidate_id,
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

    # N7-01: Self-approval attempt by manager rejected
    def test_n7_01_self_approval_rejected(self):
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

    # N7-02: Non-human manager determination rejected (GLM Gate)
    def test_n7_02_non_human_manager_determination_rejected(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        with pytest.raises(ValidationError, match="Automated agents/applications are forbidden"):
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

    # N7-03: Invalid determination state rejected
    def test_n7_03_invalid_determination_state_rejected(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        with pytest.raises(ValidationError, match="INVALID_DETERMINATION"):
            EnterpriseGovernanceService.issue_manager_determination(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                determination=ManagerDecisionState.DRAFT,  # Invalid determination
                manager_user_id=self.manager.id,
                is_human_manager=True,
                operator_ids=[self.initiator.id],
                activation_window_start=now,
                activation_window_end=now + timedelta(hours=1),
                token_expiry=now + timedelta(hours=1),
            )

    # N7-04: Cannot issue token if determination is NO_GO
    def test_n7_04_cannot_issue_token_on_no_go(self):
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
        with pytest.raises(ValidationError, match="Decision is not in authorized GO state"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.initiator.id,
            )

    # N7-05: Cannot issue token if determination is DEFER
    def test_n7_05_cannot_issue_token_on_defer(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.DEFER,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],
            activation_window_start=now,
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        with pytest.raises(ValidationError, match="Decision is not in authorized GO state"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.initiator.id,
            )

    # N7-06: Operator not in authorized list cannot receive token
    def test_n7_06_unauthorized_operator_token_issuance_rejected(self):
        decision = self._create_decision()
        self._attach_fresh_evidence(decision)
        now = timezone.now()
        EnterpriseGovernanceService.issue_manager_determination(
            tenant_id=self.tenant_a.id,
            decision_id=decision.id,
            determination=ManagerDecisionState.GO,
            manager_user_id=self.manager.id,
            is_human_manager=True,
            operator_ids=[self.initiator.id],  # Only initiator authorized
            activation_window_start=now,
            activation_window_end=now + timedelta(hours=1),
            token_expiry=now + timedelta(hours=1),
        )
        with pytest.raises(ValidationError, match="Operator is not in authorized operators list"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.unprivileged_user.id,
            )

    # N7-07: Cannot issue token after decision token expiry
    def test_n7_07_token_issuance_after_decision_expiry_rejected(self):
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
            activation_window_end=now - timedelta(hours=1),
            token_expiry=now - timedelta(seconds=1),
        )
        with pytest.raises(ValidationError, match="Decision token past expiry timestamp"):
            EnterpriseGovernanceService.issue_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                decision_id=decision.id,
                operator_id=self.initiator.id,
            )

    # N7-08: Token replay attack blocked
    def test_n7_08_token_replay_blocked(self):
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
        # 2nd consume REPLAY BLOCKED
        with pytest.raises(ValidationError, match="TOKEN_REPLAY"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-09: Token transfer across operators blocked
    def test_n7_09_token_transfer_blocked(self):
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

    # N7-10: Token consumed after manager revocation blocked
    def test_n7_10_token_consumed_after_revocation_blocked(self):
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
            reason="Emergency test stop",
        )
        with pytest.raises(ValidationError, match="TOKEN_USED_AFTER_REVOCATION"):
            EnterpriseGovernanceService.consume_synthetic_activation_token(
                tenant_id=self.tenant_a.id,
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )

    # N7-11: Token consumed outside activation window blocked
    def test_n7_11_token_consumed_outside_window_blocked(self):
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

    # N7-12: Audit log record cannot be deleted (GLM F1 & F2)
    def test_n7_12_audit_log_deletion_prohibited(self):
        audit = ManagerDecisionAuditLog.objects.create(
            tenant_id=self.tenant_a.id,
            actor_id=self.manager.id,
            action_type="TEST_NEG_AUDIT",
            details={"k": "v"},
        )
        with pytest.raises(ValidationError, match="ManagerDecisionAuditLog records cannot be deleted"):
            audit.delete()

    # N7-13: Audit log record cannot be updated (GLM F1 & F2)
    def test_n7_13_audit_log_update_prohibited(self):
        audit = ManagerDecisionAuditLog.objects.create(
            tenant_id=self.tenant_a.id,
            actor_id=self.manager.id,
            action_type="TEST_NEG_AUDIT_UPDATE",
            details={"k": "v"},
        )
        audit.action_type = "TAMPERED_ACTION"
        with pytest.raises(ValidationError, match="ManagerDecisionAuditLog records are strictly immutable"):
            audit.save()

    # N7-14: Terminal Ledger record cannot be modified (GLM F1 & Immutability)
    def test_n7_14_terminal_ledger_record_cannot_be_modified(self):
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
        decision.decision_notes = "Malicious update after NO_GO"
        with pytest.raises(ValidationError, match="Terminal decision records cannot be modified"):
            decision.save()

    # N7-15: Cross-tenant token consumption blocked
    def test_n7_15_cross_tenant_token_consumption_blocked(self):
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
                tenant_id=self.tenant_b.id,  # Wrong tenant
                token_value=token.token_value,
                operator_id=self.initiator.id,
                submitted_scope_hash=self.scope_hash,
                submitted_rc_id=self.rc_id,
            )
