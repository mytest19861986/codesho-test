# Current Task: SPRINT1-REAL-USER-ONBOARDING-LEGAL-AND-BOUNDARY-DECISION-72B

- Owner: Codex, directed by Commander AI.
- Status: `COMPLETE / DOCS-ONLY / OPTION-A / CLAUDE-PASS`.
- Base branch: `origin/main`.
- Base SHA: `0472239d06194875d1cdb6f6929dd8eaad8bc0d9`.
- Branch: `codex/task72b-real-user-legal-policy-packet`.

## Goal

Create the legal/policy packet and preimplementation gate for future real-user
onboarding. Task72A selected Option A; Option B is deferred until all P0 gates
close and receives separate authority; Option C is rejected.

## Exact allow-list

1. `docs/decisions/2026-08-05-real-user-onboarding-legal-boundary.md`
2. `docs/security/REAL_USER_ONBOARDING_PREIMPLEMENTATION_GATE.md`
3. `docs/coordination/CURRENT_TASK.md`
4. `docs/coordination/PROJECT_STATE.md`
5. `docs/coordination/CODEX_TO_COMMANDER.md`

No other file may change.

## Acceptance

- P0/P1 decisions have owners, evidence and blocking effects;
- Adult/Minor/Guardian, consent, data-flow/classification/purpose/access and
  record-lifecycle matrices are auditable;
- tenant, activation, Guardian, Recovery, enumeration and replay fail closed;
- provider/residency/DPA/incident ownership and Option B Go/No-Go are explicit;
- unresolved decisions remain `PENDING_COUNSEL` or `PENDING_EMPLOYER`;
- both primary docs trace the five Task72A-reviewed authorities;
- exact allow-list, path sanity and `git diff --check` pass;
- sequential Claude review of only the two primary docs passed under
  `CLAUDE_TASK72B_LEGAL_POLICY_PACKET_REVIEW_01_V2` with zero open blockers.

`FINAL_MARKER: CLAUDE_TASK72B_REVIEW_COMPLETED`

## Authority and exclusions

In-scope remediation, commit, push to this branch and Draft PR are authorized
only after Claude PASS and green checks. Direct-main push, merge, force-push
and branch deletion are forbidden.

No model, schema, migration, API/OpenAPI, UI, code/state-machine implementation,
PII/real data, account, credential, session, active membership, role, public
endpoint, email/SMS/OAuth/provider integration, Guardian/Recovery
implementation, deployment, Alpha, Production or protected `codesho`
promotion is authorized.
