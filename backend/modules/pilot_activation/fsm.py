"""
Finite State Machine for Phase 9 Controlled Activation Readiness Rehearsal.
Enforces all 15 states, legal transitions, and fail-closed security invariants.
"""

from typing import Dict, Set, Tuple
from .domain import ActivationState

LEGAL_TRANSITIONS: Dict[ActivationState, Set[ActivationState]] = {
    ActivationState.DRAFT: {ActivationState.PRECHECK_PENDING, ActivationState.FAILED_CLOSED},
    ActivationState.PRECHECK_PENDING: {ActivationState.MANAGER_DECISION_REQUIRED, ActivationState.FAILED_CLOSED},
    ActivationState.MANAGER_DECISION_REQUIRED: {ActivationState.SCOPE_LOCKED, ActivationState.FAILED_CLOSED},
    ActivationState.SCOPE_LOCKED: {ActivationState.AUTHORIZATION_READY, ActivationState.FAILED_CLOSED},
    ActivationState.AUTHORIZATION_READY: {ActivationState.ACTIVATION_READY, ActivationState.FAILED_CLOSED},
    ActivationState.ACTIVATION_READY: {ActivationState.ACTIVATING, ActivationState.FAILED_CLOSED},
    ActivationState.ACTIVATING: {ActivationState.ACTIVE_SYNTHETIC, ActivationState.FAILED_CLOSED, ActivationState.ROLLING_BACK},
    ActivationState.ACTIVE_SYNTHETIC: {ActivationState.PAUSED, ActivationState.STOPPING, ActivationState.ROLLING_BACK, ActivationState.EMERGENCY_ABORTED, ActivationState.FAILED_CLOSED},
    ActivationState.PAUSED: {ActivationState.ACTIVE_SYNTHETIC, ActivationState.STOPPING, ActivationState.ROLLING_BACK, ActivationState.EMERGENCY_ABORTED, ActivationState.FAILED_CLOSED},
    ActivationState.STOPPING: {ActivationState.STOPPED, ActivationState.FAILED_CLOSED},
    ActivationState.STOPPED: {ActivationState.ROLLING_BACK, ActivationState.FAILED_CLOSED},
    ActivationState.ROLLING_BACK: {ActivationState.ROLLED_BACK, ActivationState.FAILED_CLOSED},
    ActivationState.ROLLED_BACK: {ActivationState.FAILED_CLOSED},
    ActivationState.EMERGENCY_ABORTED: {ActivationState.FAILED_CLOSED},
    ActivationState.FAILED_CLOSED: set()
}

class ActivationFSM:
    def __init__(self, initial_state: ActivationState = ActivationState.DRAFT):
        self._state = initial_state

    @property
    def current_state(self) -> ActivationState:
        return self._state

    def can_transition(self, target_state: ActivationState) -> bool:
        if target_state == ActivationState.EMERGENCY_ABORTED:
            return True
        if target_state == ActivationState.FAILED_CLOSED:
            return True
        return target_state in LEGAL_TRANSITIONS.get(self._state, set())

    def transition(self, target_state: ActivationState) -> Tuple[bool, str]:
        if not self.can_transition(target_state):
            return False, f"ILLEGAL_TRANSITION: Cannot transition from {self._state.value} to {target_state.value}"
        self._state = target_state
        return True, "TRANSITION_SUCCESS"
