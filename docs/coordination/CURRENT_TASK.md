# Current Task: P3-VS14-RUNTIME-IMPLEMENTATION

## Active Phase 3 Vertical Slice 14 — 2026-09-09

- Status: `RUNTIME_ACTIVE`.
- Branch: `codex/phase3-product-platform-foundation`.
- Authority: `COMMANDER_P3_VS14_RUNTIME_UNLOCK: GRANTED`.
- Task ID: `P3-VS14-STUDENT-LEARNING-OPERATIONS-AND-AI-ASSISTED-REFLECTION`.
- Title: سیستم عملیات یادگیری دانش‌آموز، بازتاب یادگیری (Learning Reflection) و دستیار هوشمند رشد
- Scope:
  1. Student Reflection Engine (Learning Reflection entries, guided prompts, growth review).
  2. Personal Learning Goals (Goal lifecycle: proposed, active, achieved, paused, cancelled).
  3. Action Plan State Machine (Step-by-step actionable learning plans tied to formative growth).
  4. Non-Authoritative AI Assistant (AI suggestions are assistive recommendations, never authoritative source of truth).
  5. Multi-Tenancy & Child Safety: PostgreSQL 17 `FORCE ROW LEVEL SECURITY with NOBYPASSRLS`, composite FKs `(tenant_id, id)`, zero bare UUIDs, zero student ranking, zero raw PII.
  6. Mentor Supervision: Scoped visibility for authorized mentors without cross-tenant or cohort leakage.
- Previous Slices Status:
  - P3-VS1 to P3-VS13: `COMPLETE_FINAL_ACCEPTED` (VS13 Accepted at commit `403a815`).
- Discovery Review Matrix:
  - `QWEN_DISCOVERY_REVIEW`: `QWEN_SCOPE: PASS` (Granted - Goal Lifecycle FSM, Formative Non-Authoritative AI, N1-N8 Domain Invariants).
  - `GLM_POSTGRES_RLS_REVIEW`: `GLM_SCOPE: PASS` (Granted v1.6 - PostgreSQL 17 FORCE RLS, NOBYPASSRLS, Composite FKs, SA-2, R3 Explainability, N1-N27).
  - `GEMINI_UI_PSYCHOLOGY_REVIEW`: `GEMINI_SCOPE: PASS` (Granted - WCAG 2.2 AA, RTL BiDi `<bdi dir="ltr">`, Growth-over-comparison, Learner Agency).
- Discovery Status: `TRIPLE_FLEET_PASS_UNANIMOUS`.
- Runtime Implementation Plan:
  1. Django Backend Models in `backend/modules/learning/models.py`.
  2. Migrations 0034 (Schema & Constraints) & 0035 (FORCE RLS & NOBYPASSRLS).
  3. Domain Services, FSM Guards & Serializers in `backend/modules/learning/`.
  4. Views, Routers & OpenAPI alignment in `docs/openapi.yaml`.
  5. Comprehensive Pytest Suite covering N1-N27 in `backend/tests/test_p3_vs14_learning_operations.py`.
  6. Frontend Next.js Pages & Components (ReflectionJournal, GoalTracker, ActionPlan) with BiDi `<bdi dir="ltr">` & WCAG 2.2 AA.
  7. Antigravity Browser Validation (Desktop & Mobile 390px).
- Open Blockers: 0.
