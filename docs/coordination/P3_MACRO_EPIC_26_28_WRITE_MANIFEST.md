# P3-MACRO-EPIC-26-28 WRITE MANIFEST

**EPIC_ID**: `P3-MACRO-EPIC-26-28-ENTERPRISE-GOVERNANCE-DATA-LIFECYCLE-AND-PILOT-READINESS`  
**STATUS**: `DISCOVERY_LOCKED`  
**CANONICAL_HEAD**: `0e752bd560c6423e3faa8e26649946df6a693c93`  

---

## 1. Scope & Module Allocations

### Backend Models & Migrations (`backend/modules/learning/`)
- `models.py`:
  - **P3-VS26**: `StaffAccessAssignment`, `DelegatedAdminScope`, `PrivilegedPermissionGrant`, `AccessReviewCampaign`, `AccessReviewDecision`, `PrivilegedActionAudit`
  - **P3-VS27**: `DataRetentionPolicy`, `RetentionPolicyVersion`, `RetentionEvaluation`, `DataDispositionRecord`, `LegalHold`, `LegalHoldScope`, `DispositionAuditLog`
  - **P3-VS28**: `ReadinessControl`, `ReadinessEvidence`, `ReadinessAssessmentRun`, `ReadinessFinding`, `ReadinessException`, `PilotReadinessGate`, `ControlAttestationAudit`
- `migrations/`:
  - `0047_p3_macro_epic_26_28_models.py`
  - `0048_p3_macro_epic_26_28_rls_force.py`

### Backend Services & API (`backend/modules/learning/`)
- `governance_service.py`:
  - Lifecycle methods for Access Reviews, Privilege Grants, Retention, Legal Hold, and Readiness Runs.
- `governance_serializers.py`: Serializers for administrative control plane models.
- `governance_views.py`: Safe DRF API views with anti-ranking checks and permission enforcement.
- `urls.py`: Registered endpoints under `/api/v1/learning/governance/...`.

### Negative Matrix & Automated Tests (`backend/tests/`)
- `test_p3_macro_epic_26_28_governance.py`:
  - Integrated negative matrix covering RLS, privilege escalation, self-grants, legal-hold bypass, audit immutability, PII protection, and readiness non-authoritative boundaries.

### Frontend Enterprise Control Center (`frontend/src/`)
- `components/governance/EnterpriseControlCenterWorkspace.tsx`: Multi-tabbed executive dashboard.
- `components/governance/governance.module.css`: Accessible high-density styling, WCAG 2.2 AA.
- `app/dashboard/admin/enterprise-governance/page.tsx`: Route page.
