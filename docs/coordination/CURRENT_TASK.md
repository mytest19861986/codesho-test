# Current Task: SPRINT1-GUARDIAN-RECOVERY-DECISION-GATE-66D

- Owner: Codex
- Status: `BLOCKED_PENDING_EMPLOYER_LEGAL_DECISION`.
- BASE_SHA: `5ef6323a42739613b05eab1fcbb07e009a87e859`.
- Target: `codesho-test` branch `codex/task66d-guardian-recovery-decision-gate`.
- Scope: a decision package only at
  `docs/decisions/2026-07-26-guardian-recovery-boundary-gate.md`; no decision
  is made on behalf of Employer or Legal.
- Current deliverable: define the Guardian/Recovery boundary, open decisions,
  selectable owner responses, and a proposed-but-not-authorized smallest
  foundation slice.
- Required gate: self-review plus one sequential Claude document review;
  findings may be resolved only in the two-file allow-list. If no complete
  Claude response is received after the required response cycle,
  `NOT_CLAUDE_VERIFIED` must be reported to Commander; merge remains blocked.
- Commit/push/draft PR: authorized only to `codesho-test` after the allowed
  review and final two-file diff checks. Merge is not authorized.
- Restrictions: no model, migration, endpoint, OpenAPI, code, test,
  configuration, public UI, provider, notification, Signup, OAuth,
  Onboarding, deployment, Alpha/Production activation, or protected `codesho`
  promotion.
