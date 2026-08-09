# Codesho Project State

## TASK77C_CHECKPOINT_20260809

Task77C clean integration is in progress on branch
`codex/task77c-cleanup-claim-lease-clean-integration`, based exactly on
`39c35a50965184681599a0ade0dd65f34b7aa548`. The reviewed Task77B semantic
delta is being transferred without replaying historical coordination or
governance. Focused tests and local static/application gates pass; the full
backend has `217 passed, 52 skipped, 1 failed`, with the known unrelated
OpenAPI canonical LF/CRLF failure outside the allow-list. Remote CI/Compose
and Claude hard review are green for HEAD `338ee7a`: CI `31294215288`, Compose
`31294215324`, and Claude `CLAUDE_TASK77C_CLEAN_INTEGRATION_HARD_GATE_01_V1`
all passed with zero P0/P1/open blockers. Non-blocking P2 notes are recorded
in the review summary. No protected-repository, release, deployment, or
production action occurred.

## Task76A checkpoint (2026-08-08)

Task76A implementation is complete on `codex/task76a-passcode-change-cleanup-hardening`
from `cb967c26e0faf9a5868e9adc74d59a09c6a42b99`. Inspection preserved all
pre-existing untracked paths. The minimal implementation hardens the cleanup
batch and terminal-retention settings at import time and documents the
passcode-change settings in `.env.example`; existing tenant-scoped atomic
cleanup, bounded deletion, audit ordering, and explicit `BaseTenantTask`
execution were not rewritten. Focused cleanup tests pass (`7 passed`), related
tests pass (`22 passed`), and Ruff/Django/migration/compileall/diff checks pass.
The full backend suite reports `213 passed, 49 skipped, 1 failed`; the sole
failure is the unrelated OpenAPI canonical-byte test due to generated LF versus
committed CRLF in `docs/openapi.yaml`, outside the Task76A allow-list. The
full-suite revalidation was run from the official `backend` cwd, confirming
the prior root-cwd compose-path failure was environmental. Claude implementation
review `CLAUDE_TASK76A_PASSCODE_CHANGE_CLEANUP_IMPLEMENTATION_REVIEW_01_V1`
returned `PASS` with zero open/P0/P1 blockers; only a non-blocking auditability
note about the pre-existing PostgreSQL cleanup function was raised.

Updated: 2026-08-06 (Task73B OpenAPI contract remediation)

## Current Status

Task73B is `COMPLETE / LOCAL_GATES_PASS / CI_COMPOSE_PASS / CLAUDE_PASS` on
`codex/task73b-openapi-contract-drift` from
`dca0800fd74fb3e852aacb9122e6c533538d2629`. It adds an isolated schema-only
projection for exactly six approved operations, canonical byte-for-byte OpenAPI
verification, route/method/callback parity tests, and fail-closed staff-only
schema/Swagger access. Runtime URLs, auth, CSRF, sessions, cookies, tenant
middleware, business logic and public API behavior are unchanged. Claude
implementation Review 02 passed with zero open blockers. CI `31078717976`
(backend/frontend) and Compose smoke/restore `31078717914` are SUCCESS for
`264d85d06fc7c48c4eb2a721e69f53b58a57f7c5`; documentation checkpoint CI
`31078984692` and Compose `31078984491` are also SUCCESS. Review 03's Compose-only
P1 is closed by final Claude evidence-closure Review 04 (PASS / zero open blockers).
PR #16 remains Draft. Direct-main, Ready,
merge, release, Alpha and protected promotion remain forbidden.

Task72B is `COMPLETE / DOCS-ONLY / OPTION-A / CLAUDE-PASS`. It records the real-user
onboarding legal/policy boundary without implementation. Lawful-basis,
Controller, jurisdiction, notice/consent, Adult/Minor/Guardian, lifecycle,
tenant-authority, Recovery, activation, provider/residency and operational
decisions remain `PENDING_COUNSEL` or `PENDING_EMPLOYER`. Option B is deferred;
Option C is rejected. Real-user collection, PII, accounts, credentials,
sessions, active memberships, public endpoints, providers, Alpha, Production
and protected-repository promotion fail closed.

The authoritative base is `0472239d06194875d1cdb6f6929dd8eaad8bc0d9`;
branch is `codex/task72b-real-user-legal-policy-packet`. Only the five files in
`CURRENT_TASK.md` may change. Documentation checks passed. Sequential Claude
review `CLAUDE_TASK72B_LEGAL_POLICY_PACKET_REVIEW_01_V2` passed with zero P0,
zero P1 and zero open blockers. `FINAL_MARKER:
CLAUDE_TASK72B_REVIEW_COMPLETED`. Merge/direct-main remain forbidden.

