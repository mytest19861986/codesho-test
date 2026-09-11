# P3-MACRO-EPIC-23-25 Boundary Plan & Architecture Specification (v1.0-CANONICAL)

## 1. Epic Overview
- **Epic ID**: `P3-MACRO-EPIC-23-25-CURRICULUM-AUTHORING-QUALITY-AND-RELEASE-OPERATIONS`
- **FA Title**: گردش کار تألیف سرفصل، بازبینی محتوا، حاکمیت روبریک و آمادگی انتشار برنامه آموزشی
- **Branch**: `codex/phase3-product-platform-foundation`
- **Authority Directive**: `COMMANDER_P3_MACRO_EPIC_23_25_DISCOVERY_UNLOCK: GRANTED`
- **Delivery Mode**: `MACRO_FAST_ENTERPRISE` (Single Epic Package, Combined Discovery, Parallel Fleet Review)
- **Scope & Slices**:
  - **P3-VS23**: Curriculum Authoring & Editorial Workflow (`CurriculumDraftWorkspace`, `ContentChangeSet`, `EditorialReview`, `ReviewComment`, `ReviewResolution`, `AuthorAssignment`, `ChangeApprovalRecord`).
  - **P3-VS24**: Learning Assessment Blueprint & Rubric Governance (`AssessmentBlueprint`, `LearningObjectiveMapping`, `RubricDefinition`, `RubricCriterion`, `AssessmentReleaseBinding`, `RubricReviewRecord`).
  - **P3-VS25**: Release Readiness, Change Impact & Program Rollforward (`CurriculumChangeImpact`, `ReleaseReadinessCheck`, `ReleaseReadinessGate`, `CohortRollforwardPlan`, `CurriculumMigrationDecision`, `ReleaseExceptionRecord`).

---

## 2. Hard Invariants & Anti-Patterns (Lines in the Sand)

1. **Anti-Ranking Policy (`STUDENT_RANKING: 0`)**:
   - Zero student ranking, zero leaderboards, zero competitive peer comparisons, zero public percentiles.
   - Zero black-box grading policy or automated algorithmic high-stakes decisions.

2. **Historical Evidence Immutability (`HISTORICAL_EVIDENCE_REBINDING: 0`)**:
   - A learner's historical submissions, evaluations, and progress records MUST remain permanently bound to the exact curriculum, assessment, and rubric version actually experienced.
   - Zero silent historical rebind (`SILENT_HISTORICAL_REBIND: 0`).
   - Zero automatic completed evidence migration (`AUTOMATIC_COMPLETED_EVIDENCE_MIGRATION: 0`).
   - Zero automatic learner reassignment without explicit reviewed governance decision.

3. **Separation of Duties & Editorial FSM**:
   - `AUTHOR_SELF_APPROVAL: DENY` — The author/creator of a content change set or rubric cannot approve their own review submission.
   - `PUBLISHED_CONTENT_DIRECT_EDIT: DENY` — Direct edits on published materials are prohibited; all changes must flow through a versioned draft and editorial review FSM.
   - FSM transitions:
     - Content Change Set: `DRAFT` → `IN_REVIEW` → `CHANGES_REQUESTED` → `APPROVED` → `MERGED_TO_RELEASE`
     - Editorial Review: `PENDING` → `UNDER_REVIEW` → `REJECTED` | `APPROVED`
     - Rubric Definition: `DRAFT` → `ACTIVE` → `SUPERSEDED` | `RETIRED`
     - Release Readiness Gate: `PENDING_EVALUATION` → `PASSED` | `FAILED` | `BLOCKED` | `WAIVED_WITH_AUDIT`

4. **Zero AI Autonomous Authority (`AI_DECISION_AUTHORITY: 0`)**:
   - No autonomous AI curriculum authoring, no autonomous AI grading authority, no autonomous AI release approvals.
   - All AI integrations, if any advisory tools exist in future, remain synthetic and advisory only with human-in-the-loop decision-makers.

