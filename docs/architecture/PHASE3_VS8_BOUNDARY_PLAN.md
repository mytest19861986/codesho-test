# Phase 3 Vertical Slice 8 Boundary Plan (P3-VS8)

## 1. Context and Authority
- **Authority**: `COMMANDER_P3_VS8_DISCOVERY_START` (Official Commander Directive Issued)
- **Task ID**: `P3-VS8-COURSE-COMPLETION-CERTIFICATION-AND-LEARNING-VERIFICATION`
- **Scope Title (Farsi)**: صدور گواهی پایان دوره، اثبات دستاورد یادگیری و سیستم تأیید پیشرفت جامع
- **Status**: `DISCOVERY_ACTIVE / RUNTIME_LOCKED` (Strictly No Code Changes until Fleet Approval & Commander Runtime Unlock)
- **Watchdog Cadence**: Approved 5-minute polling interval with 30-second text-stability and single-line rejection rule.
- **Fundamental Invariants**:
  * **Runtime Locked**: Zero runtime code modification before triple fleet PASS and Commander Runtime Unlock.
  * **Zero PII**: Strictly synthetic student identifiers, mentor hashes, and non-identifiable educational records.
  * **Fail-Closed Multi-Tenancy**: Strict PostgreSQL 17 `FORCE ROW LEVEL SECURITY` on all tenant-scoped tables (`app.current_tenant`).
  * **Authoritative Source of Truth**: Course completion criteria computed exclusively on the backend from authoritative database records (`Progress`, `Course`, `Lesson`, `Assignment`, `Submission`, `Feedback`, `AssessmentResult`). Frontend has zero completion-granting authority.
  * **Immutability of Issuance**: Issued certificates are immutable records with cryptographic verification digests; duplicate event replay cannot mint duplicate certificates.

---

## 2. Definitive Course Completion Policy & Scoring Formula (Qwen Mandate)

### 2.1 Course Completion Policy & Versioning (`CompletionPolicy`)
A course completion is evaluated strictly against a versioned policy snapshot defined on the `Course` or `CertificateTemplate`:
1. **Mandatory Lessons Rule**: 100% of published non-optional lessons in the course must have a terminal `Progress` record with `state = 'completed'`.
2. **Assignments & Mentor Review Rule**:
   - If a course contains assignments: All assignments must have an authoritative `Submission` with `state = 'reviewed'`.
   - If a course contains no assignments: This requirement is skipped cleanly without blocking completion.
3. **Automated Code Assessments Rule**:
   - If a course contains code assessments: Every assessment must have an `AssessmentResult` with `is_passed = True` and score $\ge$ assessment passing threshold.
   - If a course contains no code assessments: This requirement is skipped cleanly.
4. **Weighted Final Score Formula (نمره کل نهایی)**:
   $$\text{Final Score} = (W_{\text{assignments}} \times \text{AvgAssignmentScore}) + (W_{\text{assessments}} \times \text{AvgAssessmentScore})$$
   - Defaults: If both exist, $W_{\text{assignments}} = 0.40$, $W_{\text{assessments}} = 0.60$. If only one exists, that component carries weight $1.0$.
   - Course completion eligibility requires: $\text{Final Score} \ge \text{CertificateTemplate.min_score_percentage}$ (e.g. $\ge 70.00\%$).

---

## 3. Data Models & Entity Relationships (Draft Specification)

### 3.1 `CertificateTemplate` (قالب گواهی دوره با نسخه‌بندی)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `course`: ForeignKey(`learning.Course`, on_delete=CASCADE, related_name="certificate_templates")
- `version`: PositiveIntegerField(default=1)
- `title`: CharField(max_length=160, e.g., "گواهی پایان دوره جامع برنامه‌نویسی پایتون")
- `description`: TextField
- `min_score_percentage`: DecimalField(max_digits=5, decimal_places=2, default=70.00)
- `is_active`: BooleanField(default=True)
- `created_at`, `updated_at`: DateTimeField
- **Constraints**: 
  * `UNIQUE (tenant, id)`
  * `UNIQUE (tenant, course, version)`

