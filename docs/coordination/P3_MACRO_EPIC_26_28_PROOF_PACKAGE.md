# P3-MACRO-EPIC-26-28 Comprehensive Proof Package & Invariant Verification Matrix (v1.0-CANONICAL)

## 1. Upstream Pinning & Architectural Pre-Conditions (§2.1 Pin)
1. **Upstream Tenant & Membership Authority**:
   - Every entity strictly cascades to `platform_tenant_tenant(id) ON DELETE CASCADE`.
   - Every user, actor, reviewer, and staff reference pins strictly to `platform_tenant_tenantmembership(tenant_id, user_id)` with `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` or `ON DELETE RESTRICT` (ensuring forensic preservation of historical administrative actions).
   - Zero bare foreign key UUIDs exist across the entire 20-table schema.
2. **Deterministic Immutability & Forensic Append-Only Architecture**:
   - Audit logs (`learning_privileged_action_audit`, `learning_disposition_audit_log`, `learning_control_attestation_audit`) and readiness evidence (`learning_readiness_evidence`) are strictly immutable: direct `UPDATE` and `DELETE` privileges are revoked from both `PUBLIC` and `app_role`.
   - Immutability guarantees are reinforced via database-level check constraints and append-only cryptographic hashes (`evidence_sha256`, `signature_digest`).
3. **Outbox Strategy**:
   - Outbox event propagation is service-layer orchestrated via durable transaction outbox (`transaction.atomic()` with `append_outbox_event`) identical to prior macro-epics; zero runtime external network calls inside database transactions; no standalone outbox table required in DDL.
4. **Advisory Gatekeeper Constraint**:
   - The pilot readiness center (`P3-VS28`) is purely advisory and governance-focused (`PRODUCTION_DEPLOY_AUTHORITY: 0`). Gate evaluations inform humans and generate auditable evidence; they never trigger automated infrastructure or unapproved production deployments.

---

## 2. Invariant Negative & Positive Test Matrix (N1 - N36) — 100% Aligned to DDL v1.2

