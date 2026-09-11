# P3-MACRO-EPIC-26-28 BOUNDARY PLAN: ENTERPRISE GOVERNANCE, DATA LIFECYCLE, AND PILOT READINESS CENTER

**EPIC_ID**: `P3-MACRO-EPIC-26-28-ENTERPRISE-GOVERNANCE-DATA-LIFECYCLE-AND-PILOT-READINESS`  
**STATUS**: `DISCOVERY_ACTIVE`  
**CANONICAL_DISCOVERY_HEAD**: `0e752bd560c6423e3faa8e26649946df6a693c93`  
**DATABASE**: PostgreSQL 17 + FORCE RLS + NOBYPASSRLS  
**ARCHITECTURAL_PARADIGM**: Modular Monolith, Django 5.2 + DRF, Next.js App Router, Transactional Outbox  

---

## 1. Executive Purpose & Scope
This macro-epic transitions Codesho from feature completeness into enterprise operational governance, deterministic data lifecycle management, and rigorous pilot readiness control.

### Flow Architecture
```text
IDENTITY / AUTHORITY
        ↓
ACCESS GOVERNANCE (P3-VS26)
        ↓
DATA LIFECYCLE GOVERNANCE (P3-VS27)
        ↓
CONTROL EVIDENCE & EVALUATION (P3-VS28)
        ↓
ENTERPRISE CONTROL CENTER (UX)
        ↓
PRE-PILOT GO / NO-GO (ADVISORY ONLY)
```

---

## 2. Integrated Slice Specifications

### P3-VS26: Delegated Administration & Access Governance
- **Purpose**: Governed staff/admin authority, principle of least privilege, and periodic access reviews.
- **Canonical Entities**:
  1. `StaffAccessAssignment`: Binds staff user to tenant-specific role with validity window.
  2. `DelegatedAdminScope`: Defines granular boundary constraints (e.g. branch, program, department) for staff admin actions.
  3. `PrivilegedPermissionGrant`: Explicit grant of high-privilege capabilities with dual-custody / justification.
  4. `AccessReviewCampaign`: Periodic review campaigns (quarterly/annual) for all assigned permissions.
  5. `AccessReviewDecision`: Explicit human decision (`MAINTAIN`, `REVOKE`, `RESTRICT`) per assignment.
  6. `PrivilegedActionAudit`: Append-only immutable log of every privileged access event.
- **Invariants**:
  - `PRIVILEGE_SELF_GRANT: DENY` (Administrators cannot grant themselves privileged roles).
  - `UNSCOPED_TENANT_ADMIN: DENY` (Tenant administrative scopes must be explicitly qualified).
  - `CROSS_TENANT_PRIVILEGE: DENY` (Permissions never cross tenant isolation boundaries).
  - `SILENT_PRIVILEGE_ESCALATION: DENY` (Role elevation requires approval and audit logging).
  - `ACCESS_REVIEW_AUDIT: APPEND_ONLY` (Decisions are immutable upon recording).

### P3-VS27: Data Lifecycle, Retention & Disposition Governance
- **Purpose**: Deterministic lifecycle policies, statutory legal holds, and auditable data disposition.
- **Canonical Entities**:
  1. `DataRetentionPolicy`: Master definition of retention periods by classification category.
  2. `RetentionPolicyVersion`: Immutable versioning of policies with active validity date ranges.
  3. `RetentionEvaluation`: Scheduled evaluation job tracking candidates for retention expiration.
  4. `DataDispositionRecord`: Formal disposition execution log (anonymization/purging) with cryptographic digest.
  5. `LegalHold`: Administrative/legal override freezing retention destruction.
  6. `LegalHoldScope`: Specific criteria/identifiers protected under active legal hold.
  7. `DispositionAuditLog`: Immutable verification trail for disposition compliance.
- **Invariants**:
  - `LEGAL_HOLD_BYPASS: DENY` (Entities under active legal hold cannot be disposed or pruned).
  - `IMMUTABLE_AUDIT_DESTRUCTIVE_DELETE: DENY` (Audit logs and evidence cannot be destroyed by disposition).
  - `UNAUTHORIZED_RETENTION_OVERRIDE: DENY` (Policy waivers require multi-signature authorization).
  - `CROSS_TENANT_DISPOSITION: DENY` (Disposition actions are strictly bound to tenant context).
  - `SYNTHETIC_DATA_ONLY: ENFORCED` (Zero real-world student PII or real child data processing).

### P3-VS28: Enterprise Control Evidence & Pilot Readiness Center
- **Purpose**: Non-production advisory control center aggregating automated and human-verified readiness criteria to assess pilot eligibility.
- **Canonical Entities**:
  1. `ReadinessControl`: Catalog of governance controls (RLS, Migrations, Test Suites, PII Guards, Fleet Consensus).
  2. `ReadinessEvidence`: Concrete immutable artifact linking verification evidence to a control.
  3. `ReadinessAssessmentRun`: Point-in-time automated evaluation run against all controls.
  4. `ReadinessFinding`: Discovered gaps, warnings, or blocking failures.
  5. `ReadinessException`: Formally approved temporary waiver for non-critical findings.
  6. `PilotReadinessGate`: Gate status evaluator producing readiness verdicts (`READY`, `NOT_READY`, `BLOCKED`, `EXCEPTION_REQUIRED`).
  7. `ControlAttestationAudit`: Immutable sign-off trail by authorized governance leads.
- **Invariants**:
  - `READINESS_SYSTEM: ADVISORY_CONTROL_PLANE` (System advises human authorities; has zero autonomous deployment capabilities).
  - `PRODUCTION_DEPLOY_AUTHORITY: 0` (No automated deployment or activation).
  - `STUDENT_RANKING: 0` (Zero comparative ranking, sorting, or leaderboard mechanisms).
  - `TAMPER_EVIDENCE_IMMUTABILITY: ENFORCED` (Readiness evidence records are append-only).

---

## 3. Security, Multi-Tenancy & Database Boundaries
- **PostgreSQL 17 FORCE RLS**: Applied to all tenant tables; `NOBYPASSRLS` set on application database roles.
- **Composite Foreign Keys**: All entity relationships must enforce `(tenant_id, id)` composite relational closure.
- **Zero Bare UUID**: No foreign key references an un-scoped bare UUID.
- **Fail Closed**: Any query or context evaluation lacking a valid `tenant_id` fails closed with immediate exception.
- **Audit Immutability**: Dedicated PostgreSQL rules and permissions (`REVOKE UPDATE, DELETE`) on `privileged_action_audit`, `disposition_audit_log`, and `control_attestation_audit`.

---

## 4. User Experience & Accessibility (Control Center)
- **Design System**: High-density enterprise dashboard, deep dark theme, WCAG 2.2 AA compliant contrast.
- **Touch & Click Target**: Minimum 44x44px for interactive elements.
- **BiDi / RTL**: Native right-to-left layout with explicit `<bdi dir="ltr">` for code identifiers, hashes, and dates.
- **State Representation**: Never rely solely on red/green colors; use distinct iconography, badges, and textual status tokens (`[PASS]`, `[FAIL]`, `[HOLD]`, `[ACTIVE]`).
- **Surface Views**:
  1. *Access Governance*: Assignments, privileged grants, active review campaigns.
  2. *Data Lifecycle*: Retention policies, legal hold tracker, disposition records.
  3. *Readiness Center*: Control matrix, live evidence status, finding resolutions, gate sign-off.
