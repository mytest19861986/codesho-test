# Phase 3 Preliminary Write Manifest (Codesho)

## Policy
- **NO WILDCARDS ALLOWED** (e.g. `backend/**` or `frontend/**` are strictly prohibited).
- Every proposed write path must be explicit, justified, risk-categorized, and assigned a primary reviewer.
- Unauthorized additions require formal `MANIFEST_AMENDMENT`.

---

## Mandatory Boundary Gates for Phase 3 Execution (G1 - G6 & Qwen Invariants)

| Gate ID | Invariant / Requirement | Authority | Enforcement Layer | Status |
| :--- | :--- | :--- | :--- | :--- |
| **G1** | Dispatcher fails closed; polling without tenant context returns 0 rows | GLM 5.3 / Commander | Task Dispatcher & DB Session | MANDATORY |
| **G2** | Append-only tenant-bound Outbox semantics with negative tampering tests | GLM 5.3 / Commander | PostgreSQL DDL & Celery | MANDATORY |
| **G3** | Payload schema validation + PII payload scanner on event envelope | GLM 5.3 / Commander | Serializers & CI scanner | MANDATORY |
| **G4** | Tenant-prefixed storage key (`{tenant_id}/media/{media_id}`) | GLM 5.3 / Commander | Storage Service | MANDATORY |
| **G5** | Synthetic Media FSM (`PENDING -> PROCESSING -> READY / QUARANTINED`) | GLM 5.3 / Commander | Django Model / FSM | MANDATORY |
| **G6** | CI egress allowlist, secret scanner, blocked payment/AI dependencies | GLM 5.3 / Commander | GitHub Actions CI | MANDATORY |
| **Q-RLS** | `FORCE ROW LEVEL SECURITY` on all tenant-owned learning tables | Qwen 3.8 Max / Commander | Migration / PostgreSQL DDL | MANDATORY |
| **Q-FK** | Composite Foreign Keys `(tenant_id, id)` preventing cross-tenant leakage | Qwen 3.8 Max / Commander | Django Models & Postgres DB | MANDATORY |
| **Q-TEST** | Comprehensive cross-tenant negative test matrix (read/write/update/delete) | Qwen 3.8 Max / Commander | Pytest Suite | MANDATORY |

---

## Explicit Path Allowlist for P3-VS1

| Path | Workstream | Purpose | Type | Primary Owner | Reviewer | Risk | Collision Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `docs/architecture/PHASE3_BOUNDARY_AND_EXECUTION_PLAN.md` | ARCHITECTURE | Authoritative Phase 3 boundary definitions & backlog | NEW | Codex | GLM / Commander | R0 | LOW |
| `docs/coordination/PHASE3_WRITE_MANIFEST.md` | COORDINATION | Explicit write manifest with G1-G6 & Qwen invariants | NEW | Codex | Qwen / GLM | R0 | LOW |
| `docs/coordination/CURRENT_TASK.md` | COORDINATION | Live sprint task tracking and status checkpoints | EXISTING | Codex | Commander | R0 | LOW |
| `docs/coordination/CODEX_TO_COMMANDER.md` | COORDINATION | Regular evidence reporting and handoff log | EXISTING | Codex | Commander | R0 | LOW |
| `backend/modules/learning/models.py` | BACKEND | Add synthetic media attachment reference with composite FKs | EXISTING | Codex | Qwen / GLM | R1 | MED |
| `backend/modules/learning/serializers.py` | BACKEND | Serializers for synthetic media and non-PII outbox event payloads | EXISTING | Codex | Qwen | R1 | MED |
| `backend/modules/learning/views.py` | BACKEND | Endpoints for synthetic media attachments and notification feeds | EXISTING | Codex | Qwen | R1 | MED |
| `backend/modules/learning/urls.py` | BACKEND | URL routing for Phase 3 endpoints | EXISTING | Codex | Qwen | R1 | LOW |
| `backend/modules/learning/events.py` | BACKEND | Domain event builder definitions for durable outbox | NEW | Codex | Qwen / GLM | R1 | LOW |
| `backend/modules/learning/tests/test_p3_media_attachment.py` | TESTING | Unit/integration tests for media attachment boundaries & FSM | NEW | Codex | Qwen | R1 | LOW |
| `backend/modules/learning/tests/test_p3_outbox_events.py` | TESTING | Invariant tests for atomic outbox event persistence & PII scan | NEW | Codex | GLM | R1 | LOW |
| `backend/modules/learning/tests/test_p3_cross_tenant_negative.py` | TESTING | Comprehensive cross-tenant negative matrix (read/write/update/delete) | NEW | Codex | Qwen / GLM | R1 | LOW |
| `frontend/src/app/admin/learning/page.tsx` | FRONTEND | Admin UI for synthetic media attachment metadata | EXISTING | Codex | Gemini | R1 | MED |
| `frontend/src/app/dashboard/student/page.tsx` | FRONTEND | Student UI for viewing attached learning media | EXISTING | Codex | Gemini | R1 | MED |
| `frontend/src/components/notifications/NotificationBell.tsx` | FRONTEND | Cross-role synthetic notification drawer component | NEW | Codex | Gemini | R1 | LOW |

---

## Manifest Status
- `GLM_REVIEW`: PASS (OPEN_BLOCKERS: 0)
- `QWEN_INVARIANTS_INTEGRATED`: YES (FORCE_RLS, COMPOSITE_FK, NEGATIVE_MATRIX)
- `R3_R4_STATUS`: ZERO (Payment, Real PII, AI Mentor blocked)
- `STATUS`: READY_FOR_FINAL_LOCK
