# Task82A Post-Task81B Readiness Gap Audit

## Scope and evidence

- Base SHA: `e58281fb5fbaef22711ea16290bad6a8ef80ba24` (`origin/main`).
- Audit-only; no runtime, application, migration, workflow, or deployment file
  is changed by this task.
- Codex inspected the current tree, task history, coordination records, CI and
  Compose workflows, dependency manifests, backend/frontend test structure,
  architecture decisions, and synthetic-only/legal gates.
- Independent reviews: Qwen completed; GLM supplied an explicitly
  repository-unverified risk framework. Codex accepted only claims corroborated
  by repository evidence.

## Confirmed findings

### F-01: coordination state is stale

- STATUS: `DOCUMENTATION_DRIFT`; SEVERITY: `P2`; DOMAIN: `DOCUMENTATION`.
- Evidence: `docs/coordination/CURRENT_TASK.md` and `PROJECT_STATE.md` lead
  with Task80C, while `git log` at the base contains merged Task81B (#42),
  Task82A (#43), and Task83A (#44).
- Why it matters: task ownership, reviewed base, and release evidence can be
  evaluated against an obsolete state.
- Disposition: this Task82A updates the coordination checkpoint; no product
  behavior is implicated.

### F-02: mutable CI action and service references

- STATUS: `CONFIRMED_GAP`; SEVERITY: `P2`; DOMAIN: `SUPPLY_CHAIN`.
- Evidence: `.github/workflows/ci.yml` uses `actions/checkout@v4`,
  `actions/setup-python@v5`, `actions/setup-node@v4`, `postgres:17-alpine`,
  and `redis:7-alpine`; `compose-smoke.yml` also uses mutable action tags.
- Why it matters: tag movement can change build or test behavior outside a
  reviewed commit.
- Dependency: normal Commander authorization and an exact task allow-list; the
  implementation itself needs no legal, business, or production decision.
- Recommended disposition: a bounded supply-chain pinning inventory and
  remediation task; do not silently change CI references.

### F-03: Python dependency reproducibility/update governance is incomplete

- STATUS: `CONFIRMED_GAP`; SEVERITY: `P2`; DOMAIN: `SUPPLY_CHAIN`.
- Evidence: the tree has `backend/pyproject.toml` with bounded version ranges
  and frontend `package-lock.json`, but no Python lockfile and no Dependabot or
  Renovate configuration was found.
- Why it matters: Python transitive dependency resolution is not committed or
  governed by an automated update policy.
- Recommended disposition: separate dependency-governance design task covering
  Python lock tooling, update cadence, vulnerability review, and CI impact.

### F-04: operational observability is policy-deferred, not production-ready

- STATUS: `DEFERRED_BY_POLICY`; SEVERITY: `P2`; DOMAIN: `OPERATIONS`.
- Evidence: `docs/sprint-zero/deployment-observability-dr.md` records provider,
  alert recipient, metrics storage, off-host backup destination, RPO/RTO and
  successful production drill as pre-launch decisions. No monitoring provider
  or production environment is authorized.
- Why it matters: this is a pre-production gate, but it is not a defect in the
  current synthetic/test environment.
- Recommended disposition: keep in `DO_NOT_START_YET` pending employer/provider
  and production authorization.

### F-05: real-user readiness is blocked by law and employer authority

- STATUS: `PENDING_HUMAN_DECISION`; SEVERITY: `P0`; DOMAIN: `PRIVACY`.
- Evidence: `docs/decisions/2026-08-05-real-user-onboarding-legal-boundary.md`
  records required decisions as `PENDING_COUNSEL`/`PENDING_EMPLOYER`; synthetic
  boundaries explicitly prohibit real-user activation.
- Why it matters: no current code, documentation, test, or release claim may
  represent the system as approved for real users.
- Recommended disposition: no engineering implementation task until the listed
  legal and employer gates are explicitly resolved.

## Controls confirmed as already implemented

- `ALREADY_IMPLEMENTED / SECURITY`: PostgreSQL CI uses runtime and migrator
  roles, runs migrations, and executes the backend suite with coverage in
  `.github/workflows/ci.yml`; RLS negatives exist in
  `backend/tests/test_tenant_context.py` and
  `backend/tests/test_learning_rls_postgres.py`.
- `ALREADY_IMPLEMENTED / OPERATIONS`: `compose-smoke.yml` runs health checks,
  PostgreSQL backup/restore, and verifies restored ownership, runtime grants,
  audit schema restrictions, and security-definer function privileges.
- `ALREADY_IMPLEMENTED / FRONTEND`: frontend CI runs UI-policy tests, lint and
  type checking; dashboard has data-contract and accessibility tests.
- `PARTIALLY_IMPLEMENTED / TESTING`: contract, RLS, role, Compose and frontend
  checks exist, but there is no repository evidence of browser E2E coverage or
  a cross-execution-path tenant-coverage matrix. This is a backlog candidate,
  not evidence of a current isolation failure.

## Ranked engineering backlog

### NEXT_1 — TASK82B-SUPPLY-CHAIN-PINNING-AND-DEPENDENCY-GOVERNANCE

- Objective: define and implement approved immutable pinning and reproducible
  dependency governance for Actions, service/base images and Python packages.
- Priority: addresses confirmed F-02/F-03 without product-scope expansion.
- Dependencies: normal task authorization and an exact implementation
  allow-list; no unresolved legal or business decision.
- Risk: R2; blast radius: CI, manifests and dependency tooling only.
- Proposed allow-list: workflow files, approved dependency-lock/config files,
  supply-chain documentation, focused tests.
- Verification: deterministic install, CI action/image pin scan, dependency
  policy checks, `git diff --check`.
- Reviewer: Qwen, then Claude only if the approved scope changes authentication,
  secrets, production artifact signing, or deployment trust boundaries.

### NEXT_2 — TASK82C-TENANT-ISOLATION-COVERAGE-MATRIX

- Objective: map request, service, task, management-command and admin paths to
  existing tenant/RLS negative coverage and add only approved missing tests.
- Dependencies: no legal decision; must preserve current RLS architecture.
- Risk: R2; blast radius: tests and audit documentation.
- Verification: PostgreSQL CI coverage and explicit negative-path mapping.
- Reviewer: Qwen; Claude required only for an R3/R4 isolation ambiguity.

### NEXT_3 — TASK82D-API-FRONTEND-CONTRACT-ASSURANCE

- Objective: identify and add bounded critical response/error/pagination
  contract coverage for existing endpoints only.
- Dependencies: current OpenAPI/runtime contract remains authoritative.
- Risk: R2; blast radius: existing API/frontend tests and contract docs.
- Verification: backend/frontend contract tests, OpenAPI parity, typecheck.
- Reviewer: Qwen and Gemini if material UI states are affected.

### NEXT_4 — TASK82E-PRODUCTION-OBSERVABILITY-DECISION-PACKET

- Objective: turn existing pre-launch observability/DR requirements into a
  provider-neutral decision packet.
- Dependencies: employer/provider and production authority.
- Risk: R2; blast radius: documentation only.
- Verification: decision completeness, no runtime activation.
- Reviewer: GLM.

### NEXT_5 — TASK82F-RELEASE-READINESS-CAPABILITY-STATEMENT

- Objective: reconcile public/internal capability wording with synthetic-only,
  non-production status.
- Dependencies: employer approval for any external wording.
- Risk: R1; blast radius: approved documentation/copy only.
- Verification: claim inventory and legal-boundary consistency.
- Reviewer: GLM and employer.

## Recommended next implementation task

`TASK82B-SUPPLY-CHAIN-PINNING-AND-DEPENDENCY-GOVERNANCE` is the single
recommended next implementation task. It is bounded, non-duplicative,
engineering-ready under the normal task-authorization process, and does not
depend on real-user, legal, provider, or production activation authority.

## Do not start yet

- Real-user onboarding, public availability, provider integrations, deployment,
  release, Production or protected-repository promotion: blocked by legal and
  employer authority.
- Production observability provider/alerting/DR execution: blocked by provider,
  production and employer decisions.
- Any architecture change to tenant/RLS, authentication or runtime roles:
  requires a separately approved task and security review.

## Review reconciliation

- Qwen: correctly identified stale coordination state and mutable Action/image
  references. Its RLS/restore, contract and frontend coverage concerns were
  checked against local evidence; RLS and restore were confirmed controls,
  while E2E/coverage-matrix absence is treated as a bounded future-assurance
  candidate rather than a claimed defect.
- GLM: its observability, DR and provenance suggestions were not accepted as
  direct findings because it declared no repository access. Repository evidence
  supports classifying them as production-policy deferred, not P0 defects.
- No unresolved R3/R4 finding was discovered.

## Verification record

- `git rev-parse HEAD` exited `0` and identified the required base as
  `e58281fb5fbaef22711ea16290bad6a8ef80ba24` before Task82A edits.
- `git log --oneline -15` exited `0` and showed the merged Task81B (#42),
  Task82A (#43), and Task83A (#44) history used in F-01.
- Focused `rg`/file inspection of coordination records, decisions, workflows,
  manifests, runtime configuration and backend/frontend test files exited
  successfully; the cited repository paths are the authoritative evidence.
- No application test suite was re-run: this is a documentation-only audit and
  all runtime claims are framed as source/workflow evidence, not fresh runtime
  execution. Final `git diff --check` and changed-file allow-list validation
  are required before commit.
