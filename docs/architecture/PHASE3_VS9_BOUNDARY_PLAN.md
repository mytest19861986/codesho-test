# Phase 3 Vertical Slice 9 Boundary Plan (P3-VS9)

## 1. Context and Authority
- **Authority**: `COMMANDER_P3_VS9_DISCOVERY_UNLOCK` (Official Commander Directive Issued)
- **Task ID**: `P3-VS9-ENTERPRISE-ANALYTICS-SUPERVISION-AND-COHORT-ORCHESTRATION`
- **Scope Title (Farsi)**: تحلیل پیشرفته سازمانی، نظارت منتورشیپ بر کوهورت‌ها و ارکستراسیون پیشرفت فراگیران
- **Status**: `DISCOVERY_ACTIVE / RUNTIME_LOCKED` (Strictly No Code Changes until Fleet Approval & Commander Runtime Unlock)
- **Watchdog Cadence**: Approved 5-minute polling interval with 30-second text-stability and single-line rejection rule.
- **Fundamental Invariants**:
  * **Runtime Locked**: Zero runtime code modification before triple fleet PASS and Commander Runtime Unlock.
  * **Zero PII**: Strictly synthetic student identifiers, mentor UUIDs, and non-identifiable educational aggregated analytics.
  * **Fail-Closed Multi-Tenancy**: Strict PostgreSQL 17 `FORCE ROW LEVEL SECURITY` on all tenant-scoped tables (`app.current_tenant`).
  * **Authoritative Aggregation Source Invariant**: "Authoritative FOR PRESENTATION READS ONLY — state-transition decisions read exclusively from Authorities (Enrollment, Progress, Submission, AssessmentResult)".
  * **Role-Based Access Boundaries**: Mentor supervision views restricted to their assigned cohorts via Single-Path Enforce Pattern (Pattern A in ViewSet with 404 response on unassigned cohorts); tenant admins access tenant-wide aggregated metrics.
  * **Complete Composite Foreign Key Integrity (Zero Bare UUIDs)**: All relational columns (`cohort_id`, `mentor_id`, `student_id`, and audit actors `assigned_by`, `revoked_by`, `acknowledged_by`, `resolved_by`) are strictly bound by DB-level Composite Foreign Keys `(tenant_id, target_id)` against authoritative tenant-scoped tables, preventing any invisible cross-tenant leakage.

---

## 2. Core Domain Architecture & Data Models (Complete Composite Integrity)

### 2.1 `CohortSupervision` (نگاشت و دسترسی نظارت منتور بر کوهورت با حفظ تاریخچه، ممیزی و FKهای ترکیبی کامل)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `cohort`: ForeignKey(`learning.Cohort`, on_delete=CASCADE, related_name="supervisors")
- `mentor_id`: UUIDField(db_index=True)
- `assigned_at`: DateTimeField(auto_now_add=True)
- `assigned_by`: UUIDField(null=True, blank=True)
- `is_lead`: BooleanField(default=False)
- `is_active`: BooleanField(default=True, db_index=True)
- `revoked_at`: DateTimeField(null=True, blank=True)
- `revoked_by`: UUIDField(null=True, blank=True)
- **Composite Foreign Key Definitions (PostgreSQL 17)**:
  * `FOREIGN KEY (tenant_id, cohort_id) REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, mentor_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT` (Guarantees mentor exists within the same tenant membership)
  * `FOREIGN KEY (tenant_id, assigned_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE SET NULL`
  * `FOREIGN KEY (tenant_id, revoked_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE SET NULL`
- **Application Layer clean() Guard**:
  * Validation: verify `self.cohort.tenant_id == self.tenant_id`, and ensure audit actors belong to current tenant.
- **Constraints & Indexes**:
  * `models.UniqueConstraint(fields=["tenant", "id"], name="learning_cohortsupervision_tenant_id_uniq")`
  * Partial unique index for active supervision: `models.UniqueConstraint(fields=["tenant", "cohort", "mentor_id"], condition=Q(is_active=True), name="learning_cohortsupervision_active_uniq")`
  * One lead per cohort constraint: `models.UniqueConstraint(fields=["tenant", "cohort"], condition=Q(is_active=True, is_lead=True), name="learning_cohortsupervision_single_lead_uniq")`
  * Composite index on `(tenant, mentor_id, is_active)` for fast mentor cohort lookups.

