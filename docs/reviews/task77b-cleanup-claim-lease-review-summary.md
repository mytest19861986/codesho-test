# Task77B Cleanup Claim / Lease Review Summary

## TASK77B_BOUNDARY_DISPOSITION_01

The first implementation placed tenant/Outbox orchestration in identity and
failed the authoritative module-boundary checker. Commander resolved this by
retaining the persistence model in identity and moving orchestration to
`config.cleanup_claims`. The checker was not weakened and no hidden import was
used.

## Implementation checkpoint

The claim model, bounded settings, migration RLS contract, transactional
Outbox intent, explicit tenant task wrapper, and focused tests are present on
the stacked Task77B branch. Local focused evidence is 11 passing tests plus
Ruff, MyPy, module-boundary, Django check, and migration-check passes.

This is not a final review verdict. PostgreSQL locking/RLS/catalog evidence and
the required sequential Qwen then Claude reviews remain open. No production or
merge authority is implied.

## QWEN_TASK77B_CLEANUP_CLAIM_LEASE_IMPLEMENTATION_CHALLENGE_01_V1

- VERDICT: `CHANGES_REQUIRED`
- OPEN_BLOCKERS: `7`; P0: `0`; P1: `7`; P2: `3`
- DISPOSITION: accepted as evidence/remediation requirements, not as a reason
  to weaken RLS or tests. The implementation added PostgreSQL-only RLS,
  privilege, and competing-claimer test contracts; added rollback and retry
  boundary tests; and made the lease boundary explicit (`> DB now` is live,
  `<= DB now` is expired/reclaimable).
- LOCAL_RESULT: claim tests `8 passed, 2 skipped`; existing passcode cleanup
  plus claim tests `15 passed, 2 skipped`; Ruff, MyPy, module boundaries,
  Django check, migration check, and diff-check pass.
- REMAINING: real PostgreSQL/CI execution is still required for RLS, grants,
  FORCE RLS, SKIP LOCKED, concurrent reclaim/claim races, and catalog checks.
  Qwen's P2 documentation notes are retained: reverse migration safety,
  DB-time/kill-switch evidence, and malformed metadata/error non-exposure.
- NEXT_GATE: do not start Claude until PostgreSQL evidence and justified Qwen
  dispositions are complete. Raw Qwen prompt/response remains outside repo.