5. **Data Privacy & Synthetic-Only (`REAL_PII: 0`)**:
   - Enforcement of the project-wide 21-key PII exclusion list on all free-text/JSONB attributes.
   - Prohibited: real child data, real guardian onboarding, real guardian consent, live communication providers (SMS/Email), live payment providers, production deployment credentials.

---

## 3. Database Schema & PostgreSQL 17 Architecture

1. **Multi-Tenancy & RLS**:
   - Every single table in Epic 23-25 contains `tenant_id uuid NOT NULL`.
   - `ALTER TABLE ... ENABLE ROW LEVEL SECURITY; ALTER TABLE ... FORCE ROW LEVEL SECURITY;` applied unconditionally.
   - Strict Fail-Closed RLS Policy:
     `USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);`

2. **Foreign Key Topology (Zero Bare UUIDs)**:
   - 100% composite foreign keys enforcing `(tenant_id, target_id)`.
   - Relational linkage to Epic 20-22 canonical models (`CurriculumVersion`, `CourseRelease`, `ModuleReleaseSnapshot`, `LessonReleaseSnapshot`).
   - Deferrable constraints where circular actor references exist (`ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`).

3. **Immutability & Access Revocation**:
   - `REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM PUBLIC, app_role;`
   - `REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM PUBLIC, app_role;`
   - `REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM PUBLIC, app_role;`
   - `REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM PUBLIC, app_role;`

4. **Concurrency & Anti-Race Guards**:
   - Unique constraints on active draft workspaces per curriculum version.
   - Advisory locking / `select_for_update()` during approval transitions to prevent double-approval side effects.
   - Outbox pattern with transactional atomicity (`append_outbox_event`) including exact `aggregate_type` and `aggregate_id`.

---

## 4. UI/UX Accessibility & BiDi Specifications

1. **Operational Workspaces**:
   - `CurriculumAuthoringWorkspace`: Structured authoring, learning objective mapping, and draft change sets.
   - `EditorialReviewWorkspace`: Diff inspection, side-by-side review comments, separation of duties approval action.
   - `AssessmentRubricWorkspace`: Visual criterion weighting, scoring scale definitions, non-ranking pedagogical guidance.
   - `ReleaseReadinessControlCenter`: Pre-flight readiness gates inspection, change impact visual graph, cohort rollforward plan.
2. **WCAG 2.2 AA Compliance**:
   - Interactive touch targets $\ge 44 \times 44\text{ px}$.
   - Text contrast $\ge 4.5:1$, UI controls contrast $\ge 3.0:1$.
   - Logical tab orders, explicit focus rings, screen-reader aria labels.
3. **BiDi / RTL Isolation**:
   - Persian native typography with CSS logical properties (`margin-inline`, `padding-inline`).
   - Technical metadata (SemVer, UUIDs, code snippets, timestamps) isolated in `<bdi dir="ltr">`.

---

## 5. Negative Test Proof Matrix (N1 - N35)

