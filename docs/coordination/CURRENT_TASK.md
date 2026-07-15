# Current Task: SZ-016

- Owner: Codex
- Priority: P0
- Status: in progress
- Goal: prove a clean Compose startup, PostgreSQL RLS test execution and a
  real backup/restore drill before Sprint Zero approval.
- Constraint: local Docker daemon is unavailable; the isolated GitHub Actions
  Compose smoke/restore workflow is the approved fallback execution path.
- Next action: validate the workflow locally where possible, push it to
  `codesho-test`, and diagnose each CI failure until green.
