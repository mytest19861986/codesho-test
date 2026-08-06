# Codex to Commander — Task72B legal/policy gate

## Task73B OpenAPI contract remediation

```text
MESSAGE_ID: CODEX_TASK73B_LOCAL_GATE_CHECKPOINT_20260806_V1
TASK_ID: SPRINT1-OPENAPI-CONTRACT-DRIFT-REMEDIATION-73B
BASE_SHA: dca0800fd74fb3e852aacb9122e6c533538d2629
BRANCH: codex/task73b-openapi-contract-drift
STATUS: IMPLEMENTED / LOCAL_GATES_PASS / CI_COMPOSE_PASS / CLAUDE_REMOTE_EVIDENCE_PENDING
ALLOW_LIST: EXACTLY_TEN_FILES (Commander approved .github/workflows/compose-smoke.yml)
CLAUDE_IMPLEMENTATION: PASS / OPEN_BLOCKERS 0
CLAUDE_PROMPT_ID: CLAUDE_TASK73B_OPENAPI_CONTRACT_IMPLEMENTATION_REVIEW_02_V1
LOCAL_GATES: ruff PASS; mypy PASS; Django check PASS; makemigrations check PASS;
focused OpenAPI 10 passed; full backend 209 passed, 49 PostgreSQL-only skips;
schema validation PASS; canonical byte diff PASS; git diff check PASS
RUNTIME_AUTH_CSRF_SESSION_COOKIE: UNCHANGED
DIRECT_MAIN_READY_MERGE_PRODUCTION_ALPHA_CODESHO: NOT_AUTHORIZED
IMPLEMENTATION_HEAD: 264d85d06fc7c48c4eb2a721e69f53b58a57f7c5
PR_16: DRAFT / https://github.com/mytest19861986/codesho-test/pull/16
CI_31078717976: SUCCESS (backend/frontend)
COMPOSE_31078717914: SUCCESS (smoke_restore)
CLAUDE_REVIEW_03: CHANGES_REQUIRED only for remote Compose evidence; resolved by COMPOSE_31078717914, Claude acknowledgement pending
NEXT: retain Draft, await sequential Claude acknowledgement, then final closeout review
```

The canonical schema uses only `config.openapi_urls`; its six declarations are
unreachable at runtime and fail closed with `Http404`. The live schema and
Swagger endpoints use `SessionAuthentication` and `IsAdminUser` through
drf-spectacular settings. Tests prove route/method/callback parity,
deterministic generated output and unapproved-path exclusion. No secret or
sensitive user value was emitted.

---

```text
TASK_ID: SPRINT1-REAL-USER-ONBOARDING-LEGAL-AND-BOUNDARY-DECISION-72B
BASE_SHA: 0472239d06194875d1cdb6f6929dd8eaad8bc0d9
BRANCH: codex/task72b-real-user-legal-policy-packet
STATUS: COMPLETE / DOCS-ONLY / OPTION-A / CLAUDE_PASS
ALLOW_LIST: EXACTLY_FIVE_FILES
OPTION_A: SELECTED
OPTION_B: DEFERRED_PENDING_ALL_P0_AND_NEW_AUTHORITY
OPTION_C: REJECTED
REAL_USER_OR_PII: PROHIBITED
IMPLEMENTATION: NONE
MERGE_OR_DIRECT_MAIN: NOT_AUTHORIZED
PRODUCTION_ALPHA_CODESHO_PROMOTION: NONE
CLAUDE_PROMPT_ID: CLAUDE_TASK72B_LEGAL_POLICY_PACKET_REVIEW_01_V2
CLAUDE_VERDICT: PASS
CLAUDE_OPEN_BLOCKERS: 0
FINAL_MARKER: CLAUDE_TASK72B_REVIEW_COMPLETED
VALIDATION: EXACT_ALLOW_LIST_PASS / DIFF_CHECK_PASS / PATH_SANITY_PASS
```

