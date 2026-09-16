# P9 Pause, Stop, Rollback, and Emergency Abort Runbook

## 1. Overview of Lifecycle Controls
Phase 9 provides explicit procedures to arrest, terminate, or revert synthetic operations without leaving orphaned resources or context leaks.

## 2. Procedure: PAUSE
- **Trigger**: Planned maintenance, anomaly investigation, or operator pause signal.
- **Behavior**:
  1. Sets state to `PAUSED`.
  2. Disallows any new incoming synthetic task executions.
  3. Preserves all existing in-memory/database state, audit records, and scope lock.
- **Resume Protocol**:
  1. Resume cannot be implicit.
  2. Requires explicit `RESUME` command with valid unexpired token and matching `scope_digest`.
  3. Re-verifies tenant isolation before returning to `ACTIVE_SYNTHETIC`.

## 3. Procedure: CONTROLLED STOP
- **Trigger**: Orderly conclusion of a rehearsal trial cycle.
- **Behavior**:
  1. Sets state to `STOPPING`.
  2. Waits for all active in-flight worker tasks to drain (or timeout within 10s).
  3. Sets state to `STOPPED`.
  4. Retains historical trial logs for audit post-mortem.
  5. Permanently expires active activation token. Cannot resume without a brand new authorization token.

## 4. Procedure: ROLLBACK
- **Trigger**: Detected anomaly, failed test assertion, or rehearsal reset.
- **Behavior**:
  1. Sets state to `ROLLING_BACK`.
  2. Executes reverse compensations for all synthetic trial entities created during the session.
  3. Validates that no cross-tenant entities were touched.
  4. Inactivates all session credentials and tokens.
  5. Verifies post-rollback baseline state (`ACTIVE_SYNTHETIC_STATE: 0`).
  6. Sets state to `ROLLED_BACK`.

## 5. Procedure: EMERGENCY ABORT (Kill-Switch)
- **Trigger**: Security gate trip, unauthorized scope breach attempt, or operator emergency kill-switch.
- **Behavior**:
  1. Immediately cuts off execution: all incoming requests fail closed (`503 / 403`).
  2. Immediately revokes token and blacklists nonce.
  3. Drops active session contexts and triggers incident audit record.
  4. State set to `EMERGENCY_ABORTED`.
  5. Strictly locks system against automated resume. Requires manual reset.
