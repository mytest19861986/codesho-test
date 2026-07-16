# Codesho Project State

Updated: 2026-07-16 (S1-004 immutable security-audit foundation in progress)

## Current Status

Sprint Zero is technically closed at `013bccc834b31c91a1424c14a304eb6acc01ff0a`
on `codesho-test/main`. Its two required GitHub Actions workflows completed
successfully. The employer approved all four Sprint 1 gate decisions on
2026-07-15, authorizing S1-001 PostgreSQL migrator/runtime separation.

- CI `29427888761`: backend and frontend checks passed.
- Compose smoke and restore `29427888874`: isolated full-stack startup,
  PostgreSQL RLS/connection-reuse tests, and backup/restore drill passed.

SZ-021 is complete at `dc13cc891dfff2e4df9a70ce61da7d8e73f3a4f2`: it records
review traceability and prepares, but does not implement, the employer
decisions that gate Sprint 1 Identity Foundation. Its CI `29430842483` and
Compose smoke/restore `29430842466` are both successful.

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

## In Progress

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

- Local Docker daemon remains unavailable:
  `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
  The required S1-001 Compose gate passed in isolated GitHub Actions.
- Local Docker daemon remains unavailable for an on-workstation Compose run;
  the replacement CI/Compose evidence will be collected after this commit.

## Next Steps

1. Do not begin Login, Rate Limit, Recovery, UI, or audit-event producer
   integration without a new Commander task; do not promote to protected
   `codesho` without employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain
  deferred.
- Legal retention/privacy/aging-out rules require counsel before paid
  production.
- Local Compose verification remains unavailable, though the CI/staging gate
  is green.
