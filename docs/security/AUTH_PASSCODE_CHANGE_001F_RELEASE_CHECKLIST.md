# AUTH-PASSCODE-CHANGE-001F release readiness

Status: test-only release gate in progress; no Production behavior is enabled.

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
