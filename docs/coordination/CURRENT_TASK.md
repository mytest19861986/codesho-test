# Current Task: P9-CONTROLLED-ACTIVATION-READINESS-REHEARSAL
 
- **COMMANDER_P9_START_AUTHORIZATION**: `GRANTED`
- **P9_STATUS**: `REHEARSAL_COMPLETE_AWAITING_FINAL_ACCEPTANCE`
- **P9_MODE**: `SYNTHETIC_ONLY`
- **P9_OBJECTIVE**: `TURN_P8_DESIGNED_CONTROLS_INTO_EXECUTABLE_SYNTHETIC_CONTROLS`
- **P9_REHEARSAL_MATRIX**: `20/20 PASS`
- **P9_NEGATIVE_MATRIX**: `40/40 PASS`
- **AUTOMATED_SUITE**: `25/25 PASSED in 0.42s`
- **P9_HEAD**: `e4a9a498a590f70b2248aea6d5bfffe1b08563db`
- **FLEET_CONSENSUS**: `Qwen PASS (0 Blockers) | GLM PASS (0 Blockers) | Gemini NOT_APPLICABLE`
- **ACCEPTED_BASELINES**:
  - `FRONTEND_HEAD`: `83f9ae322f4d3b6095d1649e07d329d7ad8d407a` (`COMPLETE_FINAL_ACCEPTED`)
  - `BACKEND_HEAD`: `7c4c1f09c876b6345b3550103a6ef30265376478` (`COMPLETE_FINAL_ACCEPTED`)
  - `P8_DISCOVERY_STATUS`: `COMPLETE_FINAL_ACCEPTED` (13 Canonical Artifacts)
- **CANONICAL_TENANT_KEY**: `app.current_tenant`
- **GOVERNANCE_LOCKS**: `REAL_PILOT: LOCKED` | `REAL_DATA: LOCKED` | `REAL_ORGANIZATION_ONBOARDING: LOCKED` | `REAL_CONSENT_ACTIVATION: LOCKED` | `REAL_SMS_EMAIL: LOCKED` | `REAL_PAYMENT: LOCKED` | `PUBLIC_SIGNUP: LOCKED` | `PRODUCTION: LOCKED` | `MERGE_TO_MAIN: LOCKED_FOR_MANAGER`
- **PROJECT_STATE**: `READY_FOR_HUMAN_MANAGER_GO_NO_GO_DEFER_DECISION_PACKAGE`

---

# Previous Task: SPRINT1-SECURITY-CLEANUP-SCHEDULING-ARCHITECTURE-77A
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
