# S1-004 Immutable Credential Security Audit Review Summary

## Review 01: migration and PostgreSQL enforcement

Claude reviewed only the current S1-004 audit migration after a bounded,
versioned request. The reviewed attachment SHA-256 was
`AF8F188DC2EDC9E14028C3F9DC6AB79E1595E0131968F5C357A728BD45E2D112`; the
required completion marker was received:
`CLAUDE_S1_004_AUDIT_MIGRATION_REVIEW_01_COMPLETED`.

### Findings and disposition

- F3/A1 (P0): `rejected-with-evidence` by Commander. No audit-schema
  `ALTER DEFAULT PRIVILEGES` grants broader runtime access; runtime access is
  explicitly insert-only and verified in PostgreSQL CI and restore checks.
  `test_audit_schema_has_no_runtime_default_read_or_mutation_privileges`
  prevents this regression.
- F2 (P1): `rejected-with-reason`. Migrations run under the fixed
  `codesho_migrator` role; the table ownership test verifies that resulting
  owner. An additional owner role is not approved architecture.
- F6 (P1): `accepted-as-P2-hardening`. The migration now states that the
  interpolated event constants are trusted literals and must never become
  runtime/configuration input.
- F9 (P1): `resolved`. Compose smoke/restore verifies audit ownership and
  runtime insert-only grants after a real restore.
- F1/F4/F5/F7/F8/F10: non-blocking controls or intentional design decisions;
  no corrective change required.

## Review 02: typed append service

Claude reviewed only `security_audit.py` after the migration review. The
reviewed attachment SHA-256 was
`C04639A46B7F5497816243FBAD0224EA7ADA0C4427C477DFE8CBA86B727787EF`; the
required completion marker was received:
`CLAUDE_S1_004_SERVICE_REVIEW_02_COMPLETED`.

### Findings and disposition

- F1 (P0): `resolved-with-repository-evidence` by Commander. Migration
  `0002` and the state model define the nullable unique `idempotency_key`;
  PostgreSQL duplicate-idempotency tests and CI verify the real DDL.
- F2 (P1): `partially accepted`. Nullable keys are intentional: events with
  no idempotency key must both be inserted. The service now uses
  `ON CONFLICT (idempotency_key) DO NOTHING`, so future constraints and a
  duplicate `event_id` cannot be treated as idempotency. PostgreSQL requires
  SELECT privilege on an explicit conflict target; direct runtime INSERT then
  failed in CI, as expected from the privilege model. Commander therefore
  approved migration `0004`: the explicit insert executes only inside the
  narrowly scoped `SECURITY DEFINER` function
  `audit.append_identity_security_event`. It is owned by `codesho_migrator`,
  has `search_path = pg_catalog, pg_temp`, schema-qualifies the audit table,
  revokes PUBLIC execution, and grants only EXECUTE to `codesho_runtime`.
  Direct runtime INSERT is revoked. A conflict returns
  `AppendAuditResult(event_id=None, created=False)` because runtime cannot
  identify the existing event.
- F3 (P2): `accepted`. Only Django `DatabaseError` is converted to the
  privacy-safe `SecurityAuditError`; programming and validation errors remain
  distinguishable.
- F5/F6/F7: verified by the explicit conflict target, single-statement insert,
  and no producer/API wiring.
- F8 (P2): `accepted`. `reason_code` is now an approved `ReasonCode`
  `StrEnum`, free-form values are rejected before persistence, and immutable
  migration `0003` adds the matching PostgreSQL CHECK constraint. The allowed
  values are non-sensitive classifications only; secrets, tokens, UUIDs, IPs,
  device digests, and arbitrary text are prohibited.

## Local review and verification

- The audit table has no foreign key to a user table and no metadata column.
- `codesho_runtime` is granted only `USAGE` on `audit` and `INSERT` on the
  table; `SELECT`, `UPDATE`, `DELETE`, and `TRUNCATE` are explicitly revoked.
- PostgreSQL triggers reject update, delete, and truncate. The reverse
  migration raises `IrreversibleError` to protect retained evidence.
- Runtime has no direct table privilege on the audit ledger. Its sole write
  capability is execution of the restricted append function; tests verify the
  function owner, `SECURITY DEFINER`, hardened search path, runtime EXECUTE,
  and absence of PUBLIC EXECUTE.
- Local checks passed: Ruff, MyPy, migration-drift check, 40 backend tests,
  frontend lint/typecheck/build, shell syntax checks, Compose configuration,
  and `git diff --check`.

## CI and restore verification

The real PostgreSQL gates passed for checkpoint `c3f52f6`:

- CI `29477200441` completed successfully, including empty-database migrations,
  runtime/migrator role tests, OpenAPI validation, and the full backend/frontend
  quality gates.
- Compose smoke and restore `29477200386` completed successfully, including
  full-stack startup, audit-schema backup/restore ownership and insert-only
  grant verification.

Local Docker remains unavailable on this workstation, so no local container
result is claimed.

## Pending gate

Fresh CI/Compose runs and the final limited Claude verification of the changed
files remain required after the approved capability-only remediation.
