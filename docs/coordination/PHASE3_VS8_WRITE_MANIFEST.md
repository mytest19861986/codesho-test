# Phase 3 Vertical Slice 8 Write Manifest (P3-VS8)

## Target Authority
- Task: `P3-VS8-COURSE-COMPLETION-CERTIFICATION-AND-LEARNING-VERIFICATION`
- Status: `DISCOVERY_LOCKED` (Zero Runtime Code Changes Permitted until Fleet Review PASS & Commander Authorization)
- Authority: `COMMANDER_P3_VS8_DISCOVERY_START`

## Manifest Invariants
- ZERO_WILDCARDS: YES
- EXACT_PATHS_ONLY: YES
- UNREVIEWED_PATHS: 0

---

## 1. Documentation & Architecture
- `docs/architecture/PHASE3_VS8_BOUNDARY_PLAN.md` (Boundary architecture specification)
- `docs/coordination/PHASE3_VS8_WRITE_MANIFEST.md` (This file)
- `docs/coordination/CURRENT_TASK.md` (Task coordination state)
- `docs/openapi.yaml` (OpenAPI schema specification for certificate endpoints)

---

## 2. Planned Backend Components (Locked for Discovery)
- `backend/modules/learning/certificates.py` (Course completion evaluator, certificate issuance engine, verification services)
- `backend/modules/learning/models.py` (Enhancements for CertificateTemplate, CourseCertificate, CertificateVerificationRecord)
- `backend/modules/learning/serializers.py` (CertificateTemplateSerializer, CourseCertificateSerializer, LearningAchievementTimelineSerializer)
- `backend/modules/learning/views.py` (CourseCertificateListView, CertificateDetailVerifyView, LearningTimelineView, ParentVerifyCertificateView)
- `backend/modules/learning/urls.py` (Routing for certificate issuance, listing, verification, and timeline endpoints)
- `backend/modules/learning/migrations/0022_p3_vs8_certificates.py` (Table definitions, constraints, and indexes)
- `backend/modules/learning/migrations/0023_p3_vs8_certificates_rls.py` (PostgreSQL 17 FORCE RLS policies)

---

## 3. Planned Backend Tests (Locked for Discovery)
- `backend/tests/test_p3_vs8_certificates.py` (Completion engine evaluation, state machine transitions, replay idempotency, verification queries)
- `backend/tests/test_p3_vs8_certificates_rls.py` (PostgreSQL 17 cross-tenant isolation and negative permission tests)

---

## 4. Planned Frontend Components (Locked for Discovery)
- `frontend/src/components/certificates/CertificateCard.tsx` (Premium, dignified certificate card with Persian typography and verification seal)
- `frontend/src/components/certificates/AchievementTimeline.tsx` (Interactive milestone progress timeline component)
- `frontend/src/features/parent/ParentDashboardScreen.tsx` (Mount certificate verification and milestone widget)
- `frontend/src/app/dashboard/student/page.tsx` (Mount certificate and timeline showcase into student dashboard)

---

## 5. Visual Evidence & Regression Testing (Antigravity Sweep)
- Route: `/` (Landing)
- Route: `/login` (Login)
- Route: `/dashboard/student` (Student Dashboard & Certificate Card)
- Route: `/dashboard/mentor` (Mentor Review & Student Achievement Dossier)
- Route: `/dashboard/parent` (Parent Progress & Milestone Verification)
- Route: `/admin/learning` (Admin Curriculum & Certificate Templates)
