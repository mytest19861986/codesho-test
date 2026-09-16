# P9 Observability and Audit Specification

## 1. Zero-Secret Append-Only Audit Logging
Every state change, token validation, scope lock check, and privileged operation in P9 generates an immutable audit record.

### Audit Ledger Fields:
- `event_id`: Unique UUIDv4.
- `timestamp`: UTC ISO-8601 string.
- `actor`: System/User UUID.
- `tenant_id`: Canonical tenant UUID (`app.current_tenant`).
- `command`: e.g. `ACTIVATE`, `PAUSE`, `RESUME`, `STOP`, `ROLLBACK`, `EMERGENCY_ABORT`.
- `source_state`: FSM state before transition.
- `target_state`: FSM state after transition.
- `scope_digest`: SHA-256 digest of active scope.
- `token_id`: Safe UUID reference (never secret keys or raw signatures).
- `outcome`: `SUCCESS` | `DENIED` | `FAILED`.
- `failure_reason`: Descriptive error code if failed (e.g. `TOKEN_EXPIRED`, `CROSS_TENANT_DENIED`).
- `correlation_id`: Distributed tracing UUID.

## 2. Invariants & Hygiene
1. `APPEND_ONLY`: Logs cannot be updated (`DENY UPDATE`) or deleted (`DENY DELETE`).
2. `AUDIT_WRITE_FAIL_CLOSED`: If an audit event cannot be written, the active business transaction MUST roll back and fail closed.
3. `ZERO_SECRET_LEAKAGE`: Token HMAC secrets, passwords, or session cookies are never written to audit payload.
4. `ZERO_PII`: Synthetic data only; no real phone numbers or national IDs.

## 3. Observability Endpoints & Signals
Exposes structured runtime signals for operators:
- `current_state`: Active FSM state.
- `current_tenant`: Bound `app.current_tenant`.
- `scope_digest`: Current scope hash.
- `last_transition`: Timestamp and actor of last change.
- `health_status`: `HEALTHY` | `DEGRADED` | `ABORTED` | `FAILED_CLOSED`.
