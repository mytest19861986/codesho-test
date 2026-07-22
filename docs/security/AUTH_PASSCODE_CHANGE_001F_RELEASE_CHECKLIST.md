# AUTH-PASSCODE-CHANGE-001F release readiness

Status: Claude verification debt cleared; documentation checkpoint recorded; no Production behavior is enabled.

## Review 02

- Prompt: `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02_V1`
- Verdict: `PASS`; P0/P1 findings: none.
- Non-blocking P2 notes are recorded in the handoff: completion total-row
  delta, SameSite assertion, and low-signal `v1` forbidden-value check.
- Review was limited to the E2E test, handoff, and this checklist.

## CI remediation

- Initial CI backend failure was `404` from the CSRF helper because the test
  generated a randomized tenant slug but used a hardcoded Alpha host.
- Fixed within the E2E test by threading the actual tenant-derived host through
  all Alpha-side requests; the cross-tenant negative path remains unchanged.
- Review 02A prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02A_V1`.
- Review 02A verdict: `PASS`; P0/P1: none; no new P2 findings.

- CI exact-SHA `f9de519` also exposed an ORM schema-resolution failure in the
  E2E evidence helper. The test now uses a parameterized schema-qualified SQL
  query; this remains test-only and preserves the same bounded shape.
- Review 02B prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02B_V1`.
- Review 02B verdict: `PASS`; P0/P1: none; no new P2 findings.

- CI exact-SHA `be73ab5` exposed stale connection visibility in the test-only
  audit evidence read. The helper now closes and reopens the connection before
  querying, without changing production behavior or evidence shape.
- Review 02C prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02C_V1`.
- Review 02C verdict: `PASS`; P0/P1: none; no new P2 findings.

- CI exact-SHA `9852f09` continued to show an audit visibility mismatch under
  the tenant+subject filter. The helper now reads the unique tenant's rows and
  asserts the expected subject explicitly, making any mismatch fail closed.
- Review 02D prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02D_V1`.
- Review 02D verdict: `PASS`; P0/P1: none; one non-blocking P2 reliability
  note about the deliberate fail-loud behavior for a future second user.

- CI exact-SHA `7d263b9` still lacked completion/rejection counts. A bounded
  aggregate event-type diagnostic was added to failure messages without any
  sensitive fields.
- Review 02F prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02F_V1`.
- Review 02F verdict: `PASS`; P0/P1: none; one non-blocking P2 diagnostic
  quality note about global counts under parallel execution.

## Exact-SHA checkpoint

- Implementation SHA: `b2d7217`.
- CI run `29737743438`: success.
- Compose smoke/restore run `29737743350`: success.
- Local: Ruff passed; focused E2E `2 skipped` for unavailable local
  PostgreSQL; full backend `130 passed, 29 skipped`; diff check passed.

## Backend flow evidence

The PostgreSQL/Redis-only HTTP gate exercises mandatory-change login, secure
challenge-cookie issuance, completion without a session, epoch/version advance,
digest nulling, prior-session rejection, fresh-login session creation, replay
rejection, and normal old/new credential behavior. Local SQLite may skip this
gate; CI and Compose must execute it without a skip before this checkpoint is
closed. Canonical OpenAPI status/cookie contracts remain the release authority.

## Explicit remaining gates

- Production TLS and `__Host-` deployment proof are still required.
- Legal must review the 30-day terminal-metadata retention policy.
- Production cleanup scheduling remains disabled.
- Login/passcode-change UI is not authorized.
- Real Alpha users remain blocked.
- Signup, Recovery, Guardian, OAuth and Onboarding remain deferred.
- Promotion to protected `codesho` remains forbidden.

## Audit producer remediation 01

- Root cause remediation is limited to the forward-only platform-event migration
  `0008_harden_audit_append_result`, which makes the append function's inserted
  row result explicit with `RETURNING` and preserves idempotent no-op behavior.
- Local Ruff, Django check, migration drift check, full backend tests, and diff
  check pass; PostgreSQL/Redis HTTP evidence remains a CI/Compose gate.

## Review 03 follow-up — audit append return-value hardening

- Prompt: `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_AUDIT_PRODUCER_REVIEW_03_V1`
- Verdict: `PASS`; P0/P1/P2 findings: none.
- Verified `inserted boolean := false` plus `RETURN COALESCE(inserted, false)` gives a strict two-valued return contract: true only for a newly inserted row and false on idempotency conflict.
- Verified `SECURITY DEFINER`, hardened `search_path`, unchanged function signature, conflict behavior, forward-only migration, dependency, and irreversible reverse operation.
- No out-of-scope changes were implicated.

## Review 04 — Mock lifecycle verification

- Prompt: `CLAUDE_AUTH_PASSCODE_CHANGE_001F2_MOCK_LIFECYCLE_REVIEW_01_V1`.
- Review base: `03eb63071e77e40d275eb2634b38eac55c212b56`.
- Reviewed patch commit: `ac721b4937e70dc5aa8682f37390472d468b53e0`.
- Verdict: `APPROVE`; P0: none; P1: none.
- P2: low-risk note that `join(timeout=20)` is bounded and is not completion proof by itself; the following `all(not thread.is_alive())` assertion is the compensating control.
- Acceptance matrix: PASS for parent-scope activation before both starts, coverage through both joins, restoration on normal/exceptional exits, no E2E mock leakage, and unchanged concurrency semantics/assertions.
- Evidence: ordered repetitions `18/18`; backend suite `164 passed`; CI `29917920277` success; Compose `29917920268` success.
- Marker: `CLAUDE_VERIFICATION_DEBT_CLEARED_PENDING_DOC_CHECKPOINT`.
- No automatic remediation was performed. Production code, tests, workflow, dependency, and migration were not changed by this documentation checkpoint. This checkpoint does not authorize promotion to protected `codesho`.
