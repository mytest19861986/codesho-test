# Phase 1 Write Manifest — review draft

Status: `AMENDMENT APPROVED — QWEN + GLM MANIFEST REVIEW PASS`.

Base: `e151260da3d0da0b1a0588ee9c3f8a67677faa97`, an authorized descendant of
the Commander package base `e58281fb5fbaef22711ea16290bad6a8ef80ba24` (PR #45).
The descendant changes only the learner learning frontend flow; W4 will test
that current canonical behavior rather than overwrite it.

| Path | Workstream | State | Purpose | Expected change | Owner/reviewer | Collision/risk | Runtime impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `backend/pyproject.toml` | W2 | existing | Python dependency authority | Make supported lock/update inputs explicit only if discovery proves a gap | Codex / Qwen, GLM | medium | none intended |
| `backend/requirements.lock` | W2 | new | immutable runtime lock | Deterministic, hash-bearing generated lock if selected tooling supports it | Codex / Qwen, GLM | medium | build/install only |
| `backend/requirements-dev.lock` | W2 | new | immutable dev lock | Deterministic, hash-bearing generated dev lock if selected tooling supports it | Codex / Qwen, GLM | medium | build/test only |
| `scripts/check-python-locks.py` | W2 | new | lock-drift gate | Verify declared lock invariants without network resolution | Codex / Qwen, GLM | low | CI/test only |
| `backend/requirements/lock-tools.txt` | W2 | new | lock toolchain | Exact-pinned, hash-verified pip-compile toolchain; not an application dependency authority | Codex / Qwen | medium | generation only |
| `scripts/update-backend-locks.sh` | W2 | new | deterministic generation | Generate application locks from `backend/pyproject.toml` only | Codex / Qwen | medium | generation only |
| `backend/tests/test_dependency_governance.py` | W2 | new | governance tests | Assert lock hashes, source restrictions, and deterministic procedure metadata | Codex / Qwen, GLM | low | test only |
| `backend/Dockerfile` | W2 | existing | runtime install boundary | Consume runtime lock, then install local project with `--no-deps`; preserve stages, image, non-root runtime behavior | Codex / Qwen, GLM | high | build reproducibility only |
| `.github/workflows/ci.yml` | W2 | existing | CI install boundary | Consume dev lock and install local project `--no-deps`; preserve jobs, runners, services, triggers and Task82B pins | Codex / Qwen, GLM | high | CI only |
| `.github/workflows/compose-smoke.yml` | W2 | existing | smoke install boundary | Consume dev lock and install local project `--no-deps`; preserve smoke behavior and Task82B pins | Codex / Qwen, GLM | high | CI only |
| `docs/coordination/PHASE1_ENGINEERING_READINESS.md` | W2/W3/W4 | new | package evidence | Record reproducible procedure, results, and exclusions | Codex / Qwen, GLM, Gemini(W4) | low | none |
| `backend/tests/test_tenant_context.py` | W3 | existing | tenant context matrix | Add fail-closed/context-cleanup negatives | Codex / Qwen, GLM | medium | test only |
| `backend/tests/test_middleware.py` | W3 | existing | request tenant boundaries | Add missing/invalid/inactive/cross-tenant negatives | Codex / Qwen, GLM | medium | test only |
| `backend/tests/test_tasks.py` | W3 | existing | worker tenant context | Add task isolation and invalid-context negatives | Codex / Qwen, GLM | medium | test only |
| `backend/tests/test_outbox.py` | W3 | existing | outbox tenant boundary | Add tenant-context/idempotency negative coverage | Codex / Qwen, GLM | medium | test only |
| `backend/tests/test_learning_rls_postgres.py` | W3 | existing | PostgreSQL RLS evidence | Add direct cross-tenant/force-RLS negative assertions | Codex / Qwen, GLM | medium | test only |
| `backend/tests/test_admin_scope.py` | W3 | existing | operator/admin boundary | Add explicit tenant-denial assertions where applicable | Codex / Qwen, GLM | medium | test only |
| `backend/tests/test_openapi_contract.py` | W4 | existing | canonical API contract | Extend canonical contract verification only | Codex / Qwen, GLM, Gemini | medium | test only |
| `backend/tests/test_learning_api.py` | W4 | existing | read API contract | Add current canonical response/error checks where supported | Codex / Qwen, GLM, Gemini | medium | test only |
| `frontend/scripts/check-auth-contract.test.mjs` | W4 | existing | auth/session contract | Cover current CSRF/session/error handling assertions | Codex / Qwen, GLM, Gemini | low | test only |
| `frontend/src/features/auth/authClient.ts` | W4 | existing | API client remediation | Only a proven, localized integration defect | Codex / Qwen, GLM, Gemini | high | bounded only |
| `frontend/src/features/dashboard/learningClient.ts` | W4 | existing | learning contract client | Only a proven, localized contract defect | Codex / Qwen, GLM, Gemini | high | bounded only |
| `frontend/src/features/learning/LearningDataBoundary.tsx` | W4 | existing | learning API boundary | Only a proven, localized contract defect | Codex / Qwen, GLM, Gemini | high | bounded only |
| `frontend/src/features/learning/learning.data-contract.test.mjs` | W4 | existing | learning contract tests | Assert canonical current frontend/data boundary assumptions | Codex / Qwen, GLM, Gemini | medium | test only |
| `frontend/src/features/dashboard/dashboard.data-contract.test.mjs` | W4 | existing | dashboard contract tests | Assert canonical current dashboard assumptions | Codex / Qwen, GLM, Gemini | medium | test only |
| `docs/openapi.yaml` | W4 | existing | canonical schema | Generated artifact only if authoritative generation changes it | Codex / Qwen, GLM, Gemini | high | contract artifact only |
| `docs/coordination/CURRENT_TASK.md` | cross-cutting | existing | active status | Phase 1 status and approvals | Codex | low | none |
| `docs/coordination/PROJECT_STATE.md` | cross-cutting | existing | durable state | checkpoint only | Codex | low | none |
| `docs/coordination/CODEX_TO_COMMANDER.md` | cross-cutting | existing | Commander handoff | auditable checkpoint only | Codex | low | none |

## Binding boundaries

- All paths in the table are repository-root-relative. The W4 abbreviated
  entries mean exactly `frontend/src/features/dashboard/learningClient.ts`,
  `frontend/src/features/learning/LearningDataBoundary.tsx`,
  `frontend/src/features/learning/learning.data-contract.test.mjs`, and
  `frontend/src/features/dashboard/dashboard.data-contract.test.mjs`.
- `backend/pyproject.toml` may change only dependency-governance or supported
  lock-tool metadata. No runtime dependency add/upgrade/removal, build backend
  change, or runtime behavior change is authorized.
- A W4 source defect is *proven* only by a failing current-canonical OpenAPI,
  frontend contract, or synthetic browser/integration test reproduced on this
  base and recorded in Phase 1 evidence. The fix must be the smallest change
  that makes that test pass: no new feature, UX/layout/state expansion,
  endpoint addition, authentication-policy change, or unrelated refactor.
- `docs/openapi.yaml` is never hand edited. It may change only as output of
  `backend/manage.py spectacular --urlconf config.openapi_urls`, with
  `backend/tests/test_openapi_contract.py` retaining generated-spec/code sync.
- CI workflow files are deliberately absent from this manifest: new CI
  enforcement is deferred. The added tests/scripts are local gates and are
  eligible for existing relevant CI only without workflow edits.
- Task82B non-overlap is verified: its only workflow paths are
  `.github/workflows/ci.yml` and `.github/workflows/compose-smoke.yml`, neither
  of which appears here. `PHASE1_ENGINEERING_READINESS.md` is additive,
  phase-level documentation and does not replace any fixed coordination file.

No `temp/phase1/**` relay material is proposed. Any path not listed above,
including a runtime remediation path, requires a reviewed manifest amendment.

Review disposition: Qwen revision-2 `PASS`; GLM revision-2 `PASS`; Gemini
revision-2 `PASS`. Implementation is authorized only within this exact manifest.

## W2 amendment A

Commander approved the three W2 consumer paths above subject to Qwen and GLM
review. `backend/Dockerfile` may replace only unconstrained dependency
installation with approved runtime-lock consumption followed by local
`--no-deps` installation. The two workflow files may replace only the existing
editable-install resolution with dev-lock consumption followed by local
`--no-deps` installation. They must preserve jobs, runners, services, triggers,
and every Task82B Action/image pin byte-for-byte except mechanical reconciliation
in a shared command block. No Python/base-image/runner/service/action version,
new workflow job, package-manager, application-source, or architecture change
is authorized. Required W2 evidence includes no active resolving `pip install .`
or `pip install -e '.[dev]'`, two byte-identical regenerations, clean lock-based
install plus `pip check`, and affected CI-equivalent validation.

### Amendment A precision controls

- Lock mapping is fixed: `backend/Dockerfile` consumes only
  `backend/requirements.lock`; `.github/workflows/ci.yml` consumes
  `backend/requirements-dev.lock`; `.github/workflows/compose-smoke.yml`
  consumes `backend/requirements-dev.lock` because its isolated Python
  containers execute pytest. Each local project installation follows with
  `pip install --no-deps`.
- “Mechanical reconciliation” means line movement or whitespace only. Every
  Task82B `uses:` SHA/comment and service-image digest value must be retained
  byte-for-byte; version, SHA, digest, tag, runner, job, service, trigger, and
  permission changes are forbidden.
- The resolver proof scans every active backend build/CI/Compose command. An
  external dependency installation must have both an approved lock input and
  `--require-hashes`; local project installation must use `--no-deps`. Any
  other `pip install`, index/extra-index flag, unpinned requirements input, or
  build-isolation resolver is a failure.
- Discovery inventory found Python installation commands only in
  `backend/Dockerfile`, `.github/workflows/ci.yml`, and
  `.github/workflows/compose-smoke.yml`; no separate restore workflow, script,
  or Dockerfile installs Python dependencies. A final repository scan must
  re-prove this assertion.
- CI-equivalent validation is defined as: build the amended backend image;
  execute the backend install/test command sequence in a clean Python 3.12
  container with the same environment/service endpoints where locally
  available; run Compose smoke if Docker is available, otherwise record
  `BLOCKED_LOCALLY` and require remote evidence. This does not authorize new
workflow behavior.

Manifest-review evidence: Qwen and GLM each returned `PASS` for the fixed
lock mapping, the `--require-hashes` / `--no-deps` resolver boundary, the
Task82B byte-preservation constraint, and the CI-equivalent validation plan.
Their approvals apply to this Manifest policy only; implementation evidence
remains required before W2 can pass.

## W2 amendment B: lock-tool provenance

Commander authorized `backend/requirements/lock-tools.txt` and
`scripts/update-backend-locks.sh`. `backend/pyproject.toml` remains the sole
application dependency authority. A one-time disposable bootstrap may create a
candidate tool lock from exact `pip-tools` and real transitive artifacts whose
hashes are recorded; it is not authoritative evidence. Qwen must review the
candidate tool lock before fresh hash-locked CPython 3.12.13/Linux amd64/
Bookworm containers run authoritative application-lock regeneration. No third
path is authorized for lock-tool inputs. The script must consume only
`backend/pyproject.toml`, `lock-tools.txt`, and its explicit output paths.
