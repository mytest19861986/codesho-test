# P3-MACRO-EPIC-17-19 Targeted Parallel Fleet Discovery Manifest

## Epic Identifier
- Epic ID: `P3-MACRO-EPIC-17-19-MENTOR-OPERATIONS-AND-PROGRAM-SUCCESS`
- Persian Title: مرکز عملیات منتور، هماهنگی تداوم یادگیری و هوشمندی موفقیت برنامه آموزشی
- Delivery Mode: `MACRO_FAST_ENTERPRISE` (Single Epic Package, Combined Discovery, Parallel Fleet Review)
- Authority: `COMMANDER_P3_VS16_CLOSURE_AND_MACRO_EPIC_17_19_DIRECTIVE`
- Included Vertical Slices:
  - `P3-VS17`: Mentor Caseload & Support Operations (`مدیریت بار کاری منتور و صف عملیات حمایتی`)
  - `P3-VS18`: Learning Check-ins, Scheduling & Follow-up Orchestration (`برنامه‌ریزی چک‌این‌های آموزشی و هماهنگی پیگیری`)
  - `P3-VS19`: Program Success Operations & Support Analytics (`داشبورد عملیاتی موفقیت برنامه و تحلیل اثربخشی`)

---

## 1. Scope and Target File Inventory (ZERO_WILDCARDS: YES)

### Exact Backend Implementation Paths:
1. `backend/modules/learning/models.py` (Add Caseload, Check-in, Aggregate projection models)
2. `backend/modules/learning/mentor_operations_service.py` (Service orchestration for VS17, VS18, VS19)
3. `backend/modules/learning/views.py` (Register mentor operations ViewSets)
4. `backend/modules/learning/serializers.py` (Add DRF serializers for Caseload, Check-in, and Aggregates)
5. `backend/modules/learning/urls.py` (Wire API endpoints under `/api/learning/mentor/...`)
6. `backend/modules/learning/migrations/0040_phase3_macro_epic_17_19_operations.py` (Schema migration)
7. `backend/modules/learning/migrations/0041_phase3_macro_epic_17_19_operations_rls.py` (PostgreSQL 17 RLS migration)
8. `backend/tests/test_p3_macro_epic_17_19_operations.py` (Negative & integration test matrix)

### Exact Frontend Implementation Paths:
1. `frontend/src/app/dashboard/mentor/caseload/page.tsx` (VS17: Mentor Caseload & Queue page)
2. `frontend/src/app/dashboard/mentor/checkins/page.tsx` (VS18: Check-ins & Scheduling page)
3. `frontend/src/app/dashboard/mentor/analytics/page.tsx` (VS19: Program Success Analytics page)
4. `frontend/src/components/mentor/MentorCaseloadQueue.tsx` (VS17 interactive component)
5. `frontend/src/components/mentor/LearningCheckInSchedule.tsx` (VS18 interactive component)
6. `frontend/src/components/mentor/ProgramSuccessMetrics.tsx` (VS19 interactive component)

---

## 2. Hard Governance & Architectural Invariants

1. **Anti-Ranking & Non-Punitive Invariant (تخطی‌ناپذیر)**:
   - ZERO student percentiles, zero leaderboards, zero competitive gamification, zero peer comparison.
   - Urgency in mentor queues is strictly operational (based on explicit due dates or pending follow-ups), NEVER based on student psychological, behavioral, or black-box risk scoring.
2. **Learner Agency & Consent**:
   - Check-ins and interventions are supportive invitations; student acknowledgement is voluntary. No forced punitive disciplinary escalations.
3. **Multi-Tenant RLS & PostgreSQL 17**:
   - `FORCE ROW LEVEL SECURITY` + `NOBYPASSRLS` across all new tables.
   - Fail-closed isolation bound strictly to `current_setting('app.current_tenant', true)`.
   - All foreign keys are strictly composite: `(tenant_id, target_id)`. ZERO bare UUIDs.
4. **Append-Only & Immutability**:
   - Any audit log or snapshot aggregates are immutable.
5. **UI & Accessibility (WCAG 2.2 AA & BiDi)**:
   - Touch targets >= 44x44px across desktop and mobile.
   - Full CSS logical properties (`margin-inline`, `padding-inline`) for RTL layout.
   - Strict `<bdi dir="ltr">` wrapping for all synthetic IDs, codes, dates, and numbers.

---

## 3. Parallel Fleet Review Allocation

- **Qwen (Principal Systems & Business Domain Architect)**:
  - Focus: Workflow & queue semantics (VS17), check-in FSM & commitment lifecycle (VS18), non-authoritative aggregate boundaries (VS19), anti-ranking and tenant authorization.
- **GLM (Principal Database & Security Specialist)**:
  - Focus: PostgreSQL 17 DDL, composite foreign keys, FORCE RLS, advisory locking concurrency, multi-tenant isolation, immutable audit logging.
- **Gemini (Principal UI/UX & Design Systems Specialist)**:
  - Focus: Mentor workspace usability, cognitive load, student check-in experience, program operations dashboard, WCAG 2.2 AA, responsive layout (1440x900 & 390x844), RTL/BiDi isolation.
