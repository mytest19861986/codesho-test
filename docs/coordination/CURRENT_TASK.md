# Current Task: P3-VS15-RUNTIME-IMPLEMENTATION

## Active Phase 3 Vertical Slice 15 — 2026-09-10

- Status: `RUNTIME_ACTIVE` (Commander Runtime Unlock Granted).
- Branch: `codex/phase3-product-platform-foundation`.
- Authority: `COMMANDER_P3_VS15_RUNTIME_UNLOCK: GRANTED`.
- Task ID: `P3-VS15-LEARNING-CONTINUITY-AND-STUDENT-SUCCESS-PLANNING`.
- Title: موتور تداوم یادگیری، برنامه موفقیت دانش‌آموز و هماهنگی مسیر رشد
- Certified Discovery Baseline:
  - Commit: `bbfce55` (DDL Baseline: `607bcac`).
  - Triple Fleet Consensus: Unanimous PASS (`GEMINI_SCOPE: PASS`, `QWEN_SCOPE: PASS`, `GLM_SCOPE: PASS`).
- Scope & Execution Order:
  1. Django ORM Models (`backend/modules/learning/models.py`):
     - `LearningStudentSuccessPlan`, `SuccessActionStep`, `SuccessTimelineEvent`, `SuccessAuditLog`.
     - Active singleton per student (`uq_successplan_student_active`), Composite FKs, Zero Bare UUIDs, 5-way XOR (`chk_timeline_target_xor`), Type-Target Coupling (`chk_timeline_type_target_coupling`), 13-key PII Exclusion regex & JSONB arrays, Non-authoritative AI boundary (`is_authoritative = FALSE`).
  2. Migrations:
     - `0036`: Schema + Constraints.
     - `0037`: PostgreSQL 17 `FORCE RLS` + `NOBYPASSRLS` + `REVOKE UPDATE, DELETE ON ... FROM app_role, PUBLIC`.
  3. Domain Service:
     - `ContinuityCoordinatorService` (`backend/modules/learning/continuity_coordinator_service.py`):
     - FSM State Machines (Plan, Action Step, Timeline Append/Amended, Audit Emission).
     - Strict permission & cohort bounds, non-authoritative AI advisory guards.
  4. API & Serializers:
     - DRF serializers & ViewSets registered with OpenAPI schema.
  5. Security Test Matrix:
     - N1 to N27 comprehensive negative test suite.
  6. Frontend Implementation & Visual Sweep:
     - `StudentSuccessTimeline` component + `/dashboard/student/success` page.
     - RTL BiDi flow, WCAG 2.2 AA, touch targets >= 44px, zero-ranking design.
- Open Blockers: 0.
