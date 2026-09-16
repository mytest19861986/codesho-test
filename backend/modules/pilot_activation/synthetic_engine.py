"""
Synthetic Activation Engine coordinating FSM, Tokens, Scope Lock, and Audit.
Enforces all operational commands: Activate, Pause, Resume, Stop, Rollback, Emergency Abort.
"""

from typing import Dict, Any, Tuple, Optional
import uuid
from .domain import ActivationState, RehearsalScope, ActivationToken, DataClassification
from .fsm import ActivationFSM
from .tokens import TokenService
from .scope_lock import ScopeLockService
from .audit import AuditLedgerService

class SyntheticActivationEngine:
    def __init__(self, tenant_id: str, scope: RehearsalScope):
        self.tenant_id = tenant_id
        self.scope = scope
        self.fsm = ActivationFSM()
        self.tokens = TokenService()
        self.audit = AuditLedgerService()
        self.active_token: Optional[ActivationToken] = None
        self.locked_digest: Optional[str] = None
        self.active_synthetic_entities: Dict[str, Any] = {}

    def run_precheck(self, actor: str) -> Tuple[bool, str]:
        # 1. State check
        if self.fsm.current_state != ActivationState.DRAFT:
            return False, "INVALID_STATE_FOR_PRECHECK"

        # 2. Data classification check
        ok, reason = ScopeLockService.validate_data_admission(self.scope)
        if not ok:
            self.fsm.transition(ActivationState.FAILED_CLOSED)
            self.audit.record_event(actor, self.tenant_id, "PRECHECK", ActivationState.DRAFT, ActivationState.FAILED_CLOSED, "", "FAILED", failure_reason=reason)
            return False, reason

        self.fsm.transition(ActivationState.PRECHECK_PENDING)
        self.fsm.transition(ActivationState.MANAGER_DECISION_REQUIRED)
        self.audit.record_event(actor, self.tenant_id, "PRECHECK", ActivationState.DRAFT, ActivationState.MANAGER_DECISION_REQUIRED, "", "SUCCESS")
        return True, "PRECHECK_PASSED"

    def apply_manager_decision(self, actor: str, decision: str, decision_ref: str) -> Tuple[bool, str]:
        if self.fsm.current_state != ActivationState.MANAGER_DECISION_REQUIRED:
            return False, "INVALID_STATE_FOR_DECISION"

        if decision != "GO":
            self.fsm.transition(ActivationState.FAILED_CLOSED)
            self.audit.record_event(actor, self.tenant_id, "MANAGER_DECISION", ActivationState.MANAGER_DECISION_REQUIRED, ActivationState.FAILED_CLOSED, "", "DENIED", failure_reason=f"DECISION_{decision}")
            return False, f"DECISION_{decision}"

        # Freeze scope lock
        self.locked_digest = ScopeLockService.calculate_digest(self.scope)
        self.fsm.transition(ActivationState.SCOPE_LOCKED)
        self.audit.record_event(actor, self.tenant_id, "SCOPE_LOCK", ActivationState.MANAGER_DECISION_REQUIRED, ActivationState.SCOPE_LOCKED, self.locked_digest, "SUCCESS")

        # Mint authority token
        token = self.tokens.generate_token(self.scope, decision_ref)
        self.active_token = token
        self.fsm.transition(ActivationState.AUTHORIZATION_READY)
        self.fsm.transition(ActivationState.ACTIVATION_READY)
        self.audit.record_event(actor, self.tenant_id, "AUTHORIZATION_ISSUED", ActivationState.SCOPE_LOCKED, ActivationState.ACTIVATION_READY, self.locked_digest, "SUCCESS", token_id=token.token_id)
        return True, "AUTHORIZATION_READY"

    def activate(self, actor: str, token: ActivationToken, active_tenant_context: str) -> Tuple[bool, str]:
        src = self.fsm.current_state
        if src != ActivationState.ACTIVATION_READY:
            if src == ActivationState.ACTIVE_SYNTHETIC:
                return True, "IDEMPOTENT_ALREADY_ACTIVE"
            return False, f"INVALID_STATE_FOR_ACTIVATION: {src.value}"

        # Validate token
        valid, reason = self.tokens.validate_token(token, active_tenant_context, self.scope)
        if not valid:
            self.audit.record_event(actor, active_tenant_context, "ACTIVATE", src, src, self.locked_digest or "", "DENIED", token_id=token.token_id, failure_reason=reason)
            return False, reason

        # Scope drift check
        intact, drift_reason = ScopeLockService.verify_no_scope_drift(self.locked_digest or "", self.scope)
        if not intact:
            self.fsm.transition(ActivationState.FAILED_CLOSED)
            self.audit.record_event(actor, active_tenant_context, "ACTIVATE", src, ActivationState.FAILED_CLOSED, self.locked_digest or "", "DENIED", token_id=token.token_id, failure_reason=drift_reason)
            return False, drift_reason

        # Consume token nonce
        self.tokens.consume_nonce(token)

        # Transition into activating then active
        self.fsm.transition(ActivationState.ACTIVATING)
        self.fsm.transition(ActivationState.ACTIVE_SYNTHETIC)
        self.active_synthetic_entities["active_cycle_id"] = str(uuid.uuid4())
        self.audit.record_event(actor, active_tenant_context, "ACTIVATE", src, ActivationState.ACTIVE_SYNTHETIC, self.locked_digest or "", "SUCCESS", token_id=token.token_id)
        return True, "ACTIVE_SYNTHETIC"

    def pause(self, actor: str, reason: str) -> Tuple[bool, str]:
        src = self.fsm.current_state
        if src != ActivationState.ACTIVE_SYNTHETIC:
            return False, f"INVALID_STATE_FOR_PAUSE: {src.value}"

        self.fsm.transition(ActivationState.PAUSED)
        self.audit.record_event(actor, self.tenant_id, "PAUSE", src, ActivationState.PAUSED, self.locked_digest or "", "SUCCESS", token_id=self.active_token.token_id if self.active_token else None, failure_reason=reason)
        return True, "PAUSED"

    def resume(self, actor: str, token: ActivationToken, active_tenant_context: str) -> Tuple[bool, str]:
        src = self.fsm.current_state
        if src != ActivationState.PAUSED:
            return False, f"INVALID_STATE_FOR_RESUME: {src.value}"

        if not token or token.revoked:
            return False, "UNAUTHORIZED_RESUME"

        if token.tenant_id != active_tenant_context:
            return False, "WRONG_TENANT_RESUME"

        self.fsm.transition(ActivationState.ACTIVE_SYNTHETIC)
        self.audit.record_event(actor, active_tenant_context, "RESUME", src, ActivationState.ACTIVE_SYNTHETIC, self.locked_digest or "", "SUCCESS", token_id=token.token_id)
        return True, "ACTIVE_SYNTHETIC"

    def stop(self, actor: str) -> Tuple[bool, str]:
        src = self.fsm.current_state
        if src not in [ActivationState.ACTIVE_SYNTHETIC, ActivationState.PAUSED]:
            if src == ActivationState.STOPPED:
                return True, "IDEMPOTENT_ALREADY_STOPPED"
            return False, f"INVALID_STATE_FOR_STOP: {src.value}"

        self.fsm.transition(ActivationState.STOPPING)
        self.fsm.transition(ActivationState.STOPPED)
        if self.active_token:
            self.tokens.revoke_token(self.active_token.token_id)
        self.audit.record_event(actor, self.tenant_id, "STOP", src, ActivationState.STOPPED, self.locked_digest or "", "SUCCESS", token_id=self.active_token.token_id if self.active_token else None)
        return True, "STOPPED"

    def rollback(self, actor: str) -> Tuple[bool, str]:
        src = self.fsm.current_state
        if src in [ActivationState.ROLLED_BACK]:
            return True, "IDEMPOTENT_ALREADY_ROLLED_BACK"

        self.fsm.transition(ActivationState.ROLLING_BACK)
        self.active_synthetic_entities.clear()
        if self.active_token:
            self.tokens.revoke_token(self.active_token.token_id)
            self.active_token = None
        self.locked_digest = None
        self.fsm.transition(ActivationState.ROLLED_BACK)
        self.audit.record_event(actor, self.tenant_id, "ROLLBACK", src, ActivationState.ROLLED_BACK, "", "SUCCESS")
        return True, "ROLLED_BACK"

    def emergency_abort(self, actor: str, reason: str) -> Tuple[bool, str]:
        src = self.fsm.current_state
        self.fsm.transition(ActivationState.EMERGENCY_ABORTED)
        self.active_synthetic_entities.clear()
        if self.active_token:
            self.tokens.revoke_token(self.active_token.token_id)
            self.active_token = None
        self.audit.record_event(actor, self.tenant_id, "EMERGENCY_ABORT", src, ActivationState.EMERGENCY_ABORTED, "", "SUCCESS", failure_reason=reason)
        return True, "EMERGENCY_ABORTED"
