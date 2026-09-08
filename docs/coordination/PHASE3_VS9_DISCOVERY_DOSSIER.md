# Phase 3 Vertical Slice 9 Discovery Dossier (P3-VS9)

## 1. Executive Summary & Fleet Consensus Status
- **Slice ID**: `P3-VS9-ENTERPRISE-ANALYTICS-SUPERVISION-AND-COHORT-ORCHESTRATION`
- **Scope Title**: تحلیل پیشرفته سازمانی، نظارت منتورشیپ بر کوهورت‌ها و ارکستراسیون پیشرفت فراگیران
- **Triple Fleet Scope Consensus**: **100% PASS ACHIEVED**
  * **Gemini 3.8**: `GEMINI_SCOPE: PASS` (Approved visual ergonomics, high-density analytics KPI cards, non-color alert severity, and strict `<bdi dir="ltr">` BiDi isolation).
  * **Qwen 3.8 Max**: `QWEN_SCOPE: PASS` (Approved cohort orchestration domain, FSM state machine `ACTIVE -> ACKNOWLEDGED -> RESOLVED`, idempotent alert deduplication, and presentation projection).
  * **GLM 5.3 (Z.ai)**: `GLM_SCOPE: PASS` (Approved database invariants, PostgreSQL 17 FORCE RLS, 404 anti-enumeration access matrix, complete 6 Composite FKs eliminating bare UUIDs, with runtime items D-1..D-5 logged for implementation).
- **Runtime Status**: `DISCOVERY_COMPLETE / READY_FOR_RUNTIME_UNLOCK`

---

## 2. Invariants & Governance Summary
1. **Runtime Locked**: Strict lock maintained through entire discovery phase; zero runtime code modified until Commander issues `COMMANDER_P3_VS9_RUNTIME_UNLOCK`.
2. **Zero PII**: Strictly synthetic student identifiers, mentor UUIDs, and aggregated educational telemetry.
3. **Database-Level Composite Integrity (Zero Bare UUIDs)**:
   - `CohortSupervision`:
     * `FOREIGN KEY (tenant_id, cohort_id) REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE`
     * `FOREIGN KEY (tenant_id, mentor_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
     * `FOREIGN KEY (tenant_id, assigned_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
     * `FOREIGN KEY (tenant_id, revoked_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
   - `CohortProgressAggregate`:
     * `FOREIGN KEY (tenant_id, cohort_id) REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE`
   - `StudentSupervisionAlert`:
     * `FOREIGN KEY (tenant_id, cohort_id) REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE`
     * `FOREIGN KEY (tenant_id, student_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE CASCADE`
     * `FOREIGN KEY (tenant_id, acknowledged_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
     * `FOREIGN KEY (tenant_id, resolved_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT`
4. **PostgreSQL 17 FORCE RLS**:
   - `tenant_isolation_policy` applied with `NULLIF(current_setting('app.current_tenant', true), '')::uuid` on all three models.
5. **Access Control (Single-Path Pattern A)**:
   - Mentor querying assigned cohort => `200 OK`.
   - Mentor querying unassigned cohort => `404 Not Found` (anti-enumeration defense).
   - Cross-tenant / missing tenant context => `404 Not Found` (fail-closed 0 rows).
6. **Alert Idempotency**:
   - `deduplication_key = f"{tenant_id}:{cohort_id}:{student_id}:{alert_type}:{date_window}"` with `max_length=255` supporting `ON CONFLICT DO NOTHING`.

---

## 3. Triple Fleet Verdict Summaries

### Gemini 3.8 Review
- **Verdict**: `GEMINI_SCOPE: PASS`
- **Focus Areas**: Design Ergonomics, RTL layout, accessibility (WCAG 2.2 AA), `<bdi dir="ltr">` isolation for code and metric percentages, distinct non-color severity tokens.

### Qwen 3.8 Max Review
- **Verdict**: `QWEN_SCOPE: PASS`
- **Focus Areas**: Domain entities, supervision relationship lifecycle, 3-state alert FSM, deduplication key formula, projection boundary separation.

### GLM 5.3 Review
- **Verdict**: `GLM_SCOPE: PASS (Discovery-Level)`
- **Focus Areas**: PostgreSQL 17 FORCE RLS, eliminating bare UUIDs via 6 Composite FKs, negative test suite, migration ordering chain (0010 -> VS2-VS8 -> VS9).
- **Runtime Operational Directives (D-1 to D-5)**:
  * D-1: Use `ON DELETE RESTRICT` on audit actor composite FKs (not SET NULL) to preserve immutable audit trails.
  * D-2: Size `deduplication_key` with safe headroom (`max_length=255`).
  * D-3: Target membership composite FK to authoritative learner/mentor roles.
  * D-4: Verify `UNIQUE (tenant, id)` / `UNIQUE (tenant, user)` prerequisite constraints prior to migration execution.
  * D-5: Allow automated remediation transition `ACTIVE -> RESOLVED` via system actor.

---

## 4. Locked Write Manifest Targets
- `backend/modules/learning/models.py`
- `backend/modules/learning/migrations/0024_p3_vs9_supervision.py`
- `backend/modules/learning/migrations/0025_p3_vs9_supervision_rls.py`
- `backend/modules/learning/supervision.py`
- `backend/modules/learning/views.py`
- `backend/modules/learning/urls.py`
- `backend/tests/test_p3_vs9_supervision.py`
- `backend/tests/test_p3_vs9_supervision_rls.py`
- `frontend/src/components/supervision/CohortOrchestrationScreen.tsx`
- `frontend/src/components/supervision/CohortKpiCards.tsx`
- `frontend/src/components/supervision/StudentAlertTable.tsx`
- `frontend/src/app/dashboard/mentor/page.tsx`
- `docs/openapi.yaml`
- `docs/coordination/PHASE3_VS9_WRITE_MANIFEST.md`
- `docs/architecture/PHASE3_VS9_BOUNDARY_PLAN.md`
