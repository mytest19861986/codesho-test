# Current Task: SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CLOSEOUT-80C

## Active Task80C coordination closeout — 2026-08-11

- Status: `IN_PROGRESS / COORDINATION_ONLY`.
- Validated main / base: `d1da19f76e7f7bae48b836029873272d6cac642a`.
- Task80B: `COMPLETE`; PR `#39` is `MERGED`.
- Qwen and Claude implementation gates: `PASS` (`P0=0`, `P1=0`, `OPEN_BLOCKERS=0`).
- Post-merge CI `31477878067` and Compose `31477878000`: `SUCCESS`.
- Scope is coordination closeout only. Production, deployment, release, and protected `codesho` remain unauthorized.

# Historical Task79A record

## Active Task79A handoff — 2026-08-10

- Task: `SPRINT1-DOMAIN-LEARNING-READ-MODEL-ARCHITECTURE-79A`
- Status: `COMPLETE / ARCHITECTURE_ONLY / CLAUDE_PASS`
- Base SHA: `cb0a09df5e566dd14be329d22333fd16c82d6378`
- Branch: `codex/task79a-learning-read-model-architecture`
- Worktree: `G:\project\codesho\codesho-task79a-learning-read-model-architecture`
- Exact write allow-list: the Task79A decision, this file,
  `docs/coordination/PROJECT_STATE.md`, `docs/coordination/CODEX_TO_COMMANDER.md`,
  and the Task79A review summary.
- No runtime implementation, migration, SQL, RLS, API/OpenAPI, frontend,
  fixture, workflow, Compose, deployment, release, merge, or protected
  `codesho` action is authorized.
- `origin/main` was verified equal to the required base before worktree creation.
- Decision: minimum V1 is Course, Lesson, ClassCohort, ClassMembership, and
  conditional LessonProgress; unsupported fields remain unavailable.
