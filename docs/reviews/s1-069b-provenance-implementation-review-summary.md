# Task69B Provenance Implementation Review Summary

Status: `REMEDIATION_REQUIRED / DRAFT_MUST_REMAIN`

Task: `SPRINT1-ADULT-SIGNUP-PROVENANCE-SYNTHETIC-IMPLEMENT-69B`
Base: `27a8626d29bfa7e21c5e770455db6b20a4521ccc`

## Scope

This review covers only the nine Task69B allow-listed files and the internal
synthetic `Option B` provenance contract. It does not authorize real users,
Production, deployment, release, public API, backfill, providers, or PR #5.

## Implemented contract inspected

- Provenance is a separate append-only model with only opaque UUIDs, controlled
  constants, and a UTC timestamp.
- New provenance is created only when a new attestation is created, inside the
  same `tenant_atomic` transaction as the attestation and audit append.
- Replay uses the existing attestation and creates no new provenance.
- PostgreSQL migration enables FORCE RLS, checks transaction tenant context,
  validates the attestation tenant through a trigger, rejects mutation, and
  grants runtime INSERT only.
- The request/response, OpenAPI, and production-disabled guard remain
  unchanged.

## Local verification

```text
makemigrations --check --dry-run: PASS
ruff (focused files): PASS
mypy (focused source/migration, backend config): PASS
django check: PASS
focused adult signup tests: PASS (28 passed; 4 PostgreSQL-only skipped)
full backend tests (SQLite): PASS (190 passed; 34 skipped)
git diff --check: PASS
Docker Compose local: unavailable because DATABASE_MIGRATOR_URL is not configured
```

The PostgreSQL-only RLS, grant, trigger, tenant-linkage, and role-atomicity
tests must pass in CI or an explicitly configured real PostgreSQL role
environment. SQLite results are not treated as evidence for those gates.

## Review disposition

Commander independent review `COMMANDER_TASK69B_INDEPENDENT_REVIEW_20260726_07`
returned `CHANGES_REQUIRED` on head `b8f2d103e5655a547fb00554c64df85f3de64caa`.

- `69B-DB-01` (`P1`, blocking): PostgreSQL CI failed because FORCE RLS test
  reads and mutation assertions lacked tenant context. Disposition: fixed by
  wrapping provenance reads in `tenant_atomic`, running migrator mutation
  assertions with the expected tenant context, and making cross-tenant and
  missing-context cases explicit. A new head and CI run are required.
- `69B-DOC-01` (`P2`, required): the project-state CI wording was ambiguous
  after the failed Task69B run. Disposition: the current Task69B status is now
  recorded as PostgreSQL CI `FAILED / REMEDIATION_REQUIRED` and Ready/Merge
  blocked; prior green statements remain historical.

Observed CI on the reviewed head:

```text
backend: FAILURE (run 30216804608)
frontend: SUCCESS (run 30216804608)
smoke_restore: SUCCESS (run 30216804605)
```

The PR must remain Draft until the replacement head passes PostgreSQL/RLS,
frontend, smoke_restore, exact-file, and independent re-review gates.

Remediation head: `889d1e9` (pushed to PR #9). Local focused and full SQLite
tests remain green. Replacement CI is green: CI run `30217280624` and Compose
smoke_restore run `30217280594`. Independent re-review remains required.
