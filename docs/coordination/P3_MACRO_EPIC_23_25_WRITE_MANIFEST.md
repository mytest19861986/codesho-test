# P3-MACRO-EPIC-23-25 Write Manifest & Implementation Blueprint

## 1. Package Overview
- **Epic ID**: `P3-MACRO-EPIC-23-25-CURRICULUM-AUTHORING-QUALITY-AND-RELEASE-OPERATIONS`
- **Scope**:
  - `P3-VS23`: Curriculum Authoring & Editorial Workflow
  - `P3-VS24`: Learning Assessment Blueprint & Rubric Governance
  - `P3-VS25`: Release Readiness, Change Impact & Program Rollforward
- **Mode**: `MACRO_FAST_ENTERPRISE`
- **Zero Wildcards**: Strictly 100% exact absolute/relative paths enumerated below.

---

## 2. Models to Add in `backend/modules/learning/models.py`
### P3-VS23: Authoring & Editorial Workflow
1. `CurriculumDraftWorkspace`: Draft environment bound to a course and base curriculum version.
2. `ContentChangeSet`: Structured batch of content changes with FSM (`DRAFT` -> `IN_REVIEW` -> `CHANGES_REQUESTED` -> `APPROVED` -> `MERGED_TO_RELEASE`).
3. `EditorialReview`: Peer review record with separation-of-duties (`decision`, `review_notes`).
4. `ReviewComment`: Entity-targeted inline editorial comments with 21-key PII exclusion.
5. `ReviewResolution`: Formal resolution and sign-off on review feedback.
6. `AuthorAssignment`: Roles for primary author, contributor, and curator.
7. `ChangeApprovalRecord`: Immutable audit trail with cryptographic approval hash.

### P3-VS24: Assessment Blueprint & Rubric Governance
8. `AssessmentBlueprint`: Versioned blueprint structuring course competencies and evaluation architecture.
9. `LearningObjectiveMapping`: Mapping of learning objectives with Bloom taxonomy levels and percentage weights.
10. `RubricDefinition`: Qualitative evaluation criteria with `is_anti_ranking_compliant = True`.
11. `RubricCriterion`: Granular evaluation criteria scales and weighting.
12. `AssessmentReleaseBinding`: Immutable binding between `CourseRelease`, `AssessmentBlueprint`, and `RubricDefinition`.
13. `RubricReviewRecord`: Immutable audit trail of pedagogical rubric reviews.

### P3-VS25: Release Readiness & Program Rollforward
14. `CurriculumChangeImpact`: Immutable analysis record of version diffs, impact level, and affected cohorts.
15. `ReleaseReadinessCheck`: Automated pre-flight check evaluations (editorial, rubric, asset coverage).
16. `ReleaseReadinessGate`: Blocking / non-blocking readiness gates controlling release deployment.
17. `CohortRollforwardPlan`: Controlled rollout plan targeting cohorts without retroactive evidence migration.
18. `CurriculumMigrationDecision`: Formal decision record (`PROCEED`, `HALT`, `EXCEPTION_REQUIRED`).
19. `ReleaseExceptionRecord`: Immutable audit record of granted readiness gate waivers.

---

## 3. Database Migrations
- `backend/modules/learning/migrations/0044_p3_macro_epic_23_25_models.py`:
  Defines all 19 models, composite foreign keys `(tenant_id, target_id)`, CheckConstraints, and PII guard regexes.
- `backend/modules/learning/migrations/0045_p3_macro_epic_23_25_rls_force.py`:
  Applies PostgreSQL 17 `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, `p3_epic23_25_tenant_isolation_policy`, and `REVOKE UPDATE, DELETE` on immutable tables (`ChangeApprovalRecord`, `RubricReviewRecord`, `ReleaseExceptionRecord`, `CurriculumChangeImpact`).

---

## 4. Service Layer & Outbox Events
- `backend/modules/learning/curriculum_authoring_service.py`:
  - `create_draft_workspace(tenant_id, course_id, base_version_id, user_id, title)`
  - `submit_change_set_for_review(tenant_id, change_set_id, author_id)` -> emits `curriculum.changeset.submitted`
  - `record_editorial_decision(tenant_id, change_set_id, reviewer_id, decision, justification)` -> enforces separation of duties (`author_id != reviewer_id`), emits `curriculum.changeset.approved` / `curriculum.changeset.rejected`
  - `create_assessment_blueprint(tenant_id, course_id, title, intent)`
  - `define_rubric(tenant_id, blueprint_id, title, criteria_list)` -> validates total weight = 100% and anti-ranking compliance
  - `bind_assessment_to_release(tenant_id, release_id, blueprint_id, rubric_id)` -> enforces historical immutability
  - `evaluate_release_readiness(tenant_id, version_id)` -> runs checks and updates gates
  - `create_cohort_rollforward_plan(tenant_id, cohort_id, target_release_id, mode)` -> prevents silent historical rebind

---

## 5. API Serializers, Views & URL Routing
- `backend/modules/learning/authoring_serializers.py`: DRF serializers with PII sanitization and composite validation.
- `backend/modules/learning/authoring_views.py`:
  - `CurriculumDraftWorkspaceViewSet`
  - `ContentChangeSetViewSet`
  - `EditorialReviewViewSet`
  - `AssessmentBlueprintViewSet`
  - `RubricDefinitionViewSet`
  - `ReleaseReadinessGateViewSet`
  - `CohortRollforwardPlanViewSet`
- `backend/modules/learning/urls.py`: Wire new viewsets under `/api/v1/learning/authoring/` and `/api/v1/learning/readiness/`.

---

## 6. Frontend Workspace Components
- `frontend/src/components/curriculum/CurriculumAuthoringWorkspace.tsx`:
  - Visual draft editor, change-set manager, and editorial review interface.
  - Rubric designer with criterion weighting and anti-ranking safeguards.
  - Release readiness control center with pre-flight gates and rollforward impact viewer.
- `frontend/src/components/curriculum/curriculum_authoring.module.css`:
  - High-contrast styles conforming to WCAG 2.2 AA.
  - Minimum touch targets $\ge 44 \times 44\text{ px}$.
  - Logical CSS properties (`margin-inline`, `padding-inline`) and `<bdi dir="ltr">` wrappers.
- `frontend/src/app/dashboard/admin/curriculum-authoring/page.tsx`:
  - Dedicated administrative dashboard route.

---

## 7. Integrated Negative Matrix & Proof Tests
- `backend/tests/test_p3_macro_epic_23_25_operations.py`:
  - Automated Django test suite testing all 35 matrix invariants (N1 to N35).