### 3.2 `CourseCertificate` (سند قطعی صدور گواهی)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `course`: ForeignKey(`learning.Course`, on_delete=PROTECT, related_name="issued_certificates")
- `template`: ForeignKey(`CertificateTemplate`, on_delete=PROTECT, related_name="issued_certificates")
- `student_id`: UUIDField(db_index=True)
- `completion_round`: PositiveIntegerField(default=1)  # Supports re-issuance only if explicitly allowed after revocation
- `certificate_number`: CharField(max_length=64, db_index=True)  # Format: CERT-{TENANT_SHORT}-{YEAR}-{HEX8}
- `verification_hash`: CharField(max_length=64, db_index=True)  # SHA-256 canonical digest
- `status`: CharField(max_length=16, choices=[`ISSUED`, `REVOKED`], default=`ISSUED`)  # GENERATED merged cleanly into atomic ISSUED
- `final_score`: DecimalField(max_digits=5, decimal_places=2)
- `completion_snapshot`: JSONField(default=dict)  # Immutable snapshot: lessons_count, assignments_passed, assessments_passed, weights, policy_version
- `source_event_id`: UUIDField(db_index=True)  # Domain completion outbox event id
- `issued_at`: DateTimeField(auto_now_add=True)
- `revoked_at`: DateTimeField(null=True, blank=True)
- `revocation_reason`: TextField(blank=True, default="")
- **Immutability Invariant**:
  * Core issuance fields (`id`, `tenant`, `course`, `student_id`, `template`, `certificate_number`, `verification_hash`, `final_score`, `completion_snapshot`, `issued_at`) are strictly immutable once created (enforced via model `.save()` override and DB trigger).
  * Only `status` (`ISSUED -> REVOKED`), `revoked_at`, and `revocation_reason` may be mutated during an authorized administrative revocation.
- **Constraints**:
  * `UNIQUE (tenant, id)`
  * `UNIQUE (tenant, course, student_id, completion_round)`
  * `UNIQUE (tenant, certificate_number)`
  * `UNIQUE (tenant, verification_hash)`
  * `UNIQUE (tenant, source_event_id)`

### 3.3 `CertificateVerificationRecord` (دفتر ثبت استعلام اصالت گواهی)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `certificate`: ForeignKey(`CourseCertificate`, null=True, blank=True, on_delete=CASCADE, related_name="verification_queries")
- `queried_number`: CharField(max_length=64, db_index=True)
- `result_status`: CharField(max_length=16, choices=[`VALID`, `REVOKED`, `NOT_FOUND`, `INVALID_HASH`])
- `queried_by_role`: CharField(max_length=16)  # 'student', 'parent', 'mentor', 'admin', 'anonymous'
- `queried_at`: DateTimeField(auto_now_add=True)
- **Constraints**: `UNIQUE (tenant, id)`.

---

## 4. Verification Hash Canonical Specification (هش اعتبارسنجی با HMAC-SHA256)

The `verification_hash` is computed deterministically via HMAC-SHA256 keyed with the tenant's secret key (`tenant.signing_key`) across a canonical, normalized JSON tuple:
```python
canonical_payload = {
    "tenant_id": str(tenant_id),
    "course_id": str(course_id),
    "student_id": str(student_id),
    "certificate_number": certificate_number,
    "final_score": f"{final_score:.2f}",
    "template_version": template.version,
    "key_version": 1,
    "issued_at_iso": issued_at.isoformat(),
}
verification_hash = hmac.new(
    key=tenant.signing_key.encode("utf-8"),
    msg=json.dumps(canonical_payload, sort_keys=True).encode("utf-8"),
    digestmod=hashlib.sha256
).hexdigest()
```
- In verification queries: Constant-time comparison (`hmac.compare_digest(computed_hash, record.verification_hash)`) is enforced. If mismatched, status returns `INVALID_HASH`.

---

## 5. Learning Achievement Timeline (Projection & Cursor Pagination)

1. **Source of Truth**: Append-only event stream from `platform_event.OutboxMessage` or dedicated `LearningActivityEvent` projection.
2. **Event Types**:
   - `COURSE_ENROLLED`
   - `LESSON_COMPLETED`
   - `ASSIGNMENT_SUBMITTED`
   - `ASSIGNMENT_REVIEWED`
   - `BADGE_AWARDED`
   - `CERTIFICATE_ISSUED`
3. **Cursor Pagination**: Ordered deterministically by `(occurred_at DESC, id DESC)`.
   - Cursor encoded as base64 token of `occurred_at_timestamp:uuid`.
   - Late-arriving events are inserted with their original UTC `occurred_at` timestamp without mutating earlier event sequence keys.

---

## 6. Multi-Tenant Security & Database Invariants (PostgreSQL 17 FORCE RLS)

- Every new table (`learning_certificatetemplate`, `learning_coursecertificate`, `learning_certificateverificationrecord`) MUST enforce:
  ```sql
  ALTER TABLE learning_certificatetemplate ENABLE ROW LEVEL SECURITY;
  ALTER TABLE learning_certificatetemplate FORCE ROW LEVEL SECURITY;
  
  ALTER TABLE learning_coursecertificate ENABLE ROW LEVEL SECURITY;
  ALTER TABLE learning_coursecertificate FORCE ROW LEVEL SECURITY;
  
  ALTER TABLE learning_certificateverificationrecord ENABLE ROW LEVEL SECURITY;
  ALTER TABLE learning_certificateverificationrecord FORCE ROW LEVEL SECURITY;
  ```
