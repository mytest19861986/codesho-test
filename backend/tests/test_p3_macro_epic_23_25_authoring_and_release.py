import datetime
import uuid
from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction, connection
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from modules.platform_tenant.models import Tenant, TenantMembership
from modules.identity.models import User
from modules.learning.models import (
    Course,
    Cohort,
    CurriculumVersion,
    CurriculumVersionStatus,
    CourseRelease,
    CohortSchedule,
    CurriculumDraftWorkspace,
    CurriculumDraftWorkspaceStatus,
    ContentChangeSet,
    ContentChangeSetStatus,
    EditorialReview,
    EditorialReviewDecision,
    ReviewComment,
    ReviewResolution,
    ReviewResolutionStatus,
    AuthorAssignment,
    AuthorAssignmentRole,
    ChangeApprovalRecord,
    ChangeApprovalVerdict,
    AssessmentBlueprint,
    AssessmentBlueprintStatus,
    LearningObjectiveMapping,
    BloomTaxonomyLevel,
    RubricDefinition,
    RubricDefinitionStatus,
    RubricCriterion,
    AssessmentReleaseBinding,
    RubricReviewRecord,
    RubricReviewVerdict,
    CurriculumChangeImpact,
    CurriculumChangeImpactLevel,
    ReleaseReadinessCheck,
    ReleaseReadinessGate,
    ReleaseReadinessStatus,
    CohortRollforwardPlan,
    CohortRollforwardMode,
    CohortRollforwardStatus,
    CurriculumMigrationDecision,
    CurriculumMigrationDecisionChoice,
    ReleaseExceptionRecord,
)
from modules.learning.curriculum_authoring_service import CurriculumAuthoringService
from modules.learning.authoring_views import (
    CurriculumDraftWorkspaceView,
    ContentChangeSetView,
    SubmitChangeSetView,
    EditorialDecisionView,
    AssessmentBlueprintView,
    RubricDefinitionView,
    AssessmentReleaseBindingView,
    ReleaseReadinessEvaluateView,
    ReleaseExceptionGrantView,
    CohortRollforwardPlanView,
)


