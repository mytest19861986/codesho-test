# Task71A Synthetic Account Bootstrap Architecture Review Summary

Status: `IN_PROGRESS / REMEDIATION_REQUIRED / REVIEW_GATES_PENDING`

Task: `SPRINT1-SYNTHETIC-ACCOUNT-BOOTSTRAP-ARCHITECTURE-71A`
Repository: `mytest19861986/codesho-test`
Base: `bdc2839bb03e829064066496739d47c7cbb05c07`
Branch: `agent/task71a-synthetic-account-bootstrap-architecture`

## Scope

This review covers exactly the five Task71A allow-listed documentation files:

```text
docs/decisions/2026-07-26-synthetic-account-bootstrap-boundary.md
docs/coordination/CODEX_TO_COMMANDER.md
docs/coordination/CURRENT_TASK.md
docs/coordination/PROJECT_STATE.md
docs/reviews/s1-071a-synthetic-account-bootstrap-architecture-review-summary.md
```

No source code, model, migration, API, OpenAPI, frontend, configuration, test,
account, membership, credential, or runtime behavior is in scope.

## Self-review checklist

- [x] AdultAgeAttestation → SyntheticBootstrapRequest → User →
      TenantMembership → Dormant/Initial Credential State is defined.
- [x] Username/email alternatives are compared without inventing contact or
      identity data; Option B placeholder fields are rejected.
- [x] Dormant User and membership are authorization-disabled and fail closed
      until a separately authorized activation and credential task.
- [x] Security, privacy, cost, time, and extensibility trade-offs are recorded.
- [x] Atomicity, idempotency, replay, and concurrent duplicate handling are
      specified.
- [x] Same-tenant opaque linkage, RLS fail-closed behavior, invalid provenance,
      duplicate attestation, and one-account maximum are specified.
- [x] No raw passcode, credential, token, cookie, or secret is produced.
- [x] API/OpenAPI/frontend/signup/runtime behavior remain excluded.
- [x] Legal retention, deletion, erasure, and hold decisions remain
      `LEGAL_PENDING`.
- [x] Future migration/rollback plan, test matrix, and proposed Task71B
      allow-list are included and clearly non-authorizing.

## Review disposition

Required independent reviews are sequential: security, privacy, and
database/RLS/provider-neutral architecture review. The first review returned
`FAIL` with blocking findings `71A-SEC-01` (dormant lifecycle needed an
explicit authorization-disabled fail-closed invariant) and `71A-DOC-01`
(historical Task69B gates and Draft PR state were unclear). This revision
addresses both findings within the exact five-file allow-list. Raw prompts and
responses remain outside the repository. Re-review V2 disposed `71A-SEC-01`
and `71A-DOC-01` as PASS, but found blocking `71A-DOC-02`: the Commander
checkpoint still named the prior V1 head. This remediation updates that
checkpoint to the live PR #11 head; the final verdict remains pending until
the new head is independently re-reviewed.

## Verification evidence

```text
ALLOW-LIST: EXACTLY 5 FILES REQUIRED
CODE/MIGRATION/API/CONFIG CHANGE: FORBIDDEN
GIT DIFF --CHECK: REQUIRED AND MUST BE RECORDED ON FINAL HEAD
CI backend/frontend/smoke_restore: REQUIRED
```

The local environment is not evidence for backend/frontend/smoke_restore CI;
the required provider-neutral CI must run on the final Task71A head.
