# S1-004 Immutable Credential Security Audit Review Summary

## Review 01: migration and PostgreSQL enforcement

The bounded Review 01 package contains only the S1-004 audit migration. The
versioned prompt is retained outside Git as
`CLAUDE_S1_004_AUDIT_MIGRATION_REVIEW_01_v1.md`; the attachment copy has SHA-256
`8DD146B94E9F7F46EB28F92DAA8BEF4495106258BA39464181B61C750C1F8863`.

Review delivery was attempted through the approved shared Brave Profile 13 on
2026-07-16. The established endpoint `127.0.0.1:9222` was unavailable, and
the safe fallback could not launch because that Profile was already locked by
an existing Brave session. Per the workspace protocol, Codex did not close or
change the shared session. No Claude review result is claimed; Review 01 and
the follow-on service review remain pending provider/session availability.

## Local review and verification

- The audit table has no foreign key to a user table and no metadata column.
- `codesho_runtime` is granted only `USAGE` on `audit` and `INSERT` on the
  table; `SELECT`, `UPDATE`, `DELETE`, and `TRUNCATE` are explicitly revoked.
- PostgreSQL triggers reject update, delete, and truncate. The reverse
  migration raises `IrreversibleError` to protect retained evidence.
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

Sequential provider review remains the only open S1-004 acceptance gate.