The packet records P0/P1 owners, evidence, fail-closed effects,
persona/consent/data/lifecycle matrices, conceptual gates,
tenant/Guardian/Recovery/enumeration threats, provider/residency/operations,
and Option B Go/No-Go. All unresolved items are `PENDING_COUNSEL` or
`PENDING_EMPLOYER`; no legal conclusion or retention duration was invented.

Claude V1 found one P0 ordering ambiguity and two P1 auditability/status
issues. The two primary docs were remediated within scope. Sequential V2 then
returned `PASS`, `OPEN_BLOCKERS: 0`, `P0: NONE`, `P1: NONE`, and confirmed the
packet is sufficient to govern a later separately authorized Option B. Raw
review remains outside the repository.

Remaining legal/product decisions by owner:

- `PENDING_COUNSEL`: jurisdiction applicability, lawful basis, Controller
  validation, notice/consent/withdrawal, Minor/Guardian/aging-out, every
  record's retention/deletion/erasure/DSR/legal hold, DPIA/no-DPIA,
  provider/residency/DPA and applicable incident/breach duties.
- `PENDING_EMPLOYER`: launch jurisdictions/personas/PRD, Controller and
  operational owners, tenant authority, identifiers/verification, Recovery,
  activation, providers and operational RACI.

Required evidence and each blocking effect are recorded in the primary
decision tables. Until those owners approve them, Option B remains deferred,
Option C rejected, and all real-user/PII/implementation paths fail closed.

Commit/push/Draft-PR are authorized after final checks; merge remains forbidden.

---

# Historical Task71C closeout

```text
TASK_ID: SPRINT1-TASK71B-POST-MERGE-CLOSEOUT-71C
STATUS: AUTHORIZED / DOCS-ONLY / POST-MERGE-CLOSEOUT
BASE_SHA: f08ddd9e56ea2c7f503fbe4e5287f4665840ec2b
BRANCH: codex/task71c-post-merge-closeout
PR_12: CLOSED / MERGED / SQUASH
MERGE_SHA: f08ddd9e56ea2c7f503fbe4e5287f4665840ec2b
POST_MERGE_CI: 31042633399 / SUCCESS
POST_MERGE_COMPOSE: 31042633952 / SUCCESS
INDEPENDENT_REVIEW: PASS / OPEN_BLOCKERS 0
CURRENT_STATE: AWAITING_COMMANDER_NEXT_TASK
PRODUCTION/ALPHA/REAL_USER/PROTECTED_CODESHO: UNCHANGED / NOT_AUTHORIZED
LEGAL_RETENTION/DELETION/HOLD: LEGAL_PENDING
```

Task71B is complete. This closeout changes documentation only and preserves
the historical review, remediation, and pre-merge evidence below. Statements
below that describe Task71B as Draft, Ready, unmerged, merge-blocked, or
unpushable are historical and superseded by the final disposition above.

The remediation branch remains inside the exact allow-list. It adds a strict
database audit-to-request binding, synthetic-only user/membership guards that
do not block human membership lifecycle, non-privileged synthetic User
constraints, PostgreSQL provenance rollback/direct-SQL tests, and conditional
reverse contracts that reject reversal when protected data or evidence exists.
Local focused tests pass with PostgreSQL-only cases skipped; full backend and
coverage, Ruff, MyPy, Django check, module boundaries, migration drift, and an
empty SQLite migration pass. Commander authorized one non-amended commit and
push to this remediation branch only; merge remains forbidden pending CI gate.

The pushed checkpoint exposed PostgreSQL-only test/rollback defects, not a
reason to weaken the production contract. The local correction uses real audit
rows for PostgreSQL valid paths, asserts Django's wrapped trigger error, and
makes reverse checks see across FORCE RLS without leaving it disabled. The
second re-review further requires and now has a real empty PostgreSQL reverse
probe with catalog assertions and rollback, plus exact populated failure/cause
and catalog-preservation assertions. The FORCE baseline is explicitly owned by
the still-applied `platform_tenant.0002_membership_rls` dependency. Full local
suite is `199 passed / 49 skipped` at `85.55%` coverage. Real PostgreSQL CI is
still required; no corrective commit, push, or merge is authorized yet.

