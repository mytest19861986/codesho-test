# P6_PILOT_DATABASE_GLM_PACKAGE.md - Codesho / SSD

**TO**: GLM (Database & Security Specialist)
**FROM**: Codex (Implementation Engineer)
**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**SUBJECT**: Phase 6 Real Data Admission Gate, PostgreSQL 17 RLS Isolation, Data Lifecycle, and Security Invariants

---

## 1. Context & Architectural Mandate
Phase 6 Discovery establishes the data governance and admission gates required before any real data may ever be introduced to Codesho. In accordance with zero-fabrication rules, all data currently remains 100% synthetic.

### Core DB & Security Invariants:
- `REAL_PII`: `0`
- `REAL_CHILD_DATA`: `0`
- `POSTGRESQL_17`: `RLS`, `FORCE ROW LEVEL SECURITY`, `NOBYPASSRLS` verified on 100% tenant tables.
- `TRANSACTION_PROTOCOL`: `SET LOCAL "app.current_tenant"` required for all tenant queries.

---

## 2. Review Artifacts Staged
Please audit the following specifications:
1. `P6_REAL_DATA_ADMISSION_GATE.md` (14 Pre-Admission Gate Domains, Child Privacy Protection).
2. `P6_PILOT_OPERATING_MODEL.md` (SEV1-SEV4 Incident Taxonomy, Emergency Circuit Breaker).
3. `P6_NEGATIVE_TEST_MATRIX.md` (N6-08 Cross-Tenant Read, N6-09 Cross-Tenant Write, N6-30 Malformed GUC Injection).
4. `P6_SYNTHETIC_DRESS_REHEARSAL_PLAN.md` (P6-R12 Backup Restore Drill, P6-R13 PITR Rehearsal, P6-R19 Deletion Drill).

---

## 3. Specific Focus Questions for GLM
1. Do the 14 Pre-Admission Gate Domains completely seal all possible vectors for early or accidental real PII ingestion?
2. Are the emergency circuit breaker procedures for SEV1 tenant leakage mathematically fail-closed?
3. Does the data lifecycle specification satisfy GDPR / national child privacy requirements for right-to-be-forgotten without breaking audit immutability?

---

## 4. Expected Review Format
Please provide your evaluation in the standard format:
```text
GLM_PHASE6_DISCOVERY: PASS / BLOCK
GLM_PHASE6_DISCOVERY_BLOCKERS: 0
FINDINGS:
- ...
```
