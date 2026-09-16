# P9 Authority Token Specification

## 1. Overview & Security Invariants
The Activation Authority Token serves as the cryptographically verifiable and auditable gateway for synthetic execution. It satisfies all 11 required properties from Commander Directive Section 9:
1. `EXPLICIT`: Contains distinct unambiguous identifiers and payload.
2. `SCOPED`: Cryptographically binds the scope digest.
3. `TENANT_BOUND`: Explicitly tied to a single tenant UUID (`app.current_tenant`).
4. `PURPOSE_BOUND`: Restricted to `SYNTHETIC_ACTIVATION_REHEARSAL`.
5. `TIME_BOUND`: Enforces `issued_at` and `expires_at` (fixed bounded lifespan).
6. `AUDITABLE`: Structured for zero-secret audit logging.
7. `REVOCABLE`: Can be revoked immediately via blacklist/status flag.
8. `NON_REPLAYABLE`: Contains a single-use unique `nonce`.
9. `NO_PRODUCTION_PROVIDER`: Evaluated entirely in-engine using standard crypto (HMAC-SHA256).

## 2. Schema Structure
```json
{
  "token_id": "uuid-v4",
  "tenant_id": "uuid-v4",
  "authorized_scope": {
    "tenant_count": 1,
    "max_students": 50,
    "max_duration_days": 14,
    "environment": "SYNTHETIC_TEST",
    "features": ["COURSES", "QUIZZES", "ATTENDANCE"],
    "data_class": "SYNTHETIC_TEST_FIXTURE",
    "payment_mode": "STUB_DISABLED",
    "communication_mode": "STUB_DISABLED"
  },
  "scope_digest": "sha256-hex-digest",
  "issued_at": "ISO-8601 UTC timestamp",
  "expires_at": "ISO-8601 UTC timestamp",
  "purpose": "SYNTHETIC_ACTIVATION_REHEARSAL",
  "decision_reference": "MGR-DEC-SYNTHETIC-20260916-01",
  "nonce": "unique-hex-32",
  "revoked": false,
  "signature": "hmac-sha256(payload, secret)"
}
```

## 3. Negative Token Validation Rules
Any token presenting with the following defects MUST be rejected immediately (`DENY`):
- `MISSING_TOKEN`: Request missing authorization token header/payload -> `DENY (401/403)`
- `INVALID_SIGNATURE`: Cryptographic signature mismatch -> `DENY`
- `EXPIRED_TOKEN`: `current_time > expires_at` -> `DENY`
- `REVOKED_TOKEN`: Token status is revoked -> `DENY`
- `REPLAYED_TOKEN`: Nonce has already been consumed -> `DENY`
- `WRONG_TENANT_TOKEN`: Token `tenant_id` does not match active `app.current_tenant` -> `DENY`
- `WRONG_SCOPE_TOKEN` / `ALTERED_SCOPE_DIGEST`: Recomputed SHA-256 does not match `scope_digest` -> `DENY`
- `WRONG_PURPOSE_TOKEN`: Purpose != `SYNTHETIC_ACTIVATION_REHEARSAL` -> `DENY`
- `STALE_TOKEN`: Pre-activation state elapsed -> `DENY`