### 2.2 `CohortProgressAggregate` (اسنپ‌شات عملکرد و پیشرفت تجمعی کوهورت - Materialized Presentation Projection)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `cohort`: OneToOneField(`learning.Cohort`, on_delete=CASCADE, related_name="analytics_aggregate")
- `total_enrolled`: PositiveIntegerField(default=0)
- `active_students`: PositiveIntegerField(default=0)
- `completed_students`: PositiveIntegerField(default=0)
- `average_progress_percentage`: DecimalField(max_digits=5, decimal_places=2, default=0.00)
- `average_assessment_score`: DecimalField(max_digits=5, decimal_places=2, default=0.00)
- `completion_rate`: DecimalField(max_digits=5, decimal_places=2, default=0.00)
- `updated_at`: DateTimeField(auto_now=True)
- **Composite Foreign Key Definitions (PostgreSQL 17)**:
  * `FOREIGN KEY (tenant_id, cohort_id) REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE`
- **Application Layer clean() Guard**:
  * Clean guard: `if self.cohort.tenant_id != self.tenant_id: raise ValidationError("Tenant mismatch between CohortProgressAggregate and Cohort.")`
- **Projection Governance & Refresh Pathway**:
  * Presentation-only projection refreshed via authoritative DB-level transaction / `BaseTenantTask` using published-only lessons/assessments denominator.
  * API exposes `updated_at` as `as_of` timestamp in OpenAPI.
- **Constraints & Indexes**:
  * `models.UniqueConstraint(fields=["tenant", "id"], name="learning_cohortprogaggregate_tenant_id_uniq")`
  * `models.UniqueConstraint(fields=["tenant", "cohort"], name="learning_cohortprogaggregate_tenant_cohort_uniq")`
  * Composite index on `(tenant, cohort)` for high-performance dashboard fetches.

### 2.3 `StudentSupervisionAlert` (هشدارهای هوشمند، ایدمپوتنت و ماشین وضعیت پیشرفت تحصیلی فراگیر با FKهای ترکیبی کامل)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `cohort`: ForeignKey(`learning.Cohort`, on_delete=CASCADE, related_name="alerts")
- `student_id`: UUIDField(db_index=True)
- `alert_type`: CharField(max_length=32, choices=[`STALLED_PROGRESS`, `FAILED_ASSESSMENTS`, `AT_RISK_DROPOUT`])
- `severity`: CharField(max_length=16, choices=[`LOW`, `MEDIUM`, `HIGH`])
- `status`: CharField(max_length=16, choices=[`ACTIVE`, `ACKNOWLEDGED`, `RESOLVED`], default=`ACTIVE`, db_index=True)
- `rule_version`: PositiveIntegerField(default=1)
- `deduplication_key`: CharField(max_length=128, unique=True, db_index=True)
- `details`: JSONField(default=dict)
- `schema_version`: PositiveIntegerField(default=1)
- `data_classification`: CharField(max_length=32, default="INTERNAL_EDUCATIONAL_ANALYTICS")
- `acknowledged_at`: DateTimeField(null=True, blank=True)
- `acknowledged_by`: UUIDField(null=True, blank=True)
- `resolved_at`: DateTimeField(null=True, blank=True)
- `resolved_by`: UUIDField(null=True, blank=True)
- `created_at`: DateTimeField(auto_now_add=True)
- **Composite Foreign Key Definitions (PostgreSQL 17)**:
  * `FOREIGN KEY (tenant_id, cohort_id) REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, student_id) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE CASCADE` (Or authoritative tenant membership/synthetic learner target)
  * `FOREIGN KEY (tenant_id, acknowledged_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE SET NULL`
  * `FOREIGN KEY (tenant_id, resolved_by) REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE SET NULL`
- **Application Layer clean() Guard**:
  * Clean guard: `if self.cohort.tenant_id != self.tenant_id: raise ValidationError("Tenant mismatch between StudentSupervisionAlert and Cohort.")`