| Test ID | Category | Target Invariant & Assertion Proof | Expected Result / SQL Assertion |
|:---|:---|:---|:---|
| **N1** | Tenant Isolation | Query without `app.current_tenant` GUC set | Fail-closed: 0 rows returned across all 20 tables |
| **N2** | Tenant Isolation | GUC set to empty string `""` | Fail-closed: 0 rows returned |
| **N3** | Positive Isolation | Query with valid matching tenant GUC | Exactly tenant-owned rows returned; 0 cross-tenant leak |
| **N4** | Cross-Tenant Leakage | Cross-tenant UUID lookup in `StaffAccessAssignment` | Rejection / 0 rows leaked across tenant boundaries |
| **N5** | Cross-Tenant Leakage | Cross-tenant lookup in `PrivilegedPermissionGrant` & `LegalHold` | Rejection / 0 rows leaked across tenant boundaries |
| **N6** | Composite FK Closure | Attempt to insert composite FK with mismatched `tenant_id` | `IntegrityError` (Violates PostgreSQL composite foreign key) |
| **N7** | Privilege Self-Grant Denial | Attempt to grant privilege where `user_id = granted_by_id` | CheckConstraint Violation (`chk_privilege_no_self_grant`) |
| **N8** | Two-Person Rule Escalation | Grant with `second_approver_id = granted_by_id` | CheckConstraint Violation (`chk_privilege_distinct_second_approver`) |
| **N9** | Immutability Protection | Direct SQL `UPDATE` on `learning_privileged_action_audit` | Permission Denied (`REVOKE UPDATE ON learning_privileged_action_audit`) |
| **N10** | Immutability Protection | Direct SQL `DELETE` on `learning_disposition_audit_log` | Permission Denied (`REVOKE DELETE ON learning_disposition_audit_log`) |
| **N11** | Immutability Protection | Direct SQL `UPDATE` or `DELETE` on `learning_control_attestation_audit` | Permission Denied (`REVOKE UPDATE, DELETE ON learning_control_attestation_audit`) |
| **N12** | Immutability Protection | Direct SQL `UPDATE` or `DELETE` on `learning_readiness_evidence` | Permission Denied (`REVOKE UPDATE, DELETE ON learning_readiness_evidence`) |
| **N13** | Legal Hold Bypass Denial | Attempt disposition on record covered by active `LegalHold` | Application/FSM Guard: `LegalHoldActiveError` |
| **N14** | Legal Hold Release Consistency | Hold with status `ACTIVE` and `released_at IS NOT NULL` | CheckConstraint Violation (`chk_hold_release_consistency`) |
| **N15** | Legal Hold Release Integrity | Hold with status `RELEASED` and `released_by_id IS NULL` | CheckConstraint Violation (`chk_hold_release_consistency`) |
| **N16** | FSM Illegal Transition | Campaign transition `COMPLETED` -> `IN_PROGRESS` | FSM Guard Rejection (`FSMValidationError`) |
| **N17** | FSM Illegal Transition | Privilege grant `REVOKED` -> `ACTIVE` | FSM Guard Rejection (`FSMValidationError`) |
| **N18** | FSM Illegal Transition | Assessment run `FAILED` -> `RUNNING` | FSM Guard Rejection (`FSMValidationError`) |
| **N19** | Anti-Ranking Compliance | Query parameter or API attempting learner ranking or scores | 400 Bad Request: `ranking_queries_prohibited` |
| **N20** | Non-Authoritative Advisory | Attempt to assign automated deployment authority to readiness gate | Rejection / Invariant: `PRODUCTION_DEPLOY_AUTHORITY: 0` |
| **N21** | Staff Validity Window | Staff assignment with `valid_until <= valid_from` | CheckConstraint Violation (`chk_staff_validity_window`) |
| **N22** | Retention Period Baseline | Retention policy version with `retention_period_days < 30` | CheckConstraint Violation (`chk_retention_period_positive`) |
| **N23** | Assessment Execution Window | Readiness assessment run with `ended_at < started_at` | CheckConstraint Violation (`chk_assessment_timing_order`) |
| **N24** | Finding Resolution Order | Readiness finding with `status = 'RESOLVED'` and `resolved_at IS NULL` | CheckConstraint Violation (`chk_finding_resolution_order`) |
| **N25** | PII Blacklist (JSONB) | Metadata containing blacklisted PII key (e.g. `national_id`, `ssn`) | CheckConstraint Violation (`chk_staff_assignment_metadata_no_pii`) |
| **N26** | PII Free-Text Bound | Privilege justification containing regex PII pattern or >2000 chars | CheckConstraint Violation (`chk_privilege_justification_pii`) |
| **N27** | PII Free-Text Bound | Legal hold reason containing regex PII pattern or >2000 chars | CheckConstraint Violation (`chk_legal_hold_reason_pii`) |
| **N28** | PII Free-Text Bound | Readiness finding summary containing regex PII pattern or >2000 chars | CheckConstraint Violation (`chk_finding_summary_pii`) |
| **N29** | PII Free-Text Bound | Attestation summary containing regex PII pattern or >2000 chars | CheckConstraint Violation (`chk_attestation_summary_pii`) |
| **N30** | Scope Resource Enum | Delegated admin scope with invalid `scope_resource_type` | CheckConstraint Violation (`chk_scope_resource_type`) |
| **N31** | Control Category Enum | Readiness control with invalid `control_category` | CheckConstraint Violation (`chk_control_category`) |
| **N32** | Zero Bare UUIDs | Database schema introspection across all 20 tables | 100% Assertion Pass: Zero bare foreign key UUIDs |
| **N33** | Tenant Cascade Wipe | Hard deletion of tenant in test environment | Cascades clean across all tables with zero orphaned rows |
| **N34** | Malformed Tenant GUC | GUC set to malformed non-UUID value (e.g. `'malformed-tenant-uuid'`) | Fail-closed: 0 rows returned, safe DB error handling |
| **N35** | Evidence Hash Integrity | Direct update to evidence file payload without updating sha256 | Verification Failure / SHA-256 Digest Mismatch |
| **N36** | Single Active Policy Enforcement | Concurrent active retention policies for identical resource type | `IntegrityError` (Unique partial index / constraint violation) |

---

## 3. Finite State Machine (FSM) Transition Specifications — 100% DDL-Aligned

