# P7 GLM Discovery Review Package
## Phase 7 Real Pilot Manager Decision & Admission Preparation

- **Task ID**: `P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-DISCOVERY`
- **Discovery HEAD**: `957f0cd4eae98d1aeeecf5e3e6141e076313e8cc`
- **Evidence HEAD**: `957f0cd4eae98d1aeeecf5e3e6141e076313e8cc`
- **Target Agent**: `GLM (Z.ai)` (Database Persistence, Security & Tenant Isolation Specialist)
- **Review Purpose**: Audit correctness of decision persistence schema, tenant context isolation, RLS/FORCE RLS enforcement, crypto-shredding key lifecycle, and database invariants N7-15..N7-20.

### In-Scope Files (Exact Paths Only)
1. `docs/coordination/P7_REAL_PILOT_ADMISSION_ARCHITECTURE.md`
2. `docs/coordination/P7_REAL_DATA_ADMISSION_DECISION_PACKAGE.md`
3. `docs/coordination/P7_REAL_PILOT_SCOPE_PROPOSAL.md`
4. `docs/coordination/P7_REAL_PILOT_EXIT_PLAN.md`
5. `docs/coordination/P7_NEGATIVE_TEST_MATRIX.md`
6. `docs/coordination/P7_REAL_PILOT_WRITE_MANIFEST.md`

### Out of Scope
- Runtime DDL migrations, production schema mutation, execution of SQL scripts.

### Canonical Database & Security Invariants
- `FORCE ROW LEVEL SECURITY` and `NOBYPASSRLS` across all tenant-bound relations.
- Session protocol `SET LOCAL "app.current_tenant" = %s` strictly within `transaction.atomic()`.
- Immutability of decision records and audit events (zero UPDATE/DELETE).
- Per-tenant cryptographic envelope key shredding protocol for irreversible data destruction.
- Point-in-time recovery (PITR) multi-tenant isolation verification.

### Applicable Negative Tests
- **N7-07, N7-15, N7-16, N7-17, N7-18, N7-19, N7-20, N7-34, N7-40**.

### Expected Terminal Verdict Format
```text
GLM_PHASE7_DISCOVERY: PASS
GLM_PHASE7_BLOCKERS: 0
```