- **FSM State Machine & Guards**:
  * Transitions: `ACTIVE -> ACKNOWLEDGED`, `ACKNOWLEDGED -> RESOLVED`, `ACTIVE -> RESOLVED` (automatic remediation).
  * Guard: Transition to `ACKNOWLEDGED` requires non-null `acknowledged_at` and `acknowledged_by`. Reverse transitions forbidden.
- **Deduplication Key Format**:
  * `deduplication_key = f"{tenant_id}:{cohort_id}:{student_id}:{alert_type}:{date_window}"`
- **Constraints & Indexes**:
  * `models.UniqueConstraint(fields=["tenant", "id"], name="learning_studentsupalert_tenant_id_uniq")`
  * Unique constraint on `deduplication_key` to enforce complete insert idempotency (`ON CONFLICT DO NOTHING`).
  * Partial unique index: `models.UniqueConstraint(fields=["tenant", "cohort", "student_id", "alert_type"], condition=Q(status="ACTIVE"), name="learning_supalert_active_dedup_uniq")`
  * Composite index on `(tenant, cohort, status, resolved_at)`.

---

## 3. Multi-Tenant Security & Database Invariants (PostgreSQL 17 FORCE RLS)

- Every new table (`learning_cohortsupervision`, `learning_cohortprogressaggregate`, `learning_studentsupervisionalert`) MUST enforce:
  ```sql
  ALTER TABLE learning_cohortsupervision ENABLE ROW LEVEL SECURITY;
  ALTER TABLE learning_cohortsupervision FORCE ROW LEVEL SECURITY;
  
  ALTER TABLE learning_cohortprogressaggregate ENABLE ROW LEVEL SECURITY;
  ALTER TABLE learning_cohortprogressaggregate FORCE ROW LEVEL SECURITY;
  
  ALTER TABLE learning_studentsupervisionalert ENABLE ROW LEVEL SECURITY;
  ALTER TABLE learning_studentsupervisionalert FORCE ROW LEVEL SECURITY;
  ```
- **Policy Definition**: Standardized on canonical project standard:
  ```sql
  CREATE POLICY tenant_isolation_policy ON <table>
  FOR ALL
  TO PUBLIC
  USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
  ```
- **Complete Suite of Composite Foreign Keys (DB Migration Constraint DDL)**:
  * In migration SQL (0024/0025):
  ```sql
  -- 1. Cohort composite FKs
  ALTER TABLE learning_cohortsupervision
    ADD CONSTRAINT fk_cohortsupervision_tenant_cohort
    FOREIGN KEY (tenant_id, cohort_id)
    REFERENCES learning_cohort (tenant_id, id)
    ON DELETE CASCADE;

  ALTER TABLE learning_cohortprogressaggregate
    ADD CONSTRAINT fk_cohortprogressagg_tenant_cohort
    FOREIGN KEY (tenant_id, cohort_id)
    REFERENCES learning_cohort (tenant_id, id)
    ON DELETE CASCADE;

  ALTER TABLE learning_studentsupervisionalert
    ADD CONSTRAINT fk_studentsupalert_tenant_cohort
    FOREIGN KEY (tenant_id, cohort_id)
    REFERENCES learning_cohort (tenant_id, id)
    ON DELETE CASCADE;

  -- 2. CohortSupervision Mentor & Audit Actors Composite FKs (Eliminating Bare UUIDs)
  ALTER TABLE learning_cohortsupervision
    ADD CONSTRAINT fk_cs_tenant_mentor
    FOREIGN KEY (tenant_id, mentor_id)
    REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
    ON DELETE RESTRICT;

  ALTER TABLE learning_cohortsupervision
    ADD CONSTRAINT fk_cs_tenant_assigned_by
    FOREIGN KEY (tenant_id, assigned_by)
    REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
    ON DELETE SET NULL;

  ALTER TABLE learning_cohortsupervision
    ADD CONSTRAINT fk_cs_tenant_revoked_by
    FOREIGN KEY (tenant_id, revoked_by)
    REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
    ON DELETE SET NULL;

  -- 3. StudentSupervisionAlert Student & Audit Actors Composite FKs (Eliminating Bare UUIDs)
  ALTER TABLE learning_studentsupervisionalert
    ADD CONSTRAINT fk_ssa_tenant_student
    FOREIGN KEY (tenant_id, student_id)
    REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
    ON DELETE CASCADE;

  ALTER TABLE learning_studentsupervisionalert
    ADD CONSTRAINT fk_ssa_tenant_acknowledged_by
    FOREIGN KEY (tenant_id, acknowledged_by)
    REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
    ON DELETE SET NULL;

  ALTER TABLE learning_studentsupervisionalert
    ADD CONSTRAINT fk_ssa_tenant_resolved_by
    FOREIGN KEY (tenant_id, resolved_by)
    REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
    ON DELETE SET NULL;
  ```