### 3.1. PrivilegedPermissionGrant FSM (DDL: status IN ('ACTIVE', 'EXPIRED', 'REVOKED'))
```
[ACTIVE] ──(auto_expire / TimeTrigger)──> [EXPIRED]
[ACTIVE] ──(revoke / SecurityOfficer)───> [REVOKED]
```
- **Guards**: `user_id <> granted_by_id` (No self-grant); `second_approver_id <> granted_by_id` (Two-person separation).

### 3.2. AccessReviewCampaign FSM (DDL: status IN ('DRAFT', 'ACTIVE', 'COMPLETED', 'CANCELLED'))
```
[DRAFT] ──(launch_campaign / Admin)────> [ACTIVE]
[ACTIVE] ──(close_campaign / Admin)────> [COMPLETED]
[DRAFT / ACTIVE] ──(cancel / Admin)────> [CANCELLED]
```
- **Guards**: Campaign completion requires all review decisions recorded or explicitly exempted.

### 3.3. LegalHold FSM (DDL: status IN ('ACTIVE', 'RELEASED'))
```
[ACTIVE] ──(release_hold / LegalOfficer)─> [RELEASED] (released_at NOT NULL, released_by_id NOT NULL)
```
- **Guards**: `chk_hold_release_consistency` strictly enforces `released_at IS NULL` on `ACTIVE` and `released_at IS NOT NULL` on `RELEASED`.

### 3.4. DataDispositionRecord FSM (DDL: status IN ('PENDING_APPROVAL', 'APPROVED', 'EXECUTED', 'CANCELLED'))
```
[PENDING_APPROVAL] ──(approve / ComplianceOfficer)─> [APPROVED]
[APPROVED] ──────────(execute / SystemWorker)───────> [EXECUTED] (executed_at NOT NULL)
[PENDING_APPROVAL] ──(reject / ComplianceOfficer)───> [CANCELLED]
```
- **Guards**: Active LegalHold on targeted resource blocks transition to `APPROVED` and `EXECUTED`.

### 3.5. ReadinessAssessmentRun FSM (DDL: status IN ('SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED'))
```
[SCHEDULED] ──(start_assessment / Runner)─> [RUNNING] (started_at NOT NULL)
[RUNNING] ────(complete_evaluation / Runner)─> [COMPLETED] (ended_at NOT NULL, ended_at >= started_at)
[RUNNING] ────(abort_on_error / Runner)──────> [FAILED] (ended_at NOT NULL)
```
- **Guards**: `chk_assessment_timing_order` ensures valid chronological intervals.

### 3.6. ReadinessFinding FSM (DDL: status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'ACCEPTED_RISK'))
```
[OPEN] ──────────(investigate / Auditor)────> [INVESTIGATING]
[INVESTIGATING] ─(resolve / SecOps)─────────> [RESOLVED] (resolved_at NOT NULL, resolution_notes NOT NULL)
[INVESTIGATING] ─(accept_risk / CISO)───────> [ACCEPTED_RISK] (resolved_at NOT NULL, resolution_notes NOT NULL)
```
- **Guards**: `chk_finding_resolution_order` ensures forensic accountability upon resolution.

---

## 4. Multi-Tenant Role & Domain Access Matrix

| Role / Context | Delegated Admin (VS26) | Privileged Grants (VS26) | Retention & Holds (VS27) | Disposition Exec (VS27) | Readiness Gates (VS28) | Attestation Audit (VS28) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Anonymous** | DENY (401) | DENY (401) | DENY (401) | DENY (401) | DENY (401) | DENY (401) |
| **Cross-Tenant** | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) |
| **Staff Member** | READ (Assigned scope) | READ (Own grants) | READ (Active policies) | DENY (403) | READ (Advisory) | DENY (403) |
| **Tenant Admin** | MANAGE (Tenant scope) | REQUEST (No self-grant) | READ / PROPOSE | DENY (403) | READ / ASSESS | VIEW (Audit logs) |
| **Compliance / SecOps**| AUDIT / REVIEW | TWO-PERSON APPROVE | MANAGE (Holds/Policies) | APPROVE / EXECUTE | EVALUATE GATES | ATTEST (Sign gate) |
