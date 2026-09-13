# GLM Review Package: P5 Controlled Pilot Activation Discovery

## Objective
Audit and qualify the database role topology, tenant isolation under PostgreSQL 17 `FORCE RLS`, additive DDL rules, audit immutability, backup/restore, PITR, and data retention/offboarding architecture.

## Review Focus Areas
1. **DB Role Topology**: Ensure canonical connecting role `codesho_runtime` adheres to `NOSUPERUSER NOBYPASSRLS` and has `DELETE` revoked on governance tables.
2. **PostgreSQL 17 FORCE RLS**: Verify tenant isolation fails closed and is enforced unconditionally before queries.
3. **Data Admission Boundary**: Strict gateway preventing real data ingestion before legal basis, consent, and minimization prerequisites.
4. **Audit Immutability & Purge Safety**: Immutable audit ledger; soft-delete or cryptographic zeroization during offboarding; regulatory retention hold enforcement.
5. **DR & Recovery Rehearsals**: Validation of automated backup verification (`scripts/restore-verify.sh`) and continuous WAL archiving PITR workflows.

## Evidence Artifacts
- `docs/architecture/P5_CONTROLLED_PILOT_ACTIVATION_BOUNDARY_PLAN.md`
- `docs/coordination/P5_PILOT_GO_NO_GO_CONTROL_MATRIX.md`
- `docs/coordination/P5_SYNTHETIC_PILOT_REHEARSAL_PLAN.md`
- `docs/coordination/P5_NEGATIVE_TEST_MATRIX.md`
- `infra/postgres/init/001-roles.sh`
- `backend/governance/migrations/0050_revoke_delete_on_immutable_tables.py`

## Required Verdict Format
```
GLM_PHASE5_DISCOVERY: PASS | CHANGES_REQUIRED | BLOCK
GLM_PHASE5_BLOCKERS: 0
FINDINGS: <summary>
```
