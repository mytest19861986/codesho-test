# AUTH-PASSCODE-CHANGE-001F handoff

Status: Review 02 passed; ready for final local gates and scoped checkpoint.
Scope is test-only E2E evidence and release-readiness documentation. No
Production scheduling, UI, Alpha activation, release or protected-repository
promotion is authorized.

## Review 02 disposition

- Prompt: `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02_V1`
- Verdict: `PASS`
- P0/P1: none.
- P2 findings: the completion checkpoint does not assert a total-row delta;
  SameSite is not asserted; and including bare `v1` in forbidden values is
  low-signal and potentially fragile. These are non-blocking evidence-quality
  notes and require no production or out-of-scope change.
- Review scope was limited to the E2E test, this handoff, and the release
  checklist. No raw secrets or passcodes were included in the review result or
  committed evidence.

## Final gate state

- Ruff: passed.
- Focused E2E: `2 skipped` because local PostgreSQL is unavailable; the test's
  PostgreSQL guard is the only skip path and Redis `PING` is unconditional once
  PostgreSQL is active.
- Full backend suite: `130 passed, 29 skipped`.
- `git diff --check`: passed.
- No protected `codesho` promotion, UI work, Production behavior, or Alpha
  user activation was performed.

## CI remediation follow-up

- Initial exact-SHA CI backend run exposed a test-only routing defect: the
  randomized tenant slug was created correctly, but helper requests still used
  a hardcoded host and returned 404 in PostgreSQL CI.
- Remediation: `_csrf`, `_login`, session checks, completion, replay, and
  re-login requests now use `alpha_host = f"{tenant.slug}.localhost"`.
  The cross-tenant request remains `f"{second_tenant.slug}.localhost"` and is
  followed by a successful Alpha completion.
- Follow-up prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02A_V1`.
- Follow-up verdict: `PASS`; P0/P1: none; no new P2 or out-of-scope finding.

- CI exact-SHA `9852f09` still showed only the issuance row through the scoped
  tenant+subject filter. The helper now selects all rows for the unique tenant
  and fail-closed asserts every row belongs to the expected subject user,
  preserving tenant isolation while exposing any producer subject mismatch.
- Follow-up prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02D_V1`.
- Follow-up verdict: `PASS`; P0/P1: none. One new non-blocking P2 notes the
  deliberate fail-loud tradeoff if a future second user is added to this unique
  tenant; no out-of-scope change is implicated.

- CI exact-SHA `7d263b9` still showed missing completion/rejection counts. A
  test-only aggregate event-type diagnostic was added to failure messages; it
  emits categories and counts only, never identifiers or sensitive values.
- Follow-up prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02F_V1`.
- Follow-up verdict: `PASS`; P0/P1: none. One non-blocking P2 notes that the
  diagnostic aggregate is global and could be noisy under parallel tests.

## Release checkpoint

- Final implementation checkpoint before this documentation update:
  `b2d7217`.
- CI exact-SHA run `29737743438`: success.
- Compose smoke/restore exact-SHA run `29737743350`: success.
- CI: https://github.com/mytest19861986/codesho-test/actions/runs/29737743438
- Compose: https://github.com/mytest19861986/codesho-test/actions/runs/29737743350
- Local final gates: Ruff passed; focused E2E `2 skipped` only because local
  PostgreSQL is unavailable; full backend `130 passed, 29 skipped`; staged
  `git diff --check` passed.
- Only the E2E test, this handoff, and the release checklist were committed;
  unrelated coordination changes remain untouched.

- CI exact-SHA `be73ab5` showed the schema-qualified evidence read only the
  issuance baseline; completion and rejection events were not visible through
  the reused Django connection snapshot.
- Remediation: `_audit_rows` closes the connection before opening its fresh,
  parameterized evidence cursor. All call sites are outside `tenant_atomic`
  blocks, so no active transaction is discarded.
- Follow-up prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02C_V1`.
- Follow-up verdict: `PASS`; P0/P1: none; no new P2 or out-of-scope finding.

- CI exact-SHA `f9de519` then exposed a second test-only issue: ORM access to
  the schema-qualified audit model resolved the relation incorrectly in the CI
  test database (`relation "audit.identity_security_event" does not exist`).
- Remediation: `_audit_rows` now uses a parameterized, explicit
  `FROM audit.identity_security_event` query and reconstructs the same ten
  bounded columns with strict shape checking. No production code changed.
- Follow-up prompt:
  `CLAUDE_AUTH_PASSCODE_CHANGE_001F1_END_TO_END_RELEASE_REVIEW_02B_V1`.
- Follow-up verdict: `PASS`; P0/P1: none; no new P2 or out-of-scope finding.
