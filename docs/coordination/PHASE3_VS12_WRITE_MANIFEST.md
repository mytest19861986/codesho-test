# Phase 3 Vertical Slice 12 Write Manifest (P3-VS12)

## Manifest Governance
- **TASK_ID**: `P3-VS12-STUDENT-LEARNING-PORTFOLIO-AND-JOURNEY-NARRATIVE`
- **SCOPE_TITLE**: موتور پورتفولیوی یادگیری، آرتیفکت‌های دستاورد و روایت مسیر رشد دانش‌آموز
- **STATUS**: `RUNTIME_ACTIVE`
- **ZERO_WILDCARDS**: `YES`
- **EXACT_PATHS_ONLY**: `YES`
- **UNREVIEWED_PATHS**: `0`

---

## Allowed File Targets (Exact Paths Only)

### 1. Architecture & Coordination Documentation
- `docs/architecture/PHASE3_VS12_BOUNDARY_PLAN.md` (Design & Boundary Spec)
- `docs/coordination/PHASE3_VS12_WRITE_MANIFEST.md` (Locked File Manifest)
- `docs/coordination/CURRENT_TASK.md` (Active Task Pointer)
- `docs/coordination/PHASE3_VS12_DISCOVERY_DOSSIER.md` (Triple Fleet Review Dossier)
- `docs/coordination/PHASE3_VS12_FINAL_REPORT.md` (Post-Implementation Report)
- `docs/openapi.yaml` (API Contract Parity)

### 2. Backend Implementation (UNLOCKED BY COMMANDER)
- `backend/modules/platform_tenant/models.py` (Append GuardianAccessGrant)
- `backend/modules/platform_tenant/migrations/0004_p3_vs12_guardian_access_grant.py` (GuardianAccessGrant Schema & RLS)
- `backend/modules/learning/models.py` (Append LearningPortfolio, AchievementArtifact, StudentJourneyTimeline, PortfolioModerationAction)
- `backend/modules/learning/migrations/0030_p3_vs12_learning_portfolio.py` (Schema & Models)
- `backend/modules/learning/migrations/0031_p3_vs12_learning_portfolio_rls.py` (FORCE RLS & Composite FK DDL)
- `backend/modules/learning/portfolio_service.py` (Portfolio Aggregation, Journey Storytelling, Visibility Policy Enforcement)
- `backend/modules/learning/serializers.py` (Portfolio & Journey Serializers)
- `backend/modules/learning/views.py` (StudentPortfolioView, ParentPortfolioView, AchievementArtifactView, JourneyTimelineView)
- `backend/modules/learning/urls.py` (Endpoint Routing)

### 3. Automated Verification & Testing (LOCKED UNTIL RUNTIME UNLOCK)
- `backend/tests/test_p3_vs12_portfolio.py` (Negative Isolation N1-N20 Matrix, Zero PII Validation, Visibility Policy Fail-Closed, RLS Verification)

### 4. Frontend Components & UX (LOCKED UNTIL RUNTIME UNLOCK)
- `frontend/src/components/portfolio/LearningPortfolioCard.tsx` (Showcase of Student Achievements)
- `frontend/src/components/portfolio/StudentJourneyNarrative.tsx` (Visual Timeline of Educational Journey)
- `frontend/src/components/portfolio/AchievementArtifactModal.tsx` (Verified Work Artifact Viewer)
- `frontend/src/app/dashboard/student/portfolio/page.tsx` (Student Portfolio Showcase Page)

---

## Prohibited Paths (Zero Tolerance)
- No modifications to billing/payments (`backend/modules/billing/`)
- No live external AI mentor or third-party LLM providers
- No modification of core auth without explicit authorization
- No wildcard directories or unlisted migration files
