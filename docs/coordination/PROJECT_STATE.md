# Codesho Project State

Updated: 2026-07-26 (Task67A adult signup internal implementation)

## Current Status

Task67A is active from independent BASE_SHA
`5ef6323a42739613b05eab1fcbb07e009a87e859` on branch
`codex/task67a-adult-signup-internal`. Employer authority is limited to
development and internal synthetic-data testing. Local implementation and
checks are complete; real PostgreSQL CI and the required external
security/privacy/database review remain pending.

The foundation records only an explicit adult self-attestation for an opaque
synthetic UUID. It is disabled by default, rejected by production settings,
rate-limited through HMAC-anonymous Redis keys, tenant-scoped, immutable, and
bound atomically to allow-listed security audit evidence. It creates no user,
credential, membership, session, frontend signup route, Guardian/Recovery
relationship, or real-user capability.

`codesho-test/main` is at merged commit
`49acc1818b6afb1d78e5e8155d0dd9b90fbbf784`. PR #3 is merged and closed; its
parents are `98c8132312d67094fbc316dea68feb454c4ffe68` and
`75c3dcd7382d354fec10315daad9d30ef466c982`.

Task62V verified the merged Platform Operator/Admin implementation
post-merge. The exact verification evidence is recorded in
`CODEX_TO_COMMANDER.md` under `TASK62V_COMPLETE_20260726_07`.

- CI `29427888761`: backend and frontend checks passed.
- Compose smoke and restore `29427888874`: isolated full-stack startup,
  PostgreSQL RLS/connection-reuse tests, and backup/restore drill passed.

Task54 backlog/evidence reconciliation is complete at
`64d9afd9d5d7f53076f15424683465298e85cbda`. CI `29920923743` and Compose
smoke/restore `29920923814` both succeeded. The reconciliation mapped existing
Sprint 1 evidence and preserved Production/Alpha/protected-repository gates;
its platform-operator/admin candidate was later separately authorized,
implemented, merged as PR #3, and verified by Task62V.

Task63D is a documentation-only closeout. No active implementation task exists
after this checkpoint; a separate authorized Task with an independent BASE_SHA
is required before further feature work. Claude
verification debt remains closed by the published Task51 checkpoint. The
historical marker `CLAUDE_VERIFICATION_DEBT_CLEARED_PENDING_DOC_CHECKPOINT`
remains preserved in the security documents; its documentation checkpoint was
published by Task51.

Production activation, real Alpha activation, and promotion to protected
`codesho` remain unauthorized. Existing open legal, TLS, cleanup-scheduling,
and Alpha-readiness gates remain unchanged; no new claim is made here.

## Completed

- Employer architecture and Sprint Zero defaults recorded.
- Django 5.2 modular-monolith skeleton and Next.js TypeScript/RTL build.
- Tenant context, PostgreSQL RLS migration and negative tests.
- Outbox foundation, duplicate-delivery tests and `BaseTenantTask`.
- Docker Compose, Nginx same-origin proxy, Redis/Celery, OpenAPI and CI.
- Sprint Zero threat, load and backup/restore documentation.
- SZ-020 Claude review completed and findings dispositioned; no unresolved
  Claude P0 remains. The auditable summary is at
  `docs/reviews/sz-020-review-resolution-summary.md`.
- SZ-021 employer decision gate and Sprint 1 plan prepared and verified.
- Employer decisions recorded: 1-B, 2-A, 3-A-revised and 4-A-revised.
- S1-001R Claude Review 01 and Review 02 were completed sequentially; raw
  responses/prompts are retained outside the repository. The review summary
  is `docs/reviews/s1-001-role-separation-review-summary.md`.
- S1-002 Passcode Foundation is implemented at `d29fd1c`: Argon2id, versioned
  Pepper HMAC, six-ASCII-digit validation, atomic credential service, model,
  migration, tests, Data Dictionary and Threat Model updates. Claude Review 01
  (service) and Review 02 (model/migration) both completed with no unresolved
  blocker; summary is `docs/reviews/s1-002-passcode-review-summary.md`.
- S1-003 Abuse Control Foundation is implemented locally: HMAC-anonymous
  Redis Lua counters, fail-closed outage handling, progressive delays,
  durable monotonic lockout, trusted-proxy/device extraction and no public API.
  Claude Review 01 was completed sequentially; its findings are recorded in
  `docs/reviews/s1-003-abuse-control-review-summary.md`. Review 02 closed its
  configuration-test blocker; final implementation commits are `7935fcf` and
  `cbd4a8c`.

## Historical Evidence

- Earlier CI `29406301878` for `0e65d23` and CI `29427689716` / Compose
  `29427689672` for `49c25c1` remain historical checkpoints. They are not the
  current closure evidence.
- The current closure evidence is the successful pair for `013bccc` above.

## Historical Sprint 1 Checkpoints (closed)

- S1-004 Immutable Credential Security Audit Foundation is complete at
  `924f76f`. The audit ledger is immutable, runtime has only EXECUTE access to
  the restricted `SECURITY DEFINER` append function, and reason codes are an
  immutable allow-list. CI `29479743517` and Compose smoke/restore
  `29479741154` are successful; final sequential Claude verification recorded
  no unresolved P0/P1. No Login, Session, Guardian, Notification, public API,
  frontend, or producer integration was included.
- S1-001 is complete at implementation checkpoint `972c54b`. It separates
  `codesho_migrator` from `codesho_runtime`: migrations run
  in a one-shot Compose service; backend, worker and beat use runtime-only
  database URLs; CI and Compose smoke/restore now verify DDL/RLS denial and
  restored ownership/grants. Review 02 identified and the code now closes the
  PUBLIC privilege gap on audit/analytics/platform; `\\getenv` avoids password
  process-argument exposure. Local checks remain green. Final checkpoint
  `a7d4fbf` passed CI `29436322030` and Compose smoke/restore `29436321886`.

## Blockers

- Task67A cannot advance to Ready for Review or Merge without successful real
  PostgreSQL CI and sequential external security/privacy/database review.
- Task67A commit `d1d70e0fdc9cd9849b9e88244b47d86e95e31576` is pushed to
  `codex/task67a-adult-signup-internal`. Draft PR publication is blocked only
  by unavailable authenticated GitHub browser/connector access; no PR or CI
  run exists yet.
- Real users remain blocked by `LEGAL_PENDING`.
- No active blocker remains for the Platform Operator/Admin closeout.
- Historical local-environment limitations in earlier checkpoints are retained
  in their original records and do not represent an unresolved Task63D gate.

## Next Steps

1. Publish the scoped Task67A checkpoint to a Draft PR and run repository CI.
2. Complete sequential external review and disposition findings; do not mark
   Ready for Review or Merge without separate authority.
3. Recovery, Guardian, Notification, user creation, OAuth and Onboarding require
   separate authorized Tasks.
4. Do not activate Production or real Alpha, deploy, provision policy, or
   promote to protected `codesho` without explicit employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain
  deferred.
- Legal retention/privacy/aging-out rules require counsel before paid
  production.
- Local Compose verification remains unavailable, though the CI/staging gate
  is green.