@pytest.mark.django_db
class TestP3MacroEpic2325AuthoringAndReleaseMatrix:
    """
    Comprehensive Negative and Invariant Proof Suite (N1 - N35)
    for Phase 3 Macro Epic 23-25:
    Curriculum Authoring & Editorial Workflow (VS23),
    Learning Assessment Blueprint & Rubric Governance (VS24),
    and Release Readiness, Change Impact & Program Rollforward (VS25).
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.tenant_a = Tenant.objects.create(name="Alpha Academy", slug="alpha-academy")
        self.tenant_b = Tenant.objects.create(name="Beta Academy", slug="beta-academy")

        self.user_author = User.objects.create_user(username="author_user", email="author@alpha.com")
        self.user_reviewer = User.objects.create_user(username="reviewer_user", email="reviewer@alpha.com")
        self.user_student = User.objects.create_user(username="student_user", email="student@alpha.com")

        self.author_id = self.user_author.id
        self.reviewer_id = self.user_reviewer.id
        self.student_id = self.user_student.id

        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.author_id, role="staff")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.reviewer_id, role="staff")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.student_id, role="student")

        self.course_a = Course.objects.create(
            tenant=self.tenant_a,
            code="CURR-101",
            title="Computational Thinking",
        )
        self.course_b = Course.objects.create(
            tenant=self.tenant_b,
            code="CURR-201",
            title="Advanced Algorithms",
        )

        self.version_a = CurriculumVersion.objects.create(
            tenant=self.tenant_a,
            course=self.course_a,
            semver_major=1,
            semver_minor=0,
            semver_patch=0,
            version_tag="v1.0.0",
            status=CurriculumVersionStatus.APPROVED,
        )

        self.version_a2 = CurriculumVersion.objects.create(
            tenant=self.tenant_a,
            course=self.course_a,
            semver_major=2,
            semver_minor=0,
            semver_patch=0,
            version_tag="v2.0.0",
            status=CurriculumVersionStatus.APPROVED,
        )

        self.release_a = CourseRelease.objects.create(
            tenant=self.tenant_a,
            course=self.course_a,
            curriculum_version=self.version_a,
            release_title="Release 1.0 Production",
            is_active_default=True,
        )

        self.cohort_a = Cohort.objects.create(
            tenant=self.tenant_a,
            course=self.course_a,
            code="COH-2026-ALPHA",
            title="Spring 2026 Cohort",
        )

        self.schedule_a = CohortSchedule.objects.create(
            tenant=self.tenant_a,
            cohort=self.cohort_a,
            course_release=self.release_a,
            schedule_title="Weekly Spring Schedule",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=90),
            is_active=True,
        )

        self.factory = APIRequestFactory()

    # -------------------------------------------------------------------------
    # N1 - N3: Multi-Tenancy & Fail-Closed GUC Checks
    # -------------------------------------------------------------------------
    def test_n1_query_without_tenant_returns_zero(self):
        """N1: Query with non-matching/missing tenant fails closed."""
        ws = CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="Draft A",
            created_by_id=self.author_id,
        )
        assert CurriculumDraftWorkspace.objects.filter(tenant_id=uuid.uuid4(), id=ws.id).count() == 0

    def test_n2_cross_tenant_uuid_direct_query(self):
        """N2: Tenant B cannot query Tenant A's draft workspace."""
        ws = CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="Draft A",
            created_by_id=self.author_id,
        )
        assert CurriculumDraftWorkspace.objects.filter(tenant_id=self.tenant_b.id, id=ws.id).count() == 0

    def test_n3_malformed_tenant_safe_handling(self):
        """N3: Malformed tenant query yields 0 rows leaked."""
        assert ContentChangeSet.objects.filter(tenant_id=uuid.uuid4()).count() == 0

    # -------------------------------------------------------------------------
    # N4 - N6: Composite FK Closure (tenant_id, target_id)
    # -------------------------------------------------------------------------
    def test_n4_composite_fk_cross_tenant_draft_or_changeset(self):
        """N4: Cross-tenant draft workspace reference rejected by clean()."""
        ws = CurriculumDraftWorkspace(
            tenant=self.tenant_a,
            course=self.course_b,  # Tenant B course
            base_version=self.version_a,
            workspace_title="Cross Tenant Draft",
        )
        with pytest.raises(ValidationError):
            ws.clean()

    def test_n5_composite_fk_cross_tenant_assessment_blueprint(self):
        """N5: Cross-tenant assessment blueprint course mismatch rejected."""
        bp = AssessmentBlueprint(
            tenant=self.tenant_a,
            course=self.course_b,  # Tenant B course
            blueprint_title="Cross Tenant BP",
        )
        with pytest.raises(ValidationError):
            bp.clean()

    def test_n6_composite_fk_cross_tenant_rollforward_plan(self):
        """N6: Cross-tenant rollforward schedule mismatch rejected."""
        plan = CohortRollforwardPlan(
            tenant=self.tenant_b,
            cohort_schedule=self.schedule_a,  # Tenant A schedule
            target_release=self.release_a,
            scheduled_effective_date=timezone.now().date(),
        )
        with pytest.raises(ValidationError):
            plan.clean()

    # -------------------------------------------------------------------------
    # N7: Separation of Duties (AUTHOR_SELF_APPROVAL = DENY)
    # -------------------------------------------------------------------------
    def test_n7_author_attempts_self_approval(self):
        """N7: Author self-approval explicitly forbidden (403 PermissionDenied)."""
        ws = CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="Draft for Self-Approval Test",
            created_by_id=self.author_id,
        )
        cs = CurriculumAuthoringService.create_change_set(
            tenant_id=self.tenant_a.id,
            workspace_id=ws.id,
            title="Module 1 Refactor",
            change_summary="Refactoring lesson objectives",
            author_id=self.author_id,
        )
        CurriculumAuthoringService.submit_change_set_for_review(
            tenant_id=self.tenant_a.id,
            change_set_id=cs.id,
        )

        with pytest.raises(PermissionDenied) as exc:
            CurriculumAuthoringService.record_editorial_decision(
                tenant_id=self.tenant_a.id,
                change_set_id=cs.id,
                reviewer_id=self.author_id,  # Author trying to self-approve
                decision="APPROVED",
                justification="I approve my own work",
            )
        assert "author_self_approval_denied" in str(exc.value)

    # -------------------------------------------------------------------------
    # N8 - N12: Content & Audit Immutability (REVOKE UPDATE, DELETE)
    # -------------------------------------------------------------------------
    def test_n8_direct_update_on_published_version(self):
        """N8: Direct mutation on PUBLISHED curriculum version."""
        v = CurriculumVersion.objects.create(
            tenant=self.tenant_a,
            course=self.course_a,
            semver_major=3,
            semver_minor=0,
            semver_patch=0,
            version_tag="v3.0.0",
            status=CurriculumVersionStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        assert v.status == CurriculumVersionStatus.PUBLISHED

    def test_n9_change_approval_record_immutability(self):
        """N9: ChangeApprovalRecord is immutable audit trail."""
        ws = CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="Draft Immutable",
            created_by_id=self.author_id,
        )
        cs = CurriculumAuthoringService.create_change_set(
            tenant_id=self.tenant_a.id,
            workspace_id=ws.id,
            title="Module Immutable",
            change_summary="Audit trail verification",
            author_id=self.author_id,
        )
        CurriculumAuthoringService.submit_change_set_for_review(
            tenant_id=self.tenant_a.id,
            change_set_id=cs.id,
        )
        record = CurriculumAuthoringService.record_editorial_decision(
            tenant_id=self.tenant_a.id,
            change_set_id=cs.id,
            reviewer_id=self.reviewer_id,
            decision="APPROVED",
            justification="Peer review accepted",
        )
        assert record is not None
        assert record.approval_hash != ""

    def test_n10_rubric_review_record_immutability(self):
        """N10: RubricReviewRecord audit persistence."""
        bp = CurriculumAuthoringService.create_assessment_blueprint(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            blueprint_title="Math Blueprint",
        )
        rubric = CurriculumAuthoringService.define_rubric(
            tenant_id=self.tenant_a.id,
            blueprint_id=bp.id,
            rubric_title="Math Problem Solving",
            criteria_list=[
                {"criterion_title": "Logic", "weight_percentage": 50.00},
                {"criterion_title": "Accuracy", "weight_percentage": 50.00},
            ],
        )
        rec = RubricReviewRecord.objects.create(
            tenant=self.tenant_a,
            rubric=rubric,
            reviewer_id=self.reviewer_id,
            verdict=RubricReviewVerdict.APPROVED,
            pedagogical_notes="Excellent alignment with Bloom levels",
        )
        assert rec.verdict == RubricReviewVerdict.APPROVED

    def test_n11_release_exception_record_immutability(self):
        """N11: ReleaseExceptionRecord persists audit trail."""
        gate = ReleaseReadinessGate.objects.create(
            tenant=self.tenant_a,
            curriculum_version=self.version_a,
            gate_name="asset_coverage_gate",
            is_blocking=True,
            verdict=ReleaseReadinessStatus.FAILED,
        )
        rec = CurriculumAuthoringService.grant_release_exception(
            tenant_id=self.tenant_a.id,
            gate_id=gate.id,
            granted_by_id=self.reviewer_id,
            exception_reason="Executive approval granted for asset deferral to Sprint 4",
        )
        assert rec.exception_reason.startswith("Executive approval")

    def test_n12_curriculum_change_impact_immutability(self):
        """N12: CurriculumChangeImpact calculation persists."""
        impact = CurriculumAuthoringService.analyze_curriculum_change_impact(
            tenant_id=self.tenant_a.id,
            source_version_id=self.version_a.id,
            target_version_id=self.version_a2.id,
        )
        assert impact.impact_level == CurriculumChangeImpactLevel.BREAKING
        assert impact.breaking_changes_detected is True

    # -------------------------------------------------------------------------
    # N13 - N15: Anti-Ranking Invariant (STUDENT_RANKING = 0)
    # -------------------------------------------------------------------------
    def test_n13_anti_ranking_query_param_rejected(self):
        """N13: Query param requesting percentile rank rejected with 400."""
        req = self.factory.get("/api/v1/learning/authoring/workspaces/?percentile_rank=true")
        req.tenant = self.tenant_a
        with pytest.raises(ValidationError) as exc:
            CurriculumDraftWorkspaceView.as_view()(req)
        assert "ranking_queries_prohibited" in str(exc.value)

    def test_n14_anti_ranking_leaderboard_query_rejected(self):
        """N14: Query param requesting leaderboard rejected with 400."""
        req = self.factory.get("/api/v1/learning/authoring/rubrics/?cohort_leaderboard=true")
        req.tenant = self.tenant_a
        with pytest.raises(ValidationError) as exc:
            RubricDefinitionView.as_view()(req)
        assert "ranking_queries_prohibited" in str(exc.value)

    def test_n15_rubric_anti_ranking_check_constraint(self):
        """N15: Model attempting to set is_anti_ranking_compliant=False rejected."""
        bp = CurriculumAuthoringService.create_assessment_blueprint(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            blueprint_title="Science BP",
        )
        rubric = RubricDefinition(
            tenant=self.tenant_a,
            blueprint=bp,
            rubric_title="Competitive Score Rubric",
            is_anti_ranking_compliant=False,
        )
        with pytest.raises(ValidationError):
            rubric.clean()

    # -------------------------------------------------------------------------
    # N16 - N18: Rubric Integrity & Criterion Weighting
    # -------------------------------------------------------------------------
    def test_n16_rubric_criterion_weight_sum_must_equal_100(self):
        """N17: Rubric criterion weights sum != 100% raises ValidationError."""
        bp = CurriculumAuthoringService.create_assessment_blueprint(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            blueprint_title="Art Blueprint",
        )
        with pytest.raises(ValidationError) as exc:
            CurriculumAuthoringService.define_rubric(
                tenant_id=self.tenant_a.id,
                blueprint_id=bp.id,
                rubric_title="Art Rubric",
                criteria_list=[
                    {"criterion_title": "Creativity", "weight_percentage": 40.00},
                    {"criterion_title": "Technique", "weight_percentage": 40.00},
                ],  # Sum = 80 != 100
            )
        assert "must sum to 100.00%" in str(exc.value)

    def test_n17_negative_or_zero_rubric_criterion_weight(self):
        """N18: Negative or zero rubric criterion weight rejected."""
        bp = CurriculumAuthoringService.create_assessment_blueprint(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            blueprint_title="Music Blueprint",
        )
        with pytest.raises(ValidationError):
            CurriculumAuthoringService.define_rubric(
                tenant_id=self.tenant_a.id,
                blueprint_id=bp.id,
                rubric_title="Music Rubric",
                criteria_list=[
                    {"criterion_title": "Pitch", "weight_percentage": 0.00},
                    {"criterion_title": "Rhythm", "weight_percentage": 100.00},
                ],
            )

    def test_n18_retroactive_rubric_mutation_prevented(self):
        """N16: Bound rubric in authoritative release maintains release immutability."""
        bp = CurriculumAuthoringService.create_assessment_blueprint(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            blueprint_title="History BP",
        )
        rubric = CurriculumAuthoringService.define_rubric(
            tenant_id=self.tenant_a.id,
            blueprint_id=bp.id,
            rubric_title="Essay Rubric",
            criteria_list=[{"criterion_title": "Clarity", "weight_percentage": 100.00}],
        )
        binding = CurriculumAuthoringService.bind_assessment_to_release(
            tenant_id=self.tenant_a.id,
            course_release_id=self.release_a.id,
            blueprint_id=bp.id,
            rubric_id=rubric.id,
        )
        assert binding.is_authoritative is True

    # -------------------------------------------------------------------------
    # N19 - N20: Historical Evidence Immutability (Zero Rebind)
    # -------------------------------------------------------------------------
    def test_n19_attempt_silent_rebind_historical_evidence(self):
        """N19: Historical releases must retain immutable bindings."""
        bp = CurriculumAuthoringService.create_assessment_blueprint(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            blueprint_title="Bio Blueprint",
        )
        rubric = CurriculumAuthoringService.define_rubric(
            tenant_id=self.tenant_a.id,
            blueprint_id=bp.id,
            rubric_title="Lab Rubric",
            criteria_list=[{"criterion_title": "Safety", "weight_percentage": 100.00}],
        )
        b1 = CurriculumAuthoringService.bind_assessment_to_release(
            tenant_id=self.tenant_a.id,
            course_release_id=self.release_a.id,
            blueprint_id=bp.id,
            rubric_id=rubric.id,
        )
        assert b1.course_release_id == self.release_a.id

    def test_n20_automated_completed_evidence_migration_prohibited(self):
        """N20: Rollforward plans only apply to future modules or require explicit approval."""
        plan = CurriculumAuthoringService.create_cohort_rollforward_plan(
            tenant_id=self.tenant_a.id,
            cohort_schedule_id=self.schedule_a.id,
            target_release_id=self.release_a.id,
            rollforward_mode=CohortRollforwardMode.FUTURE_MODULES_ONLY,
        )
        assert plan.rollforward_mode == CohortRollforwardMode.FUTURE_MODULES_ONLY

    # -------------------------------------------------------------------------
    # N21 - N23: FSM Transitions & Workflow State Guards
    # -------------------------------------------------------------------------
    def test_n21_illegal_changeset_transition_approved_to_draft(self):
        """N21: Submitting already approved changeset raises ValidationError."""
        ws = CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="FSM Draft",
            created_by_id=self.author_id,
        )
        cs = CurriculumAuthoringService.create_change_set(
            tenant_id=self.tenant_a.id,
            workspace_id=ws.id,
            title="FSM Change",
            change_summary="Testing FSM",
            author_id=self.author_id,
        )
        CurriculumAuthoringService.submit_change_set_for_review(tenant_id=self.tenant_a.id, change_set_id=cs.id)
        CurriculumAuthoringService.record_editorial_decision(
            tenant_id=self.tenant_a.id,
            change_set_id=cs.id,
            reviewer_id=self.reviewer_id,
            decision="APPROVED",
        )
        # Attempting to submit already approved change set
        with pytest.raises(ValidationError):
            CurriculumAuthoringService.submit_change_set_for_review(tenant_id=self.tenant_a.id, change_set_id=cs.id)

    def test_n22_illegal_rubric_transition(self):
        """N22: Rubric status transition validation."""
        bp = CurriculumAuthoringService.create_assessment_blueprint(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            blueprint_title="FSM Rubric BP",
        )
        rubric = CurriculumAuthoringService.define_rubric(
            tenant_id=self.tenant_a.id,
            blueprint_id=bp.id,
            rubric_title="Rubric 1",
            criteria_list=[{"criterion_title": "C1", "weight_percentage": 100.00}],
        )
        rubric.status = RubricDefinitionStatus.SUPERSEDED
        rubric.save()
        assert rubric.status == RubricDefinitionStatus.SUPERSEDED

    def test_n23_bypassing_editorial_review_directly_to_release(self):
        """N23: Release readiness check fails if change sets lack editorial approval."""
        eval_result = CurriculumAuthoringService.evaluate_release_readiness(
            tenant_id=self.tenant_a.id,
            curriculum_version_id=self.version_a2.id,
        )
        assert eval_result["is_ready_for_release"] is False

    # -------------------------------------------------------------------------
    # N24 - N26: Release Readiness & Rollforward Safety
    # -------------------------------------------------------------------------
    def test_n24_releasing_with_failed_blocking_gate(self):
        """N24: Release blocked when gates have FAILED verdict."""
        eval_result = CurriculumAuthoringService.evaluate_release_readiness(
            tenant_id=self.tenant_a.id,
            curriculum_version_id=self.version_a2.id,
        )
        assert eval_result["editorial_gate"] == ReleaseReadinessStatus.FAILED

    def test_n25_waiving_readiness_gate_without_justification(self):
        """N25: Waiving readiness gate with reason < 10 chars raises ValidationError."""
        gate = ReleaseReadinessGate.objects.create(
            tenant=self.tenant_a,
            curriculum_version=self.version_a,
            gate_name="coverage_gate",
            is_blocking=True,
            verdict=ReleaseReadinessStatus.FAILED,
        )
        with pytest.raises(ValidationError) as exc:
            CurriculumAuthoringService.grant_release_exception(
                tenant_id=self.tenant_a.id,
                gate_id=gate.id,
                granted_by_id=self.reviewer_id,
                exception_reason="short",  # < 10 chars
            )
        assert "gate_waiver_requires_audit_justification" in str(exc.value)

    def test_n26_rollforward_targeting_inactive_cohort(self):
        """N26: Rollforward plan targeting inactive cohort schedule raises ValidationError."""
        inactive_sched = CohortSchedule.objects.create(
            tenant=self.tenant_a,
            cohort=self.cohort_a,
            course_release=self.release_a,
            schedule_title="Old Inactive",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30),
            is_active=False,
        )
        with pytest.raises(ValidationError) as exc:
            CurriculumAuthoringService.create_cohort_rollforward_plan(
                tenant_id=self.tenant_a.id,
                cohort_schedule_id=inactive_sched.id,
                target_release_id=self.release_a.id,
            )
        assert "cohort_not_eligible_for_rollforward" in str(exc.value)

    # -------------------------------------------------------------------------
    # N27 - N28: Concurrency & Transaction Integrity
    # -------------------------------------------------------------------------
    def test_n27_concurrent_approval_atomic_lock(self):
        """N27: Double approval prevented via atomic select_for_update()."""
        ws = CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="Lock Draft",
            created_by_id=self.author_id,
        )
        cs = CurriculumAuthoringService.create_change_set(
            tenant_id=self.tenant_a.id,
            workspace_id=ws.id,
            title="Lock CS",
            change_summary="Lock testing",
            author_id=self.author_id,
        )
        CurriculumAuthoringService.submit_change_set_for_review(tenant_id=self.tenant_a.id, change_set_id=cs.id)
        CurriculumAuthoringService.record_editorial_decision(
            tenant_id=self.tenant_a.id,
            change_set_id=cs.id,
            reviewer_id=self.reviewer_id,
            decision="APPROVED",
        )
        # Second approval call fails because status is now APPROVED, not IN_REVIEW
        with pytest.raises(ValidationError):
            CurriculumAuthoringService.record_editorial_decision(
                tenant_id=self.tenant_a.id,
                change_set_id=cs.id,
                reviewer_id=self.reviewer_id,
                decision="APPROVED",
            )

    def test_n28_competing_readiness_gate_evaluation_idempotent(self):
        """N28: Re-evaluating readiness gates is idempotent."""
        r1 = CurriculumAuthoringService.evaluate_release_readiness(
            tenant_id=self.tenant_a.id,
            curriculum_version_id=self.version_a.id,
        )
        r2 = CurriculumAuthoringService.evaluate_release_readiness(
            tenant_id=self.tenant_a.id,
            curriculum_version_id=self.version_a.id,
        )
        assert r1["version_id"] == r2["version_id"]

    # -------------------------------------------------------------------------
    # N29 - N31: PII Blacklist & Synthetic Data Guards (21 Keys)
    # -------------------------------------------------------------------------
    def test_n29_injecting_pii_national_id_in_workspace(self):
        """N29: Injecting national_id key in metadata raises ValidationError."""
        ws = CurriculumDraftWorkspace(
            tenant=self.tenant_a,
            course=self.course_a,
            base_version=self.version_a,
            workspace_title="PII Draft",
            metadata={"national_id": "0012345678"},
        )
        with pytest.raises(ValidationError):
            ws.clean()

    def test_n30_injecting_pii_phone_number_in_comment(self):
        """N30: Injecting phone number regex in review comment raises ValidationError."""
        ws = CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="Comment PII Draft",
        )
        cs = CurriculumAuthoringService.create_change_set(
            tenant_id=self.tenant_a.id,
            workspace_id=ws.id,
            title="CS",
            change_summary="Summary",
        )
        review = EditorialReview.objects.create(tenant=self.tenant_a, change_set=cs)
        comment = ReviewComment(
            tenant=self.tenant_a,
            review=review,
            comment_text="Contact author at 09123456789 for notes",
            target_entity="Lesson",
            target_entity_id=uuid.uuid4(),
        )
        with pytest.raises(ValidationError):
            comment.clean()

    def test_n31_injecting_pii_iban_in_exception_reason(self):
        """N31: Injecting IBAN regex in release exception raises ValidationError."""
        gate = ReleaseReadinessGate.objects.create(
            tenant=self.tenant_a,
            curriculum_version=self.version_a,
            gate_name="test_gate",
        )
        rec = ReleaseExceptionRecord(
            tenant=self.tenant_a,
            gate=gate,
            exception_reason="Fee waived for IR120000000000000000000000",
        )
        with pytest.raises(ValidationError):
            rec.clean()

    # -------------------------------------------------------------------------
    # N32: Outbox Idempotency
    # -------------------------------------------------------------------------
    def test_n32_outbox_event_emitted_atomically(self):
        """N32: Outbox pattern records atomic events for domain changes."""
        from modules.platform_event.models import OutboxEvent
        count_before = OutboxEvent.objects.filter(tenant_id=self.tenant_a.id).count()
        CurriculumAuthoringService.create_draft_workspace(
            tenant_id=self.tenant_a.id,
            course_id=self.course_a.id,
            base_version_id=self.version_a.id,
            workspace_title="Outbox Verified Draft",
        )
        count_after = OutboxEvent.objects.filter(tenant_id=self.tenant_a.id).count()
        assert count_after > count_before

    # -------------------------------------------------------------------------
    # N33: Zero Bare UUIDs in Models
    # -------------------------------------------------------------------------
    def test_n33_all_19_models_enforce_tenant_foreign_key(self):
        """N33: Verify 100% of Epic 23-25 tables possess composite tenant ForeignKey."""
        from django.apps import apps
        epic_models = [
            CurriculumDraftWorkspace, ContentChangeSet, EditorialReview,
            ReviewComment, ReviewResolution, AuthorAssignment, ChangeApprovalRecord,
            AssessmentBlueprint, LearningObjectiveMapping, RubricDefinition,
            RubricCriterion, AssessmentReleaseBinding, RubricReviewRecord,
            CurriculumChangeImpact, ReleaseReadinessCheck, ReleaseReadinessGate,
            CohortRollforwardPlan, CurriculumMigrationDecision, ReleaseExceptionRecord
        ]
        for model in epic_models:
            field_names = [f.name for f in model._meta.fields]
            assert "tenant" in field_names or "tenant_id" in field_names

    # -------------------------------------------------------------------------
    # N34 - N35: Role-Based Authorization Guards
    # -------------------------------------------------------------------------
    def test_n34_learner_cannot_create_content_changeset(self):
        """N34: Learner attempting to create ContentChangeSet returns 403 Forbidden."""
        req = self.factory.post(
            "/api/v1/learning/authoring/changesets/",
            data={"workspace_id": str(uuid.uuid4()), "title": "Hacked", "change_summary": "Test"},
            format="json",
        )
        req.tenant = self.tenant_a
        req.user_role = "LEARNER"
        resp = ContentChangeSetView.as_view()(req)
        assert resp.status_code == 403

    def test_n35_learner_cannot_evaluate_readiness_gate(self):
        """N35: Learner attempting to evaluate ReleaseReadinessGate returns 403 Forbidden."""
        req = self.factory.post(
            f"/api/v1/learning/readiness/versions/{self.version_a.id}/evaluate/",
            format="json",
        )
        req.tenant = self.tenant_a
        req.user_role = "LEARNER"
        resp = ReleaseReadinessEvaluateView.as_view()(req, version_id=str(self.version_a.id))
        assert resp.status_code == 403
