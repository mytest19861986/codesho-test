# P3-MACRO-EPIC-23-25 Discovery Dossier

## 1. Executive Summary
- **Target Epic**: `P3-MACRO-EPIC-23-25-CURRICULUM-AUTHORING-QUALITY-AND-RELEASE-OPERATIONS`
- **Delivery Mode**: `MACRO_FAST_ENTERPRISE`
- **Status**: DISCOVERY PHASE (Pre-Review Fleet Consensus)
- **Primary Objective**: Establish a controlled curriculum authoring and draft change set workflow, separation-of-duties editorial review, non-ranking assessment blueprint and rubric governance, and pre-flight release readiness gates with safe cohort rollforward plans.

---

## 2. Invariant & Safety Checklist
- [x] **Zero Student Ranking (`STUDENT_RANKING: 0`)**: No peer ranks, no leaderboards, no percentile score comparisons, no gamified ranking badges.
- [x] **Historical Evidence Immutability (`HISTORICAL_EVIDENCE_REBINDING: 0`)**: Past learner submissions and evaluations remain permanently pinned to historical versions.
- [x] **Separation of Duties (`AUTHOR_SELF_APPROVAL: DENY`)**: An author of a content change set cannot approve their own review.
- [x] **Published Immutability**: Direct edits to published content are denied; all modifications require a new versioned draft change set.
- [x] **Zero AI Autonomous Authority (`AI_DECISION_AUTHORITY: 0`)**: No autonomous AI curriculum generation or automated high-stakes evaluation authority.
- [x] **Synthetic Only & Privacy Guard (`REAL_PII: 0`)**: All JSONB and free-text fields enforce the 21-key PII exclusion list. Zero real child, guardian, or live provider integrations.
- [x] **PostgreSQL 17 FORCE RLS**: Mandatory on all 19 new tables with fail-closed default.
- [x] **Zero Bare UUIDs**: 100% composite foreign keys `(tenant_id, target_id)`.
- [x] **Append-Only Audits**: `ChangeApprovalRecord`, `RubricReviewRecord`, `ReleaseExceptionRecord`, and `CurriculumChangeImpact` have `REVOKE UPDATE, DELETE` enforced.
- [x] **WCAG 2.2 AA & BiDi Isolation**: LTR data (SemVer, codes, metrics) wrapped in `<bdi dir="ltr">`, minimum 44px touch targets.

---

## 3. Fleet Review Focus Areas
1. **Qwen (Lifecycle, FSM & Governance Invariants)**:
   - Verification of FSM transitions for `ContentChangeSet` (`DRAFT` -> `IN_REVIEW` -> `CHANGES_REQUESTED` -> `APPROVED` -> `MERGED_TO_RELEASE`).
   - Strict enforcement of separation of duties (`author != reviewer`).
   - Verification of rubric lifecycle, assessment version binding, and prohibition of historical evidence rebinding.
   - Controlled cohort rollforward lifecycle without retroactive mutation.
2. **GLM (Database Schema, PostgreSQL 17 RLS & Security Architecture)**:
   - Verification of PostgreSQL 17 FORCE RLS, NOBYPASSRLS, and `p3_epic23_25_tenant_isolation_policy`.
   - Verification of 100% composite foreign key closure `(tenant_id, target_id)` and absence of bare UUIDs.
   - Verification of immutable audit table permissions (`REVOKE UPDATE, DELETE`).
   - Concurrency locking, partial unique constraints, and 21-key PII regex check constraints.
3. **Gemini (UX Specification, Accessibility & BiDi)**:
   - Review of `CurriculumAuthoringWorkspace`, `EditorialReviewWorkspace`, `AssessmentRubricWorkspace`, and `ReleaseReadinessControlCenter`.
   - Verification of WCAG 2.2 AA compliance, $\ge 44 \times 44\text{ px}$ touch targets, high contrast, and logical tab orders.
   - Persian native RTL typography and strict BiDi isolation via `<bdi dir="ltr">`.
   - Absolute absence of competitive student ranking, leaderboards, or punitive behavioral indicators.