Task71B Synthetic Account Bootstrap is `COMPLETE / MERGED / VERIFIED`. PR #12
was Squash-merged into `codesho-test/main` at
`f08ddd9e56ea2c7f503fbe4e5287f4665840ec2b`; post-merge CI `31042633399` and
Compose smoke/restore `31042633952` are `SUCCESS`. The independent review
verdict is `PASS` with zero open blockers.

The merged foundation creates only opaque, inactive, roleless synthetic
memberships and dormant no-credential users; it adds no public or Production
capability. Production, Alpha, real-user activation, deployment, release,
public API expansion, backfill, providers, and protected `codesho` promotion
remain unauthorized. Legal decisions remain `LEGAL_PENDING`.

Task69B/Task70A/Task71A and pre-merge Task71B wording below is historical
evidence only.

Task67A/67B and the Task68A documentation closeout are merged. PR #7 is
CLOSED / MERGED at `fc2aa2f4d7261dc7bb597886dbe782163313eceb`. Its parents
are `e11557f378231469d22348f4959caa554dbbd406` and
`3c61ae6b4b2408a8f2dd759eb266089ac3a3ccff`. The resulting
`codesho-test/main` commit is `fc2aa2f4d7261dc7bb597886dbe782163313eceb`.

The merged head passed backend PostgreSQL, frontend, and smoke_restore.
Security, Privacy, and Database review verdicts were each
APPROVED_WITH_NON_BLOCKING_NOTES. This merge does not authorize Production,
real-user availability, deployment, release, or protected-repository
promotion.

The foundation records only an explicit adult self-attestation for an opaque
synthetic UUID. It is disabled by default, rejected by production settings,
rate-limited through HMAC-anonymous Redis keys, tenant-scoped, immutable, and
bound atomically to allow-listed security audit evidence. It creates no user,
credential, membership, session, frontend signup route, Guardian/Recovery
relationship, or real-user capability.

The earlier Platform Operator/Admin merge remains recorded at
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

Task69A architecture/privacy gate was accepted and merged as PR #8 at
`27a8626d29bfa7e21c5e770455db6b20a4521ccc`. Task69B is the separately
authorized internal synthetic implementation based on that contract. Claude
verification debt remains closed by the
published Task51 checkpoint. The
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

## Task67A/67B review disposition and future gates

- The Database `get_or_create` P1 was rejected: Django catches the
  uniqueness-race `IntegrityError` and retrieves the winning row using the
  same immediate unique-constraint fields.
- Privacy provenance separation is defined by
  `docs/decisions/2026-07-26-adult-signup-provenance-separation.md`; legal
  retention, deletion, and linkage decisions remain `LEGAL_PENDING`. Task69B
  adds no real-user or Production capability.
- All P2 review findings are recorded as non-blocking technical debt; they do
  not alter the confirmed Task67A gate results.

## Blockers

- Real users remain blocked by `LEGAL_PENDING`.
- No active blocker remains for the Platform Operator/Admin closeout.
- Historical local-environment limitations in earlier checkpoints are retained
  in their original records and do not represent an unresolved Task63D gate.

## Historical Task71A next steps

1. Complete self-review, provider-neutral independent architecture review,
   exact-file review, and backend/frontend/smoke_restore CI for the Draft PR.
2. Record only review findings and dispositions in the Task71A review summary;
   keep raw prompts and responses outside the repository.
3. Request separate authority before marking ready or merging to
   `codesho-test/main`; never promote to protected `codesho`.

## Historical Next Steps

1. Wait for the next separate authorized Task; Task69B review, CI, Ready, and
   merge work are complete.
2. Resolve legal retention/deletion/linkage decisions before any future
   real-user, public-availability, or Production decision.
3. Recovery, Guardian, Notification, user creation, OAuth and Onboarding require
   separate authorized Tasks.
4. Do not mutate or merge PR #5 without a separate disposition. Do not activate
   Production or real Alpha, deploy, provision policy, or
   promote to protected `codesho` without explicit employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain
  deferred.
- Legal retention/privacy/aging-out rules require counsel before paid
  production.
- Local Compose verification remains unavailable, though the CI/staging gate
  is green.
## TASK77A_INSPECTION_CHECKPOINT_20260808

- TASK_ID: `SPRINT1-SECURITY-CLEANUP-SCHEDULING-ARCHITECTURE-77A`
- BASE_SHA: `cb967c26e0faf9a5868e9adc74d59a09c6a42b99`
- BRANCH: `codex/task77a-cleanup-scheduling-architecture`
- STATUS: `INSPECTION COMPLETE / DOCS-ONLY / CLAUDE GATE REQUIRED`
- CURRENT_EXECUTION_MODEL: explicit `tenant_id` -> `BaseTenantTask` ->
  `tenant_atomic` -> bounded tenant cleanup; no periodic schedule.
