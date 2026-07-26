# Current Task: SPRINT1-ADULT-SIGNUP-PROVENANCE-ARCHITECTURE-69A

- Owner: Codex
- Status: architecture/privacy-gate definition in progress.
- BASE_SHA: `fc2aa2f4d7261dc7bb597886dbe782163313eceb`.
- Target repository: `mytest19861986/codesho-test`.
- Branch: `agent/task69a-provenance-architecture`.
- Employer standing authorization date: `2026-07-26`.

## Goal

Define a precise, provider-neutral privacy/provenance separation contract for
the internal synthetic adult-attestation foundation. This task changes
documentation only and creates no Production claim.

## Exact allow-list

```text
docs/decisions/2026-07-26-adult-signup-provenance-separation.md
docs/coordination/CODEX_TO_COMMANDER.md
docs/coordination/CURRENT_TASK.md
docs/coordination/PROJECT_STATE.md
```

## Acceptance criteria

1. Base and PR #7 merge evidence match the Commander disposition.
2. The new decision document contains all required sections and contract
   invariants, options A/B/C, and `LEGAL_PENDING` treatment.
3. Coordination records state PR #7 `CLOSED / MERGED`, main
   `fc2aa2f4d7261dc7bb597886dbe782163313eceb`, and Task69A architecture-only
   status.
4. No stale PR #7 unmerged claim remains except explicit historical context.
5. No model, migration, endpoint, OpenAPI, configuration, test, or source
   code changes are made.
6. The final diff contains exactly four allow-listed files and passes
   `git diff --check`.

## Review and release gates

```text
Task68E: COMPLETED / CLOSED; PR #7 CLOSED / MERGED
Provider-neutral independent documentation review: REQUIRED
Privacy architecture verdict: PASS REQUIRED
Internal consistency: PASS REQUIRED
Task69A CI (backend/frontend/smoke_restore): REQUIRED
Real-user Legal approval: REQUIRED / BLOCKING
Deployment: NOT AUTHORIZED
Release: NOT AUTHORIZED
Protected codesho promotion: NOT AUTHORIZED
```

## Stop conditions

Stop if completion requires a file outside the allow-list, product/source
changes, real user data, PR #5 mutation, deployment, release, Production
enablement, or protected-repository promotion.
