# AUTH-PASSCODE-CHANGE-001B2 Handoff

Status: `IMPLEMENTATION_IN_PROGRESS`

Resolved paths: `backend/modules/platform_event/migrations/0007_passcode_change_challenge_allow_list.py` and `backend/tests/test_passcode_change_audit_allow_list_migration.py`.

The migration is atomic, PostgreSQL-only, additive and forward-only. Before
any `DROP CONSTRAINT`, it creates matching transaction-local expected
constraints and compares PostgreSQL's canonical `pg_get_constraintdef` output
plus `convalidated` against the existing audit constraints. A missing,
unvalidated, or mismatched predecessor aborts before any replacement DDL.

The focused suite covers predecessor literals, approved additions, irreversible
rollback, PostgreSQL mismatch fail-closed behavior, and the test-only empty
SQLite database path. The real PostgreSQL empty-database and constraint gate is
covered by the required CI and Compose workflows after commit.

Claude review `CLAUDE_AUTH_PASSCODE_CHANGE_001B2_AUDIT_MIGRATION_REVIEW_01_V1`
completed with no P0/P1 findings. The focused suite additionally covers
missing/unvalidated predecessor aborts and the matching validated path's exact
two `DROP`/`ADD` replacement pairs.
