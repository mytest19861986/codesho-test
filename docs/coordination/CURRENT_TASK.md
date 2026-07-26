# Current Task: SPRINT1-ADULT-SIGNUP-CLOSEOUT-67B

- Owner: Codex
- Status: documentation-only closeout in progress. PR #6 is OPEN / READY /
  UNMERGED. Development/internal synthetic-data authority only.
- BASE_SHA: `a7caa268e0ce32b4b8e074d539add0ea4d07143d`.
- Target repository: `mytest19861986/codesho-test`.
- Branch: `codex/task67a-adult-signup-internal`.
- Checkpoint commit: `a7caa268e0ce32b4b8e074d539add0ea4d07143d`.
- Employer authorization date: `2026-07-26`.

## Goal

Implement a fail-closed adult age-attestation foundation for a future signup
flow. The endpoint may record only a self-attested `18+` status and minimal
immutable evidence for a synthetic opaque subject. It does not create a user,
credential, membership, session, Guardian relationship, or public signup flow.

## Task67B exact allow-list

```text
docs/coordination/CODEX_TO_COMMANDER.md
docs/coordination/CURRENT_TASK.md
docs/coordination/PROJECT_STATE.md
docs/reviews/s1-067a-adult-signup-review-summary.md
```

No backend, frontend, migration, OpenAPI, workflow, configuration,
architecture, product, UI, deployment, protected-repository, Guardian/Recovery,
or real-user file is in scope.

## Task67B acceptance criteria

1. Record the confirmed gates: backend PostgreSQL SUCCESS, frontend SUCCESS,
   smoke_restore SUCCESS, and security/privacy/database APPROVED_WITH_NON_BLOCKING_NOTES.
2. Record the rejected database `get_or_create` P1 rationale and the mandatory
   future privacy provenance-separation gate.
3. Record P2 findings as non-blocking technical debt.
4. Preserve PR #6 as OPEN / READY / UNMERGED and make no Production or
   real-user readiness claim.
5. Keep the diff limited to this task's four-file allow-list and pass
   `git diff --check`.

## Review and release gates

```text
Security/privacy/database review: REQUIRED BEFORE MERGE
Repository CI: REQUIRED BEFORE MERGE
Real-user Legal approval: REQUIRED / BLOCKING
Ready for Review: NOT AUTHORIZED BY THIS TASK
Merge: NOT AUTHORIZED
Deployment: NOT AUTHORIZED
Protected codesho promotion: NOT AUTHORIZED
```

## Stop conditions

Stop for new authority if implementation requires real user data, birth date,
identity evidence, Guardian/Minor/Recovery, account creation, frontend/public
activation, external provider access, a file outside the allow-list, Merge, or
Deployment.
