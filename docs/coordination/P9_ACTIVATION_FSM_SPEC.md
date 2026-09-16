# P9 Activation FSM Specification

## 1. Overview & States
In accordance with Commander Directive Section 7 (`COMMANDER_P9_EXECUTION_DIRECTIVE`), the Synthetic Activation Finite State Machine enforces rigorous lifecycle transitions without permitting any unauthenticated or unauthorized skips.

### Minimum Defined FSM States:
1. `DRAFT`: Initial draft definition of rehearsal parameters.
2. `PRECHECK_PENDING`: Environment, RLS context, and synthetic fixtures validation.
3. `MANAGER_DECISION_REQUIRED`: Formal pause point representing manager governance gate (in P9 rehearsal, synthetic mock decision).
4. `SCOPE_LOCKED`: Immutable digest frozen across tenants, features, data classes, and bounds.
5. `AUTHORIZATION_READY`: Activation token created and cryptographically signed.
6. `ACTIVATION_READY`: All 9 pre-activation gates verified PASS.
7. `ACTIVATING`: In-flight transactional activation sequence.
8. `ACTIVE_SYNTHETIC`: Fully operational synthetic trial environment.
9. `PAUSED`: Temporarily suspended workload; new work denied; audit and state preserved.
10: `STOPPING`: Controlled draining of inflight synthetic tasks.
11. `STOPPED`: Orderly completed run; historical data retained for evaluation.
12. `ROLLING_BACK`: Active atomic reversal and data compensation.
13. `ROLLED_BACK`: Reverted clean baseline; authority permanently invalidated.
14. `EMERGENCY_ABORTED`: Immediate fail-closed kill-switch execution.
15. `FAILED_CLOSED`: Safe fallback terminal state upon unhandled anomaly or audit failure.

## 2. Transition Rules & Preconditions
| Source State | Target State | Authorized Actor | Preconditions | Audit Event |
|---|---|---|---|---|
| `DRAFT` | `PRECHECK_PENDING` | `SYSTEM / OPERATOR` | Scope parameters defined | `P9_FSM_PRECHECK_INITIATED` |
| `PRECHECK_PENDING` | `MANAGER_DECISION_REQUIRED` | `SYSTEM` | Precheck tests 100% pass | `P9_FSM_PRECHECK_PASSED` |
| `MANAGER_DECISION_REQUIRED` | `SCOPE_LOCKED` | `MOCK_MANAGER` | Valid Decision (`GO`), Scope frozen | `P9_FSM_SCOPE_LOCKED` |
| `SCOPE_LOCKED` | `AUTHORIZATION_READY` | `TOKEN_ISSUER` | Authority token minted with matching scope digest | `P9_FSM_TOKEN_ISSUED` |
| `AUTHORIZATION_READY` | `ACTIVATION_READY` | `SYSTEM` | Token valid, unrevoked, unexpired | `P9_FSM_READY_VERIFIED` |
| `ACTIVATION_READY` | `ACTIVATING` | `ACTIVATOR` | Atomic transaction opened, RLS set to `app.current_tenant` | `P9_FSM_ACTIVATION_STARTED` |
| `ACTIVATING` | `ACTIVE_SYNTHETIC` | `SYSTEM` | All transactional checks pass | `P9_FSM_ACTIVATED` |
| `ACTIVE_SYNTHETIC` | `PAUSED` | `OPERATOR / SYSTEM` | Valid pause reason | `P9_FSM_PAUSED` |
| `PAUSED` | `ACTIVE_SYNTHETIC` | `OPERATOR` | Valid resume token & scope re-verification | `P9_FSM_RESUMED` |
| `ACTIVE_SYNTHETIC` | `STOPPING` | `OPERATOR` | Orderly stop signal | `P9_FSM_STOPPING` |
| `STOPPING` | `STOPPED` | `SYSTEM` | Inflight tasks drained | `P9_FSM_STOPPED` |
| `ACTIVE_SYNTHETIC` | `ROLLING_BACK` | `OPERATOR / EMERGENCY` | Rollback authorized | `P9_FSM_ROLLBACK_STARTED` |
| `ROLLING_BACK` | `ROLLED_BACK` | `SYSTEM` | Data compensation verified, token invalidated | `P9_FSM_ROLLED_BACK` |
| `ANY_STATE` | `EMERGENCY_ABORTED` | `KILL_SWITCH / ANY` | Abort trigger fired | `P9_FSM_EMERGENCY_ABORTED` |
| `ANY_STATE` | `FAILED_CLOSED` | `SYSTEM` | Unrecoverable error or audit write failure | `P9_FSM_FAILED_CLOSED` |

## 3. Explicitly Forbidden Transitions (Deny Matrix)
- `DRAFT` -> `ACTIVE_SYNTHETIC` (DENIED: Precheck, Manager Decision & Token missing)
- `MANAGER_DECISION_REQUIRED` -> `ACTIVE_SYNTHETIC` (DENIED: Cannot skip Scope Lock & Token)
- `PAUSED` -> `ACTIVE_SYNTHETIC` without valid unrevoked authority (DENIED)
- `STOPPED` -> `ACTIVE_SYNTHETIC` without full new authorization cycle (DENIED)
- `ROLLED_BACK` -> `ACTIVE_SYNTHETIC` without full new authorization cycle (DENIED)
- `EMERGENCY_ABORTED` -> `ACTIVE_SYNTHETIC` (DENIED: Terminal; no automatic resume)
- `FAILED_CLOSED` -> `ACTIVE_SYNTHETIC` without formal recovery protocol (DENIED)