- **Policy Definition**: Standardized on `app.current_tenant` fail-closed UUID casting.
- **Cross-Tenant Negatives**:
  * Querying certificates belonging to Tenant B while session is set to Tenant A yields strictly empty result sets (0 rows).
  * Direct insert with mismatched `tenant_id` fails closed immediately.

---

## 7. Mandatory Test Suites (Qwen & Fleet Verification Matrix)

1. **Completion Logic Tests**:
   - Course with incomplete lessons -> Certificate issuance denied (`IncompleteCourseError`).
   - Course with failed assignment / pending review -> Issuance denied.
   - Course with failed code assessment -> Issuance denied.
   - Final score below `min_score_percentage` -> Issuance denied.
   - Course with zero assignments and zero assessments -> Successfully completes on 100% lesson completion.
2. **Idempotency & Concurrency Tests**:
   - Two concurrent completion events for same student/course -> `select_for_update()` lock prevents duplicate rows; exactly 1 certificate issued.
   - Replay of identical `source_event_id` -> Returns existing certificate cleanly with status 200.
3. **State Machine & Revocation Tests**:
   - Active certificate -> Verification returns `VALID`.
   - Revoke action -> Requires mandatory reason; updates status to `REVOKED`.
   - Revoked certificate verification -> Returns `REVOKED`.
   - Re-issuance attempt on same `completion_round` -> Rejected.
4. **Immutability Tests**:
   - Attempting to update `certificate_number`, `student_id`, `verification_hash`, or `final_score` -> Raises `ValidationError` / DB constraint error.
5. **Timeline & Cursor Tests**:
   - Cursor pagination stable across page boundaries.
   - Zero cross-tenant event leakage in student timeline.

---

## 8. Out-of-Scope & Prohibited Items (Non-Goals)
- ❌ Official government or accredited educational diplomas (Certificates are platform-synthetic achievement milestones).
- ❌ Integration with external national verification registries or third-party credential providers.
- ❌ Public unrestricted internet search indexation.
- ❌ Real personal identification information (PII) like national IDs, phone numbers, or physical addresses.
- ❌ Commercial payment gates or paywalled certificate issuance.
- ❌ Runtime AI mentor or unverified external LLM services.

---

## 9. Triple Fleet Review Dispatch Checklist
- [ ] **Qwen 3.8 Max**: Domain logic, course completion evaluation rules, state machine transitions, event consistency, idempotency, and concurrency control.
- [ ] **GLM 5.3**: Database architecture, PostgreSQL 17 FORCE RLS tenant isolation, immutability, zero-PII audit trail, and security boundaries.
- [ ] **Gemini 3.8**: UI/UX design tokens, certificate aesthetic dignity, achievement psychology, RTL typography, responsive layout, and WCAG 2.2 AA compliance.

---

## 10. Database Architecture & Security Hardening (GLM Remediation)

### 10.1 Cryptographic Integrity & Anti-Tampering (HMAC-SHA256)
- The certificate verification digest uses HMAC-SHA256 keyed with a tenant-level secret (`tenant.signing_key`) rather than unsalted SHA-256:
  ```python
  verification_digest = hmac.new(
      key=tenant.signing_key.encode("utf-8"),
      msg=json.dumps(canonical_payload, sort_keys=True).encode("utf-8"),
      digestmod=hashlib.sha256
  ).hexdigest()
  ```
- Constant-time comparison (`hmac.compare_digest`) is enforced during public/role verification queries to prevent timing side-channel attacks.

### 10.2 Public Verification Routing & RLS Isolation
- Public certificate verification is served via a dedicated endpoint `/api/v1/certificates/verify/` that:
  * Accepts `certificate_number` and `verification_hash`.
  * Queries with strict `tenant` isolation established inside `transaction.atomic()`.
  * Returns strictly sanitized, non-PII verification data: `{ "is_valid": true, "course_title": "...", "issued_at": "...", "student_display_id": "STU-XXXX", "final_score": "95.00" }`.
  * Rejects queries without valid tenant header/subdomain fail-closed.

### 10.3 Finite State Machine (FSM) & Partial Unique Index
- **FSM States**: Strictly `ISSUED` and `REVOKED`. No uncommitted intermediate states.
- **Revocation Enforcement**: Revocation transitions `ISSUED -> REVOKED` atomically. An issued certificate cannot be un-revoked; a re-issuance requires a distinct `completion_round` counter.
- **Partial Unique Index**:
  * PostgreSQL 17 Partial Index: `CREATE UNIQUE INDEX idx_unique_active_certificate ON learning_coursecertificate (tenant_id, course_id, student_id) WHERE status = 'ISSUED';`
  * Guarantees at the database engine level that no student can hold more than one active certificate for the same course simultaneously.