---

# Historical Codex to Commander — Task70A

## Current closeout: Task69B

```text
TASK_ID: SPRINT1-TASK69B-POST-MERGE-CLOSEOUT-70A
STATUS: COMPLETE / MERGED / VERIFIED
BASE_SHA: 5be173afb03197cbc2e293e2ff28e1f9156a47ad
IMPLEMENTATION_HEAD: 889d1e998a1433c31646179856922fa2d0b6c449
CI_EVIDENCE_HEAD: 57e235cd088174e5a75132ea89f82a105191adfc
CI_RUNS: 30218593247 backend/frontend SUCCESS; 30218593254 smoke_restore SUCCESS
DOCUMENTATION_CHECKPOINT_HEAD: 0aea2e0a1dbba925343a854de35683b84d83a748
MERGE_COMMIT: 5be173afb03197cbc2e293e2ff28e1f9156a47ad
MERGE_PARENTS:
- 27a8626d29bfa7e21c5e770455db6b20a4521ccc
- 0aea2e0a1dbba925343a854de35683b84d83a748
PR_9: CLOSED / MERGED
SOURCE_BRANCH: agent/task69b-provenance-synthetic / PRESERVED
PR_5: OPEN / DRAFT / UNCHANGED / HEAD ee708a59fda89f08b824b079ebece2eed3b5515b
PRODUCTION/DEPLOYMENT/RELEASE: NOT_AUTHORIZED
REAL_USERS/PUBLIC_API/BACKFILL/PROVIDER: NOT_AUTHORIZED
PROTECTED_CODESHO_PROMOTION: NOT_AUTHORIZED
NEXT_STATE: WAITING_FOR_NEXT_SEPARATE_AUTHORIZATION
LEGAL_RETENTION/DELETION/HOLD: LEGAL_PENDING
```

Task69B has passed its implementation, review, CI, merge, and post-merge
verification gates. The remaining Task69B Draft/Ready/pending statements below
are historical records only and do not describe current repository state.

---

# Historical Codex to Commander — Task69B

```text
MESSAGE_ID: CODEX_TASK69B_PROVENANCE_SYNTHETIC_CHECKPOINT_20260726_07
TASK_ID: SPRINT1-ADULT-SIGNUP-PROVENANCE-SYNTHETIC-IMPLEMENT-69B
BASE_SHA: 27a8626d29bfa7e21c5e770455db6b20a4521ccc
BRANCH: agent/task69b-provenance-synthetic
STATUS: FINAL_REVIEW_PASS / DOCUMENTATION_CHECKPOINT / INTERNAL_SYNTHETIC_ONLY
IMPLEMENTATION_HEAD: 889d1e998a1433c31646179856922fa2d0b6c449
CI_EVIDENCE_HEAD: 57e235cd088174e5a75132ea89f82a105191adfc
DOCUMENTATION_CHECKPOINT: this coordination commit (docs-only after CI evidence)
PR_9: HISTORICAL / OPEN-DRAFT-THEN-MERGED / SUPERSEDED_BY_TASK70A_CLOSEOUT
PR_5: PRESERVED_AS_DRAFT / UNCHANGED
REAL_USERS: NOT_AUTHORIZED
PRODUCTION/DEPLOYMENT/RELEASE: NOT_AUTHORIZED
PROTECTED_CODESHO_PROMOTION: NOT_AUTHORIZED
```

## Task69B implementation checkpoint

Implemented the minimum Option B provenance boundary in the exact allow-list:

- independent append-only `AdultAttestationProvenance` model and migration;
- server-generated opaque UUID, tenant UUID, one-to-one attestation reference,
  controlled constants, and UTC timestamp only;
