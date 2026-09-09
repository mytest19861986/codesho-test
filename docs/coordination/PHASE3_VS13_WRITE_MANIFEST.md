# Phase 3 Vertical Slice 13 Write Manifest

## Task ID: P3-VS13-STUDENT-GROWTH-INSIGHTS-AND-LONGITUDINAL-LEARNING-INTELLIGENCE

### Policy
- ZERO_WILDCARDS: Enforced. Every file path is exact.
- ARCHITECTURE: Longitudinal learning intelligence, growth metric snapshots, student growth trends, event-driven derivations without student ranking.
- STRICT_IMMUTABILITY: Published content, consent, receipts, and audit events are immutable.
- PRIVACY & SECURITY: PostgreSQL 17 FORCE RLS, Zero Bare UUIDs, Composite FKs `(tenant_id, id)`. Pure projection from Source of Truth. No student ranking or competitive leaderboards.

---

### Backend Files (Django 5.2 + DRF)
1. `backend/modules/learning/models.py` (Add LearningInsight, GrowthMetricSnapshot, StudentGrowthTrend, InsightGenerationEvent, LearningMilestone)
2. `backend/modules/learning/serializers.py` (Add serializers for P3-VS13 insights and trends)
3. `backend/modules/learning/views.py` (Add ViewSets for Growth Insights, Metrics, Trends, and Derivation Event triggers)
4. `backend/modules/learning/urls.py` (Add endpoints under `/api/v1/learning/...`)
5. `backend/modules/learning/services.py` (Add GrowthInsightService, TrendDerivationService with idempotency)
6. `backend/modules/learning/migrations/0033_phase3_vs13_growth_insights.py` (Schema migration)
7. `backend/modules/learning/migrations/0034_phase3_vs13_growth_insights_rls.py` (PostgreSQL 17 FORCE RLS migration)
8. `backend/tests/test_p3_vs13_growth_insights.py` (Exhaustive test suite covering domain, RLS, boundary, isolation, and negative scenarios N1-N40)

### Frontend Files (Next.js App Router + TypeScript)
9. `frontend/src/features/student_growth/GrowthJourneyDashboard.tsx`
10. `frontend/src/features/student_growth/ProgressStoryCard.tsx`
11. `frontend/src/features/student_growth/LearningInsightTimeline.tsx`
12. `frontend/src/features/student_growth/growth.module.css`
13. `frontend/src/app/dashboard/student/growth/page.tsx`

### Documentation & Coordination Artifacts
14. `docs/architecture/PHASE3_VS13_BOUNDARY_PLAN.md`
15. `docs/coordination/PHASE3_VS13_WRITE_MANIFEST.md`
16. `docs/coordination/PHASE3_VS13_DISCOVERY_DOSSIER.md`
17. `docs/coordination/PHASE3_VS13_FINAL_REPORT.md`
18. `docs/coordination/CURRENT_TASK.md`
19. `docs/openapi.yaml`