- Claude gate: `CLAUDE_TASK79A_LEARNING_READ_MODEL_ARCHITECTURE_REVIEW_01_V1`
  returned `PASS / P0=0 / P1=0 / OPEN_BLOCKERS=0` with
  `READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.
- Three non-blocking successor notes: pin field bounds, choose append-only
  progress semantics, and set a maximum page size.
- Exact-content follow-up `CLAUDE_TASK79A_LEARNING_READ_MODEL_ARCHITECTURE_REVIEW_02_EXACT_HEAD_V1`
  returned `PASS (content-only) / P0=0 / P1=0 / OPEN_BLOCKERS=0`; Claude's
  cryptographic provenance limitation is recorded for Commander.
- Next action: await separate Commander-authorized implementation task.

## TASK77C_ACTIVE_CHECKPOINT_20260809

- TASK_ID: `SPRINT1-SECURITY-CLEANUP-CLAIM-LEASE-CLEAN-INTEGRATION-77C`
- BASE_SHA: `39c35a50965184681599a0ade0dd65f34b7aa548`
- BRANCH: `codex/task77c-cleanup-claim-lease-clean-integration`
- STATUS: `IMPLEMENTATION / LOCAL_GATES_PARTIAL`
- SOURCE_REFERENCE: `47cb8acc9290bdff927b63679d0a07e85132f06f`
- COMPLETED: clean worktree from exact base; claim persistence, DB-time lease
  operations, fencing, transactional Outbox acquisition, durable retry/DEAD
  task flow, RLS migration and focused assertions transferred.
- LOCAL_EVIDENCE: focused `9 passed, 3 skipped`; Ruff/MyPy/boundaries/Django/
  migration/compileall/diff checks pass. Full backend `217 passed, 52 skipped,
  1 failed` only on the pre-existing out-of-scope OpenAPI LF/CRLF mismatch.
- CHECKPOINT_HEAD: `338ee7a438f7fc55a6486f573e988a3e7ce78c81`
- REMOTE_EVIDENCE: CI `31294215288` SUCCESS; Compose `31294215324` SUCCESS.
- CLAUDE: `CLAUDE_TASK77C_CLEAN_INTEGRATION_HARD_GATE_01_V1` PASS with zero
  open/P0/P1 blockers; P2 notes are non-blocking and recorded in review summary.
- FINAL_CLAUDE_REVALIDATION: `CLAUDE_TASK77C_CLEAN_INTEGRATION_HARD_GATE_02_V1`
  PASS with zero open/P0/P1 blockers for the docs-only successor HEAD.
- NEXT: record this evidence in the final coordination checkpoint, then any
  post-checkpoint HEAD requires fresh exact-head CI/Compose/Claude evidence.
- EXCLUSIONS: no governance replacement, scheduler/Beat/cron, public API,
  protected `codesho`, Release, Deployment, Production or Alpha action.

## Active Task77A handoff — 2026-08-08

- Task: `SPRINT1-SECURITY-CLEANUP-SCHEDULING-ARCHITECTURE-77A`
- Status: `INSPECTION COMPLETE / DOCS-ONLY IMPLEMENTATION IN PROGRESS`
- Base SHA: `cb967c26e0faf9a5868e9adc74d59a09c6a42b99`
- Branch: `codex/task77a-cleanup-scheduling-architecture`
- Exact write allow-list: the Task77A decision document, this file,
  `docs/coordination/PROJECT_STATE.md`,
  `docs/coordination/CODEX_TO_COMMANDER.md`, and the Task77A review summary.
- No Python, settings, Celery, migration, workflow, Compose, scheduler, or
  worker implementation changes are authorized.
- Inspection found the current cleanup task already uses explicit tenant UUID
  validation, `BaseTenantTask`, `tenant_atomic`, bounded work, database time,
  row locking, and no registered periodic schedule.
- Recommended architecture: bounded database-authoritative work claims with
  short leases, followed by one explicit tenant task per claim.

- Owner: Codex, directed by Commander AI.
- Status: `IMPLEMENTED / FOCUSED_GATES_PASS / REMOTE_GATES_PASS / CLAUDE_PASS`
- Base SHA: `cb967c26e0faf9a5868e9adc74d59a09c6a42b99`.
- Branch: `codex/task76a-passcode-change-cleanup-hardening`.
- Scope: tenant-scoped passcode-change challenge cleanup hardening only; no
  migration, beat schedule, global fan-out, or protected-repository promotion.
- Current checkpoint: cleanup settings are now represented in `.env.example`
  and validated as bounded configuration at settings load. Existing cleanup
  orchestration and tenant task code were preserved because inspection found
  no confirmed defect in those paths.
- Verification: focused cleanup tests pass (`7 passed`); related completion/E2E
  tests pass (`7 passed, 3 PostgreSQL-only skipped`); backend-cwd full suite is
  `213 passed, 49 skipped, 1 failed`. The sole failure is the unrelated
  OpenAPI canonical-byte test detecting generated LF versus committed CRLF in
  `docs/openapi.yaml`, outside the task allow-list. The root-cwd compose-path
  failure disappears when rerun from the official `backend` cwd.
- Claude hard gate: `CLAUDE_TASK76A_PASSCODE_CHANGE_CLEANUP_IMPLEMENTATION_REVIEW_01_V1`
  returned `PASS / OPEN_BLOCKERS 0 / P0 0 / P1 0`. One non-blocking note asks
  for explicit audit wording that the PostgreSQL cleanup function comes from a
  prior authorized migration; no code remediation was required.
- Draft PR: `https://github.com/mytest19861986/codesho-test/pull/22`.
- Remote CI for commit `8710d96`: backend SUCCESS, frontend SUCCESS, and
  smoke_restore SUCCESS (workflow run `31263338566` / compose run
  `31263338543`).
- Documentation checkpoint commit `6eb7a30` also passed remote CI: backend and
  frontend SUCCESS in run `31263485129`; smoke_restore SUCCESS in run
  `31263485122`.

- Owner: Codex, directed by Commander AI.
- Status: `COMPLETE / LOCAL_GATES_PASS / CI_COMPOSE_PASS / CLAUDE_PASS`.
- Base branch: `codesho-test/main`.
- Base SHA: `dca0800fd74fb3e852aacb9122e6c533538d2629`.
- Branch: `codex/task73b-openapi-contract-drift`.

## Goal

Eliminate OpenAPI contract drift through an isolated `drf-spectacular`
projection while preserving runtime URLs, auth, sessions, CSRF, cookies,
tenant middleware and business logic.

## Exact allow-list