- **Access Control Matrix & Enforce Architecture (Pinned to Single-Path Application Layer Pattern A)**:
  * Single-Path enforcement inside `CohortSupervisionAccessService` and ViewSets.
  * Mentor requesting assigned cohort data => `200 OK`.
  * Mentor requesting unassigned cohort (even within same tenant) => `404 Not Found` (strict enumeration prevention).
  * Tenant Admin => `200 OK` (full tenant scope).
  * Cross-tenant request or missing context => Fail-closed `0 rows / 404 Not Found`.
  * **Mandatory Negative Test Suite in `test_p3_vs9_supervision_rls.py`**:
    * Attempting to link a `cohort_id` from Tenant B into Tenant A raises DB Composite FK constraint violation.
    * Attempting to link a `mentor_id` or `student_id` from Tenant B into Tenant A raises DB Composite FK constraint violation.
    * Attempting to record audit actor (`assigned_by`, `acknowledged_by`, etc.) from Tenant B raises DB Composite FK violation.

---

## 4. UI/UX & Design Specification (WCAG 2.2 AA & BiDi/RTL)
- **Mentor Supervision Dashboard (`CohortOrchestrationScreen.tsx`)**:
  * نمای کلی عملکرد کوهورت‌ها با کارت‌های متریک غنی و بدون المان‌های کارتونی.
  * جدول فراگیران با ستون‌های پیشرفت، آزمون‌های کد، تمرین‌ها و تگ‌های وضعیت (ACTIVE, ACKNOWLEDGED, RESOLVED).
  * ایزولاسیون BiDi/RTL برای کدها، درصدها و شناسه‌های سنتتیک فراگیران (`<bdi dir="ltr">`).
  * تضاد رنگی بالای ۴.۵:۱ برای برچسب‌های وضعیت (سبز، زرد، قرمز).
  * حداقل مساحت تاچ تارگت ۴۴×۴۴ پیکسل برای دکمه‌های آکاردئون و تایید هشدار.

---

## 5. Non-Goals & Boundaries
- ❌ هیچ‌گونه دسترسی منتور به داده‌های کوهورت‌های نامرتبط مجاز نیست.
- ❌ هیچ‌گونه ذخیره‌سازی اطلاعات هویتی واقعی (PII).
- ❌ محاسبات آماری سنگین در فرانت‌اند مجاز نیست؛ تمام متریک‌ها از دیتابیس دریافت می‌شوند.

---

## 6. Triple Fleet Review Plan & Status
- **Qwen 3.8 Max**: ارکستراسیون کوهورت‌ها، روابط داده‌ای، منطق محاسبات تجمیعی و هشدارهای تحصیلی (`QWEN_SCOPE: PASS` - تأیید نهایی صادر شد).
- **GLM 5.3**: مدل داده، پایداری کوئری‌ها، ایندکس‌های PostgreSQL 17 FORCE RLS، ایزولاسیون چندمستأجری و ماتریس دسترسی ۴۰۴ (در انتظار صدور PASS پس از اعمال کامل قیدهای ارجاعی شش‌گانه).
- **Gemini 3.8**: طراحی بصری داشبورد نظارت، تایپوگرافی RTL، دسته‌بندی هشدارها و استانداردهای WCAG 2.2 AA (`GEMINI_SCOPE: PASS` - تأیید نهایی صادر شد).
