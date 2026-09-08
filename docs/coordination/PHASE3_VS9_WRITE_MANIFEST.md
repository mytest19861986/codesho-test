# Phase 3 Vertical Slice 9 Write Manifest (P3-VS9)

## 1. Locked Authority & Scope
- **Slice ID**: `P3-VS9-ENTERPRISE-ANALYTICS-SUPERVISION-AND-COHORT-ORCHESTRATION`
- **Reference Plan**: `docs/architecture/PHASE3_VS9_BOUNDARY_PLAN.md`
- **Authority**: `COMMANDER_P3_VS9_DISCOVERY_UNLOCK`
- **Status**: `DISCOVERY_PASS / RUNTIME_LOCK_ACTIVE`

---

## 2. Locked File Targets (Zero Wildcards)

### Backend Targets
- `backend/modules/learning/models.py`: Addition of `CohortSupervision`, `CohortProgressAggregate`, `StudentSupervisionAlert`.
- `backend/modules/learning/migrations/0024_p3_vs9_supervision.py`: Schema migration for models, constraints, and composite indexes.
- `backend/modules/learning/migrations/0025_p3_vs9_supervision_rls.py`: PostgreSQL 17 `FORCE ROW LEVEL SECURITY` migrations with `app.current_tenant` isolation.
- `backend/modules/learning/supervision.py`: Supervision service, snapshot calculator/reader, and idempotent alert generator.
- `backend/modules/learning/views.py`: API endpoints for mentor cohort analytics and supervision alerts.
- `backend/modules/learning/urls.py`: URL patterns routing to supervision endpoints.
- `backend/tests/test_p3_vs9_supervision.py`: Domain, snapshot, and alert state machine test suite.
- `backend/tests/test_p3_vs9_supervision_rls.py`: PostgreSQL 17 FORCE RLS, cross-tenant negative isolation, and 404 access matrix tests.

### Frontend Targets
- `frontend/src/components/supervision/CohortOrchestrationScreen.tsx`: Mentor supervision analytical dashboard.
- `frontend/src/components/supervision/CohortKpiCards.tsx`: High-density KPI cards with BiDi tabular-nums.
- `frontend/src/components/supervision/StudentAlertTable.tsx`: Supervision alert table with non-color severity indicators and WCAG 2.2 AA compliance.
- `frontend/src/app/dashboard/mentor/page.tsx`: Route mounting for mentor supervision interface.

### Documentation & OpenAPI Targets
- `docs/openapi.yaml`: Complete OpenAPI 3.1 specification for `/mentor/cohorts/{id}/analytics/` and `/mentor/cohorts/{id}/alerts/`.
- `docs/coordination/PHASE3_VS9_WRITE_MANIFEST.md`: This locked manifest.