- CURRENT_RLS_CONSTRAINTS: runtime worker remains FORCE-RLS-compatible and
  fail-closed; tenant context is established before tenant queries.
- CURRENT_CELERY_CONSTRAINTS: JSON task payloads, no Beat schedule, no global
  cleanup task, and tenant-aware work must inherit `BaseTenantTask`.
- CURRENT_IDEMPOTENCY_MECHANISMS: deterministic per-challenge audit/event
  identifiers, row locking with `skip_locked`, atomic cleanup/audit updates,
  and bounded batches.
- THREAT_SUMMARY: duplicate schedulers/delivery, stale or disabled tenants,
  retry storms, unbounded fan-out, lease expiry, cross-tenant access, and
  scheduler privilege escalation must fail closed.
- PROPOSED_RECOMMENDATION: database-authoritative bounded work claims with
  short leases, explicit ownership, and one tenant task per claim.
- CHANGED_TRACKED_FILES: Task77A exact allow-list only.
- UNAUTHORIZED_ACTIONS: no scheduler implementation, migration, production,
  merge, Ready transition, or protected-repository promotion.

## TASK77A_REVIEW_TRANSPORT_BLOCKER_20260808

- QWEN_PROMPT_ID: `QWEN_TASK77A_CLEANUP_SCHEDULING_ARCH_CHALLENGE_01_V1`
- CLAUDE_PROMPT_ID: `CLAUDE_TASK77A_CLEANUP_SCHEDULING_ARCHITECTURE_REVIEW_01_V1`
- ATTEMPT: Commander bridge attempted `chrome.user.openTabs()` for the exact
  Qwen conversation URL `https://chatgpt.com/c/6a758cbd-6c88-83eb-b124-068222291391`.
- ERROR: browser transport returned an environment failure before the tab
  listing completed; a second attempt also timed out and reset the browser
  kernel. No review response was received.
- DISPOSITION: no Qwen or Claude verdict is claimed; no code or architecture
  change was made in response to an unverified review. Resume with Qwen first,
  then Claude sequentially, when the authenticated browser transport returns.

## TASK77A_QWEN_SUBMISSION_CHECKPOINT_20260808

- QWEN_URL: `https://chat.qwen.ai/c/abb20f82-6c44-4cf4-a854-f5e3f8831edb`
- PROMPT_ID: `QWEN_TASK77A_CLEANUP_SCHEDULING_ARCH_CHALLENGE_01_V1`
- SUBMISSION: prompt was sent successfully to the authenticated Qwen
  conversation at the exact URL above.
- POLLING: multiple 30-second checks observed Qwen evaluating the prompt; the
  tab subsequently left the shared session before a final response could be
  retrieved.
- VERDICT: `NOT RECEIVED`; no PASS or CHANGES_REQUIRED claim is made.
- NEXT GATE: recover the real Qwen response, disposition findings if any, then
  run the sequential mandatory Claude review.

## TASK77A_QWEN_DISPOSITION_20260808

- PROMPT_ID: `QWEN_TASK77A_CLEANUP_SCHEDULING_ARCH_CHALLENGE_01_V1`
- VERDICT: `CHANGES_REQUIRED`
- OPEN_BLOCKERS: `7`; P0: `0`; P1: `7`
- DISPOSITION: accepted and remediated in the decision document and review
  summary, all within the exact five-file allow-list. Clarifications cover
  normative one-tenant claim transitions, role/RLS authority, lease lifecycle,
  Outbox publication, capacity/fairness/backpressure, fail-closed operations,
  and Task77A governance boundaries.
- NO_RUNTIME_CHANGE: Python, schema, migration, settings, Celery, worker, and
  scheduler files remain unchanged.
- NEXT_GATE: mandatory sequential Claude review with
  `CLAUDE_TASK77A_CLEANUP_SCHEDULING_ARCHITECTURE_REVIEW_01_V1`.
## TASK77A_CLAUDE_GATE_RESULT_20260808

The existing authenticated Claude tab reviewed the supplied Task77A materials
for commit `f0692d53cdeb1d65857d3efeb35a49dc709c4ab2` and returned
`PASS / OPEN_BLOCKERS: 0 / P0: 0 / P1: 0`. The review confirmed the docs-only
boundary, tenant-safe architecture, fail-closed rules, RLS/role separation,
Qwen disposition, and governance boundary. The next step requires a separate
Commander-approved implementation task; no implementation or release authority
is implied.
