# AUTH-PASSCODE-CHANGE-001B2 Handoff

Status: `COMPLETE`

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

The first remote run exposed malformed expected-constraint SQL before any
replacement DDL. The regression is fixed by constructing the full nullable
condition once, and the focused test now pins both generated PostgreSQL CHECK
forms. Claude remediation review
`CLAUDE_AUTH_PASSCODE_CHANGE_001B2_AUDIT_MIGRATION_REVIEW_02_V1` completed
with no blocking findings.

After a second remote syntax failure, the exact DDL assertion was strengthened
to include the table-closing parenthesis before `ON COMMIT DROP`. Claude review
`CLAUDE_AUTH_PASSCODE_CHANGE_001B2_AUDIT_MIGRATION_REVIEW_03_V1` confirmed the
generated PostgreSQL DDL is balanced and no blocking findings remain.

Implementation commit `aaa3e9350a290b92c8edb128c06ad9f520d7042e` passed the
required remote gates: CI
`https://github.com/mytest19861986/codesho-test/actions/runs/29643913096` and
Compose smoke/restore
`https://github.com/mytest19861986/codesho-test/actions/runs/29643913110`.
No producer, endpoint, 001C work, coordination-file change, or protected
`codesho` promotion was performed.