| ID | Domain Category | Target Invariant | Expected Behavior / Proof |
|:---|:---|:---|:---|
| **N1** | Multi-Tenancy | Query without `app.current_tenant` GUC | Fail-closed: 0 rows returned |
| **N2** | Multi-Tenancy | Cross-tenant UUID direct query | Rejection: 0 rows leaked across tenant boundaries |
| **N3** | Multi-Tenancy | Malformed tenant GUC format | Fail-closed: Safe handling, 0 rows leaked |
| **N4** | Composite FK | Cross-tenant draft or change set reference | IntegrityError: Composite foreign key violation |
| **N5** | Composite FK | Cross-tenant assessment blueprint reference | IntegrityError: Composite foreign key violation |
| **N6** | Composite FK | Cross-tenant rollforward plan reference | IntegrityError: Composite foreign key violation |
| **N7** | Separation of Duties | Author attempts to self-approve EditorialReview | 400 ValidationError / 403 Forbidden (`author_self_approval_denied`) |
| **N8** | Content Immutability | Direct UPDATE on `PUBLISHED` content | Rejection: CheckConstraint violation / ReadOnlyError |
| **N9** | Content Immutability | Direct DELETE on `ChangeApprovalRecord` | Database Error: Permission Denied (REVOKE DELETE) |
| **N10** | Content Immutability | Direct UPDATE on `RubricReviewRecord` | Database Error: Permission Denied (REVOKE UPDATE) |
| **N11** | Content Immutability | Direct UPDATE/DELETE on `ReleaseExceptionRecord` | Database Error: Permission Denied (REVOKE UPDATE, DELETE) |
| **N12** | Content Immutability | Direct UPDATE on `CurriculumChangeImpact` | Database Error: Permission Denied (REVOKE UPDATE) |
| **N13** | Anti-Ranking | Query parameter requesting student percentile rank | 400 Bad Request: `ranking_queries_prohibited` |
| **N14** | Anti-Ranking | Query parameter requesting cohort peer leaderboard | 400 Bad Request: `ranking_queries_prohibited` |
| **N15** | Anti-Ranking | Model attempting to persist competitive score rank | ValidationError: `student_ranking_prohibited` |
| **N16** | Rubric Integrity | Retroactive mutation of completed assessment rubric | ValidationError / IntegrityError: `historical_rubric_immutable` |
| **N17** | Rubric Integrity | Rubric criterion weights sum $\neq 100\%$ | CheckConstraint violation / ValidationError |
| **N18** | Rubric Integrity | Negative or zero rubric criterion score scale | CheckConstraint violation (`chk_rubric_criterion_weight_pos`) |
| **N19** | Evidence Integrity | Attempt to silently rebind historical learner evidence | ValidationError / IntegrityError: `historical_rebind_prohibited` |
| **N20** | Evidence Integrity | Attempt automated completed evidence migration | ValidationError: `automated_evidence_migration_prohibited` |
| **N21** | FSM Transition | Illegal transition: `APPROVED` -> `DRAFT` in ChangeSet | FSMValidationError (400 Bad Request) |
| **N22** | FSM Transition | Illegal transition: `SUPERSEDED` -> `ACTIVE` in Rubric | FSMValidationError (400 Bad Request) |
| **N23** | FSM Transition | Bypassing editorial review directly to release | ValidationError: `review_required_before_release` |
| **N24** | Release Readiness | Releasing curriculum with `FAILED` blocking gate | 400 Bad Request: `release_readiness_gate_blocked` |
| **N25** | Release Readiness | Waiving readiness gate without audit justification | ValidationError: `gate_waiver_requires_audit_justification` |
| **N26** | Rollforward Safety | Rollforward plan targeting inactive cohort | ValidationError: `cohort_not_eligible_for_rollforward` |
| **N27** | Concurrency | Simultaneous approval of same content change set | Handled via transaction lock; zero duplicate approvals |
| **N28** | Concurrency | Competing release readiness gate evaluations | Handled via transaction lock; idempotent state |
| **N29** | PII Blacklist | Injecting PII key (`'national_id'`) into draft change set | CheckConstraint / ValidationError |
| **N30** | PII Blacklist | Injecting PII key (`'phone_number'`) into review comment | CheckConstraint / ValidationError |
| **N31** | PII Blacklist | Injecting PII key (`'iban'`) into release exception reason | CheckConstraint / ValidationError |
| **N32** | Outbox Idempotency | Replaying outbox event emission for change approval | Idempotent / Deduped: zero duplicate downstream events |
| **N33** | Zero Bare UUID | Foreign key inspection verifying 0 bare UUIDs | 100% composite `(tenant_id, target_id)` verified |
| **N34** | Role Authorization | Learner role attempting to create ContentChangeSet | 403 Forbidden |
| **N35** | Role Authorization | Learner role attempting to evaluate ReadinessGate | 403 Forbidden |
