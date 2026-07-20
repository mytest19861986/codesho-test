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