1. `backend/config/openapi_schema.py`
2. `backend/config/openapi_urls.py`
3. `backend/config/settings/base.py`
4. `backend/tests/test_openapi_contract.py`
5. `docs/openapi.yaml`
6. `.github/workflows/ci.yml`
7. `docs/coordination/CURRENT_TASK.md`
8. `docs/coordination/PROJECT_STATE.md`
9. `docs/coordination/CODEX_TO_COMMANDER.md`
10. `.github/workflows/compose-smoke.yml` (Commander-approved CI remediation)

No other file may change.

## Acceptance

- Generated schema is deterministic and exposes exactly six approved operations.
- Generated schema is byte-equal to `docs/openapi.yaml`; schema and Swagger
  are fail-closed for anonymous and non-staff users.
- Runtime/projection path names, callback identities and HTTP methods are
  parity-tested; unapproved endpoints are absent.
- Runtime CSRF, session, cookie, status and Retry-After behavior is unchanged.
- Ruff, MyPy, Django check, migration check, focused/full backend tests,
  schema validation and `git diff --check` pass.
- Claude implementation Review 02 passed with zero open blockers. Review 03's
  only P1 (real Compose execution) is resolved by successful remote execution;
  final evidence-closure Review 04 passed with zero open blockers.

## Remote evidence

- Commit: `264d85d06fc7c48c4eb2a721e69f53b58a57f7c5`.
- CI: `31078717976` — SUCCESS (backend and frontend).
- Compose smoke and restore: `31078717914` — SUCCESS.
- Documentation checkpoint CI: `31078984692` — SUCCESS.
- Documentation checkpoint Compose smoke and restore: `31078984491` — SUCCESS.
- Final Claude evidence-closure review:
  `CLAUDE_TASK73B_CI_COMPOSE_EVIDENCE_CLOSURE_REVIEW_04_V1` — PASS / 0 open
  blockers.
- Draft PR: `https://github.com/mytest19861986/codesho-test/pull/16` (Draft;
  Ready, merge and protected-repository promotion remain forbidden).

`FINAL_MARKER: CLAUDE_TASK73B_OPENAPI_CONTRACT_IMPLEMENTATION_REVIEW_02_V1`

## Authority and exclusions

Commit, normal branch push and Draft PR are authorized after final gates.
Direct-main, Ready, merge, force-push and branch deletion are forbidden.

No model, schema, migration, API/OpenAPI, UI, code/state-machine implementation,
PII/real data, account, credential, session, active membership, role, public
endpoint, email/SMS/OAuth/provider integration, Guardian/Recovery
implementation, deployment, Alpha, Production or protected `codesho`
promotion is authorized.

## TASK77A_CLAUDE_GATE_RESULT_20260808

Claude hard gate completed against `f0692d53cdeb1d65857d3efeb35a49dc709c4ab2`.
Verdict: `PASS`; `OPEN_BLOCKERS: 0`; `P0: 0`; `P1: 0`. This closes the
architecture-only review gate. It does not authorize implementation, merge,
release, deployment, promotion, or protected-repository changes.

## Active Task78A handoff - 2026-08-09

- Task: `SPRINT1-UI-STUDENT-DASHBOARD-FOUNDATION-78A`
- Status: `IMPLEMENTED / LOCAL_UI_GATES_PASS / GEMINI_ATTACHMENT_REVIEW_PENDING`
- Base SHA: `4c52816a15d34ce28955034f2ab77c04bd733506`
- Branch: `codex/task78a-student-dashboard-ui-foundation`
- Scope: Persian-first RTL student dashboard UI foundation only; no backend,
  API, auth/session, database, migration, OpenAPI, dependency, workflow,
  deployment, Production, or protected-repository changes.
- Local evidence: ESLint, TypeScript, dashboard a11y (`2 passed`), Next build,
  responsive viewport checks at 360/390/768/1024/1440, and diff-check passed.
- Gemini: primary launcher failed on Firefox; Chrome retry cited unrelated
  files; exact attachment upload failed with `fileChooser.setFiles failed:
  Not allowed`. No Gemini PASS is claimed.
- Next action: push checkpoint, provide versioned GitHub links for exact files,
  obtain attachment-verified Gemini review, then run remote CI/Compose.
