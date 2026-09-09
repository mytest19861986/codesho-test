# Current Task: P3-VS13-RUNTIME-IMPLEMENTATION

## Active Phase 3 Vertical Slice 13 — 2026-09-09

- Status: `RUNTIME_AUTHORIZED_PHASED_EXECUTION`.
- Branch: `codex/phase3-product-platform-foundation`.
- Authority: `COMMANDER_P3_VS13_RUNTIME_UNLOCK: GRANTED`.
- Directives: `COMMANDER_P3_VS13_RUNTIME_IMPLEMENTATION`.
- Task ID: `P3-VS13-STUDENT-GROWTH-INSIGHTS-AND-LONGITUDINAL-LEARNING-INTELLIGENCE`.
- Scope: موتور بینش‌های طولی یادگیری، تحلیل مسیر رشد و گزارش‌های هوشمند پیشرفت دانش‌آموز (Longitudinal learning intelligence, growth metric snapshots, student growth trends, calculation run registry, event-driven derivations without student ranking).
- Discovery Gate Status:
  - `QWEN_DOMAIN_LOGIC_REVIEW`: PASS (VERIFIED)
  - `GLM_POSTGRES_RLS_SECURITY_REVIEW`: PASS (VERIFIED - v1.2 0 Blockers, 0 Majors)
  - `GEMINI_UI_PSYCHOLOGY_A11Y_REVIEW`: PASS (VERIFIED - v1.0 UI/UX, BiDi & Accessibility Approved)
  - `COMMANDER_RUNTIME_UNLOCK`: GRANTED (VERIFIED)
- Previous Slices Status:
  - P3-VS1 to P3-VS12: `COMPLETE_FINAL_ACCEPTED`
- Implementation Directives & Quality Gates:
  1. Backend Domain Models (`CalculationRun`, `GrowthMetricSnapshot`, `StudentGrowthTrend`, `LearningMilestone`, `LearningInsight`, `InsightGenerationEvent`).
  2. PostgreSQL 17 Composite FKs, Fail-closed RLS (`FORCE ROW LEVEL SECURITY with NOBYPASSRLS`).
  3. Calculation Engine (`pg_advisory_xact_lock`, Idempotency, Provenance).
  4. Anti-Ranking & Growth-Over-Comparison child protection invariants.
  5. API Serializers, Views, OpenAPI, Zero-PII sanitization.
  6. Frontend Components (`GrowthJourneyDashboard.tsx`, `ProgressStoryCard.tsx`, `LearningInsightTimeline.tsx`, `MentorInsightPanel.tsx`).
  7. Antigravity Regression (Desktop 1440x900, Mobile 390x844).
  8. Gemini Final Visual Gate + Qwen/GLM Final Gates.
- Open Blockers: 0.