- `tenant_atomic` context for the attestation/provenance/audit transaction;
- PostgreSQL RLS/FORCE RLS, same-tenant trigger validation, immutable trigger,
  and runtime INSERT-only grants;
- replay, rollback, prohibited-field, cross-tenant, runtime privilege, API
  non-disclosure, and PostgreSQL contract tests;
- data dictionary entry without raw or sensitive review content.

No public API, OpenAPI, frontend, account/user/session, backfill, provider,
Production, deployment, release, or real-user behavior was added. PR #5 was
not changed.

## Local checkpoint evidence

```text
makemigrations --check --dry-run: PASS
focused tests (SQLite): 28 passed / 4 PostgreSQL-only skipped
ruff (focused files): PASS
mypy (focused source/migration): PASS
django check: PASS
docker compose local run: BLOCKED by missing required DATABASE_MIGRATOR_URL environment input
```

PostgreSQL/RLS/grant/trigger gates remain required in CI or an explicitly
configured real PostgreSQL role environment. Reviews are sequential and raw
review prompts/responses remain outside the repository.

## Task69B independent review checkpoint

Historical snapshot before merge; all status and gate statements in this
section describe that earlier checkpoint only.

Historical Commander response `COMMANDER_TASK69B_INDEPENDENT_REVIEW_20260726_07`
returned `CHANGES_REQUIRED` on an earlier head. Backend PostgreSQL CI run
`30216804608` failed four FORCE-RLS tests because provenance reads and migrator
mutation assertions lacked tenant context; frontend succeeded and Compose
smoke_restore run `30216804605` succeeded. This is recorded as
`69B-DB-01`: DISPOSED / PASS. The cross-tenant assertion uses beta context,
beta provenance tenant, alpha source attestation, and the explicit linkage
mismatch message. `69B-CI-02`: DISPOSED / PASS. `69B-DOC-02`: this checkpoint
disposes the stale-head documentation mismatch. At that historical snapshot,
PR #9 remained Draft pending
final CI/re-review on this documentation head.

Implementation head is `889d1e998a1433c31646179856922fa2d0b6c449`; cross-tenant
remediation is `585b3b9`; final documentation head is
`57e235cd088174e5a75132ea89f82a105191adfc`. Final-head CI was successful:
CI `30218263108` / workflow #194 and smoke_restore `30218263084` / workflow
#192. The final review verdict was PASS, followed by the authorized
Draft-to-Ready transition. Local focused tests remain `28
passed / 4 PostgreSQL-only skipped`; full backend SQLite tests remain `190
passed / 34 skipped`.

```text
MESSAGE_ID: CODEX_TASK69A_PROVENANCE_ARCHITECTURE_CHECKPOINT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-PROVENANCE-ARCHITECTURE-69A
BASE_SHA: fc2aa2f4d7261dc7bb597886dbe782163313eceb
BRANCH: agent/task69a-provenance-architecture
PR_7: CLOSED / MERGED
MERGE_COMMIT: fc2aa2f4d7261dc7bb597886dbe782163313eceb
STATUS: ARCHITECTURE_ONLY / PRIVACY_GATE / REVIEW_REQUIRED
REAL_USERS: NOT_AUTHORIZED
PRODUCTION/DEPLOYMENT/RELEASE: NOT_AUTHORIZED
PROTECTED_CODESHO_PROMOTION: NOT_AUTHORIZED
PR_5: PRESERVED_AS_DRAFT / UNCHANGED
```

## Task69A checkpoint

Added the provider-neutral architecture decision
`docs/decisions/2026-07-26-adult-signup-provenance-separation.md`. It defines
the separation of the minimal `adult_attested` claim from restricted opaque
provenance, distinguishes subject/attestation/provenance/security-audit
boundaries, specifies tenant/RLS fail-closed, immutability, idempotency and
data-minimization invariants, compares Options A/B/C, and records legal
retention/deletion/hold questions as `LEGAL_PENDING`.

