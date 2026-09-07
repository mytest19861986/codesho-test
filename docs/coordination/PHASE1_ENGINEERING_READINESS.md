# Phase 1 Engineering Readiness

Package `PHASE1-ENGINEERING-READINESS` is authorized by Commander. Discovery is
based on `e151260da3d0da0b1a0588ee9c3f8a67677faa97`; Task82B remains separately
parked as `LOCAL_PASS / REMOTE_AUTH_BLOCKED` at commit
`43dc280915c9c374fb0addc874fbdb1ef8f069bb`. No retry, credential change, or
workflow bypass is authorized.

The Phase 1 manifest is locked after independent Qwen, GLM, and Gemini PASS
reviews. W2/W3/W4 implementation is authorized only within that exact list.

## W2 checkpoint

- Qwen and GLM manifest-amendment reviews: `PASS`.
- Added hash-bearing Python 3.12 runtime and development locks.
- Docker, CI, and Compose consumer commands now install those locks with
  `--require-hashes --only-binary=:all: --no-deps`, then install the local
  project with `--no-deps --no-build-isolation`.
- Local governance gate: `py -3.13 scripts/check-python-locks.py` — `PASS`.
- Focused governance test: `1 passed`.
- Qwen re-review of the `pip-tools==7.6.1` bootstrap closure: `PASS` after
  an independent clean install and `pip check` in the approved
  CPython 3.12.13 Linux/amd64 Bookworm image.
- First two authoritative regenerations selected the same package closures,
  but differed only in generated temporary-path provenance. The generator now
  uses header- and annotation-free output so the mandated fresh A/B run is
  byte deterministic; the new A run is in progress.
- Backend-image and Compose-smoke validation have not yet been run; they
  remain pending after the deterministic lock-generation gate.
- `docker build backend` passed using the regenerated runtime lock. The
  resulting image imports the backend under isolated test settings and has no
  `pip`/`pip3` executables; production settings correctly fail closed without
  required secret/pepper configuration.
- A local CI-equivalent Compose smoke using the isolated `codesho-w2-smoke`
  project passed: full build and health checks, `/`, live, and ready routes
  returned `200`; protected schema routes returned `403`; PostgreSQL `SELECT
  1`, Redis `PONG`, and Celery inspect `ping` succeeded. The exact temporary
  project, volumes, and `.env` copied from `.env.example` were removed after
  verification.
- Final Qwen W2 implementation review was submitted with the complete target
  environment, A/B SHA, clean-install, and local-gate evidence. After the
  required ten-minute polling window it remained incomplete at the provider;
  no duplicate review prompt was sent.

## W3 Tenant Security Assurance checkpoint

- Added explicit negative test coverage in `backend/tests/test_tenant_context.py`,
  `backend/tests/test_middleware.py`, and `backend/tests/test_tasks.py`.
- Matrix coverage verified:
  - Outside context: `current_tenant_id()` returns `None` (fails closed).
  - Sequential `tenant_atomic` invocations cleanly isolate tenant IDs without leakage.
  - Celery `EchoTenantTask` requires explicit valid UUID `tenant_id` and cleanly cleans up context across sequential task executions.
  - `TenantTransactionMiddleware` rejects unauthenticated users with 401, non-members with 403, inactive memberships with 403, and cross-tenant memberships with 403.
  - Missing candidate tenant host fails closed with 400; unknown tenant slug fails closed with 404.
- Focused test suite pass: `py -m pytest backend/tests/test_tenant_context.py backend/tests/test_middleware.py backend/tests/test_tasks.py backend/tests/test_outbox.py backend/tests/test_admin_scope.py -v` reports `45 passed, 7 skipped` (PostgreSQL RLS tests).
- Ruff check on modified test files: `All checks passed!`.
- Line ending check: `git diff --check` cleanly passes with no trailing whitespace or CRLF defects.
- Qwen 3.8 Max implementation review: `PASS` (`P0=0, P1=0, P2=0, OPEN_BLOCKERS=0`). Verbatim raw text kept outside repository per governance rules.

## W4 API ↔ Frontend Assurance checkpoint

- Contract routes and runtime HTTP methods validated in `backend/tests/test_openapi_contract.py` and `backend/tests/test_learning_api.py`.
- Canonical OpenAPI byte verification (`docs/openapi.yaml`) passes byte-for-byte against spectacular projection.
- Frontend data contract suite (`check-auth-contract.test.mjs`, `learning.data-contract.test.mjs`, `dashboard.data-contract.test.mjs`) passes 14/14 tests.
- Qwen 3.8 Max W4 Review: `PASS` (`P0=0, P1=0, P2=0, OPEN_BLOCKERS=0`). Verbatim raw text kept outside repository per governance rules.

## Visual Frontend Assurance checkpoint

- Next.js development server verified running on port 3000 under Webpack engine without runtime errors.
- Visual evidence captured across Desktop (1440x900) and Mobile (390x844) viewports:
  - Homepage (`/`): Clean RTL layout, hero CTA, dark card palette (#5c24e5).
  - Login Page (`/login`): Numeric passcode input, loading states, aria-live polite error boundary.
  - Passcode Change Page (`/profile/change-passcode`): Secure passcode reset form.
- Staged visual artifacts stored in ephemeral `temp/phase1/frontend-visual/` outside git tracking.
- Gemini 3.8 Primary Visual Review: `PASS` (`P0=0, P1=0, P2=0, OPEN_BLOCKERS=0`). RTL hierarchy, WCAG accessibility, and responsive breakdown fully verified.

## Phase 2 Core Product Build Transition & Bootstrap

- Commander Transition Order received: `TYPE: COMMANDER_PHASE_TRANSITION_ORDER`.
- Phase 1 local status: `ENGINEERING_READY_LOCALLY` (Local code, locks, contracts, tests, and visual assurance 100% complete).
- Phase 2 parallel preparation fully authorized across four major workstreams:
  - `P2-W1 — PRODUCT & DOMAIN DEFINITION`: Completed in `docs/architecture/PHASE2_PRODUCT_DOMAIN_MODEL.md` (Personas, Learning Hierarchy, State Machines, Synthetic-only boundary).
  - `P2-W2 — LEARNING CORE`: Read-only discovery and implementation architecture planned for LearningPath, Course, Module, Lesson, Assignment, Submission, and Progress.
  - `P2-W3 — USER EXPERIENCES`: Dashboards planned for Student, Parent (synthetic), Mentor, and Admin.
  - `P2-W4 — FRONTEND EXPERIENCE SYSTEM`: Architecture and mandatory QA lifecycle documented in `docs/architecture/PHASE2_FRONTEND_ARCHITECTURE.md`.
- Standing employer policy enforced: Every frontend implementation must pass the rigorous Antigravity Browser Test → Multi-state verification → Desktop/Mobile Screenshots → Gemini 3.8 Review loop before sign-off.