No model, migration, endpoint, OpenAPI, configuration, test, frontend,
account, credential, provider, deployment, release, or real-user behavior was
changed. No sensitive or raw review content is included.

Task68E was accepted and verified: PR #7 is CLOSED / MERGED with parents
`e11557f378231469d22348f4959caa554dbbd406` and
`3c61ae6b4b2408a8f2dd759eb266089ac3a3ccff`. PR #5 remains a draft and was
not mutated.

## Required gates before closeout

- self-review and internal consistency: required;
- provider-neutral independent documentation review: required;
- privacy architecture verdict: PASS required;
- exact four-file allow-list and `git diff --check`: required;
- new backend, frontend, and smoke_restore CI: required;
- commit, push, draft PR, ready transition, and merge only under Task69A
  authorization and after all gates pass.

The next implementation step is a separate authorized Task69B. This checkpoint
does not create a Production claim or authorize real users.

## Commander response window

### Standing coordination default

Unless a newer explicit Commander instruction changes it, every future request
to Commander uses a `600-second / 10-minute` response window. If no complete
response arrives by then, refresh the shared session and resend the same
request, recording each attempt and window here or in the next scoped
coordination handoff. This is a coordination timing rule only; it does not
override repository safety, scope, authorization, or stop conditions.

```text
REQUEST_SENT_UTC: 2026-07-26T18:51:58Z
REQUEST: TASK69A review/disposition and independent documentation review
WAIT_WINDOW: 600 seconds (10 minutes)
PR: #8 OPEN / DRAFT
HISTORICAL_INTERMEDIATE_COMMIT: f7cfe2a59785798f333037476fd989935dcd98b7
FINAL_HEAD: 0d13d2bd432e746475198e2a81deef494f74d380
```

The ten-minute response window is recorded per the execution protocol. No
source-code or out-of-scope action is pending during the wait.

```text
MESSAGE_ID: CODEX_TASK68A_POST_MERGE_CLOSEOUT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-POST-MERGE-CLOSEOUT-68A
BASE_SHA: e11557f378231469d22348f4959caa554dbbd406
BRANCH: agent/task68a-post-merge-closeout
PR_6: CLOSED / MERGED
MERGED_AT: 2026-07-26T12:48:10Z
MERGE_COMMIT: e11557f378231469d22348f4959caa554dbbd406
STATUS: IMPLEMENTATION_COMPLETE / CI_REQUIRED / MERGE_NOT_AUTHORIZED
```

## Verified merge checkpoint

- Authorized PR head:
  `9247bec6e22e8415344d78ee90018ea8eaaeac90`.
- Merge parents: `5ef6323a42739613b05eab1fcbb07e009a87e859` and
  `9247bec6e22e8415344d78ee90018ea8eaaeac90`.
- Merge method: merge commit.
- backend PostgreSQL: SUCCESS.
- frontend: SUCCESS.
- smoke_restore: SUCCESS.
- No deployment, release, Production activation, real-user activation,
  protected `codesho` promotion, direct push, rebase, force-push, or branch
  deletion occurred as part of Task67C.

Task68A only reconciles the four allow-listed documents with this verified
state. Its merge requires separate employer authorization.

```text
MESSAGE_ID: CODEX_TASK67B_CLOSEOUT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-CLOSEOUT-67B
BASE_SHA: a7caa268e0ce32b4b8e074d539add0ea4d07143d
BRANCH: codex/task67a-adult-signup-internal
HISTORICAL_PR_STATE: #6 OPEN / READY / UNMERGED
STATUS: COMPLETED / MERGED_BY_PR_6
```

## Commander-confirmed gate disposition

- backend PostgreSQL: SUCCESS
- frontend: SUCCESS
- smoke_restore: SUCCESS
- Security, Privacy, Database: APPROVED_WITH_NON_BLOCKING_NOTES
- Database `get_or_create` P1: rejected because Django catches the
  uniqueness-race `IntegrityError` and retrieves the winning row using the
  same immediate unique-constraint fields.
- Privacy provenance separation: mandatory future gate before real users,
  public availability, or Production enablement.
- P2 findings: non-blocking technical debt.

This closeout made no Production or real-user readiness claim. Its merge was
later separately authorized and completed by Task67C. Deployment, release,
Production enablement, real-user activation, and promotion to `codesho` remain
forbidden.

```text
MESSAGE_ID: CODEX_ADULT_SIGNUP_IMPLEMENT_67A_PUSH_CHECKPOINT_20260726_02
TASK_ID: SPRINT1-ADULT-SIGNUP-IMPLEMENT-67A
BASE_SHA: 5ef6323a42739613b05eab1fcbb07e009a87e859
BRANCH: codex/task67a-adult-signup-internal
COMMIT: d1d70e0fdc9cd9849b9e88244b47d86e95e31576
STATUS: HISTORICAL / SUPERSEDED_BY_TASK67B_CLOSEOUT / PR6_OPEN_READY_UNMERGED
```

## Completed

- Created the independent Task67A branch from the exact authorized base.
- Recorded the employer decision and exact implementation allow-list.
- Added a disabled-by-default, production-prohibited adult age-attestation API.
- Added minimal append-only `AdultAgeAttestation` evidence with no birth date,
  numeric age, identity evidence, Guardian data, raw IP, or arbitrary metadata.
- Added HMAC-anonymous, fail-closed Redis limits.
- Added accepted/rejected immutable audit events and forward-only allow-list
  migration.
- Added strict CSRF, request-shape, UUIDv4, policy-version, idempotency,
  tenant-isolation, audit-failure, abuse-backend, immutability, privilege, and
  prohibited-field tests.
- Updated OpenAPI and the data dictionary.

## Local evidence

```text
Ruff: PASS
MyPy: PASS
Module boundaries: PASS
Django check: PASS
makemigrations --check --dry-run: PASS
Empty SQLite migration: PASS
Generated OpenAPI validation: PASS
docs/openapi.yaml validation: PASS
Focused Task67A: 27 passed / 2 PostgreSQL-only skipped locally
Full backend: 189 passed / 32 PostgreSQL-only skipped locally
Coverage: 87.04% (80% required)
Frontend lint + typecheck + build: PASS
Frontend UI-policy: 9 passed / 1 failed on legacy CSS baseline hashes; the
frontend tree is unchanged from BASE_SHA, so this pre-existing failure is not
attributed to Task67A. check:ui-policy: NO_RUN (blocked by that test failure)
git diff --check: PASS
```

## Historical pending state

The former Draft-PR, CI-pending, review-pending, and OPEN / READY / UNMERGED
states are historical. PR #6 is CLOSED / MERGED; backend PostgreSQL, frontend,
and smoke_restore are SUCCESS; and Security, Privacy, and Database are
APPROVED_WITH_NON_BLOCKING_NOTES.

Commander-message transport was also attempted through the mandated shared
Brave/Profile 13 path. It did not send: the existing browser was not launched
with the required control endpoint, and the helper requested closing it. The
repository instruction prohibits closing or replacing the shared session, so
no unsafe recovery was attempted. This document is the auditable handoff until
the employer supplies an authenticated controllable session.

## Explicit restrictions

```text
REAL_USERS: NOT_AUTHORIZED
FRONTEND_PUBLIC_SIGNUP: NOT_IMPLEMENTED / NOT_AUTHORIZED
GUARDIAN_RECOVERY: NOT_AUTHORIZED
PR_6_READY_TRANSITION: COMPLETED UNDER SEPARATE AUTHORIZATION
PR_6_MERGE: COMPLETED UNDER SEPARATE TASK67C AUTHORIZATION
TASK68A_MERGE: NOT_AUTHORIZED
DEPLOYMENT: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PROTECTED_CODESHO_PROMOTION: NOT_AUTHORIZED
```
