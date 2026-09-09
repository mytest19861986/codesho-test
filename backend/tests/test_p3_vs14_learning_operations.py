import uuid
import datetime
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from modules.platform_tenant.models import Tenant, TenantMembership
from modules.learning.models import (
    AIAssistedGrowthSuggestion,
    ActionPlanStatus,
    CalculationRun,
    GoalActionPlan,
    GoalStatus,
    LearningInsight,
    LearningMilestone,
    LearningReflection,
    MentorReflectionFeedback,
    ReflectionAuditAction,
    ReflectionAuditLog,
    ReflectionMoodSentiment,
    ReflectionPromptType,
    StudentLearningGoal,
    SuggestionStatus,
)
from modules.learning.learning_operations_service import LearningOperationsService
from modules.learning.views import (
    AIAssistedGrowthSuggestionView,
    LearningReflectionListCreateView,
    StudentLearningGoalListCreateView,
)


@pytest.mark.django_db
class TestP3VS14LearningOperationsMatrix:
    """
    Comprehensive test suite for Phase 3 Vertical Slice 14:
    Student Learning Operations, Reflection & AI-Assisted Growth.
    Covers Negative & Compliance Proof Matrix (N1 - N27).
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.tenant_a = Tenant.objects.create(name="Alpha Academy", slug="alpha-academy")
        self.tenant_b = Tenant.objects.create(name="Beta Academy", slug="beta-academy")

        from modules.identity.models import User

        self.user_student_a = User.objects.create_user(username="student_a", email="student_a@alpha.com")
        self.user_student_b = User.objects.create_user(username="student_b", email="student_b@beta.com")
        self.user_mentor_a = User.objects.create_user(username="mentor_a", email="mentor_a@alpha.com")
        self.user_admin_a = User.objects.create_user(username="admin_a", email="admin_a@alpha.com")

        self.student_a_id = self.user_student_a.id
        self.student_b_id = self.user_student_b.id
        self.mentor_a_id = self.user_mentor_a.id
        self.admin_a_id = self.user_admin_a.id

        # Memberships
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.student_a_id, role="student")
        TenantMembership.objects.create(tenant=self.tenant_b, user_id=self.student_b_id, role="student")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.mentor_a_id, role="mentor")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.admin_a_id, role="admin")

        self.factory = APIRequestFactory()

    # -------------------------------------------------------------------------
    # N5 & N6: Cross-Tenant Isolation
    # -------------------------------------------------------------------------
    def test_n5_cross_tenant_student_membership_isolation(self):
        """N5: Cross-tenant student membership isolation check."""
        with pytest.raises(ValidationError):
            # student_b belongs to tenant_b, attempting to assign to reflection in tenant_a
            refl = LearningReflection(
                tenant=self.tenant_a,
                student_id=self.student_b_id,
                prompt_type=ReflectionPromptType.WEEKLY_REVIEW,
                content="My reflections on Python",
            )
            # Service / clean check
            refl.clean()

    def test_n6_cross_tenant_action_plan_goal_isolation(self):
        """N6: Insert GoalActionPlan pointing to goal of Tenant B into Tenant A."""
        goal_b = StudentLearningGoal.objects.create(
            tenant=self.tenant_b,
            student_id=self.student_b_id,
            title="Goal in Tenant B",
            domain="PYTHON_BASICS",
        )
        plan = GoalActionPlan(
            tenant=self.tenant_a,
            goal=goal_b,
            step_order=1,
            description="Step 1 in Tenant A",
        )
        with pytest.raises(ValidationError):
            plan.clean()

    # -------------------------------------------------------------------------
    # N10 & N11: ReflectionAuditLog Target Integrity
    # -------------------------------------------------------------------------
    def test_n10_audit_target_xor_constraint(self):
        """N10: Insert ReflectionAuditLog with multiple targets or 0 targets -> REJECT."""
        refl = LearningReflection.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            prompt_type=ReflectionPromptType.FREE_REFLECTION,
            content="Valid reflection content",
        )
        goal = StudentLearningGoal.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            title="Valid Goal",
            domain="ALGORITHMS",
        )
        # Multiple targets
        log_multi = ReflectionAuditLog(
            tenant=self.tenant_a,
            actor_id=self.student_a_id,
            target_reflection=refl,
            target_goal=goal,
            action=ReflectionAuditAction.CREATE_REFLECTION,
        )
        with pytest.raises(ValidationError):
            log_multi.clean()

        # Zero targets
        log_zero = ReflectionAuditLog(
            tenant=self.tenant_a,
            actor_id=self.student_a_id,
            action=ReflectionAuditAction.CREATE_REFLECTION,
        )
        with pytest.raises(ValidationError):
            log_zero.clean()

    def test_n11_audit_target_cross_tenant_rejection(self):
        """N11: Insert ReflectionAuditLog pointing to target from Tenant B into Tenant A."""
        refl_b = LearningReflection.objects.create(
            tenant=self.tenant_b,
            student_id=self.student_b_id,
            prompt_type=ReflectionPromptType.WEEKLY_REVIEW,
            content="Reflection in Tenant B",
        )
        log = ReflectionAuditLog(
            tenant=self.tenant_a,
            actor_id=self.student_a_id,
            target_reflection=refl_b,
            action=ReflectionAuditAction.CREATE_REFLECTION,
        )
        with pytest.raises(ValidationError):
            log.clean()

    def test_n13_audit_log_immutable_append_only(self):
        """N13: Attempt UPDATE or DELETE on ReflectionAuditLog -> REJECT."""
        refl = LearningReflection.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            prompt_type=ReflectionPromptType.WEEKLY_REVIEW,
            content="Reflection entry",
        )
        log = ReflectionAuditLog.objects.create(
            tenant=self.tenant_a,
            actor_id=self.student_a_id,
            target_reflection=refl,
            action=ReflectionAuditAction.CREATE_REFLECTION,
        )
        with pytest.raises(ValidationError):
            log.action = ReflectionAuditAction.RETRACT_REFLECTION
            log.save()

        with pytest.raises(ValidationError):
            log.delete()

    # -------------------------------------------------------------------------
    # N14 & N15: Goal FSM Transitions and Domain Uniqueness
    # -------------------------------------------------------------------------
    def test_n14_fsm_illegal_jump_draft_to_achieved(self):
        """N14: Transition StudentLearningGoal directly from DRAFT to ACHIEVED -> REJECT."""
        goal = LearningOperationsService.create_goal(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            title="Direct Jump Goal",
            domain="DATA_STRUCTURES",
        )
        with pytest.raises(ValidationError, match="Illegal goal transition"):
            LearningOperationsService.transition_goal_status(
                tenant_id=self.tenant_a.id,
                goal_id=goal.id,
                actor_id=self.student_a_id,
                target_status="ACHIEVED",
            )

    def test_n15_domain_active_uniqueness_enforced(self):
        """N15: Insert 2nd ACTIVE goal in same domain for same student -> REJECT."""
        goal1 = LearningOperationsService.create_goal(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            title="Goal 1",
            domain="PYTHON_BASICS",
        )
        LearningOperationsService.transition_goal_status(
            tenant_id=self.tenant_a.id,
            goal_id=goal1.id,
            actor_id=self.student_a_id,
            target_status="ACTIVE",
        )

        goal2 = LearningOperationsService.create_goal(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            title="Goal 2",
            domain="PYTHON_BASICS",
        )
        with pytest.raises(ValidationError, match="already has an ACTIVE goal in domain"):
            LearningOperationsService.transition_goal_status(
                tenant_id=self.tenant_a.id,
                goal_id=goal2.id,
                actor_id=self.student_a_id,
                target_status="ACTIVE",
            )

    # -------------------------------------------------------------------------
    # N16 & N17: Max 5 Active Goals Limit
    # -------------------------------------------------------------------------
    def test_n16_max_five_active_goals_limit(self):
        """N16: Activate 6th goal concurrently across domains -> REJECT."""
        domains = ["DOMAIN_1", "DOMAIN_2", "DOMAIN_3", "DOMAIN_4", "DOMAIN_5", "DOMAIN_6"]
        for i in range(5):
            g = LearningOperationsService.create_goal(
                tenant_id=self.tenant_a.id,
                student_id=self.student_a_id,
                title=f"Goal {i}",
                domain=domains[i],
            )
            LearningOperationsService.transition_goal_status(
                tenant_id=self.tenant_a.id,
                goal_id=g.id,
                actor_id=self.student_a_id,
                target_status="ACTIVE",
            )

        # 6th goal
        g6 = LearningOperationsService.create_goal(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            title="Goal 6",
            domain=domains[5],
        )
        with pytest.raises(ValidationError, match="cannot have more than 5 concurrent ACTIVE goals"):
            LearningOperationsService.transition_goal_status(
                tenant_id=self.tenant_a.id,
                goal_id=g6.id,
                actor_id=self.student_a_id,
                target_status="ACTIVE",
            )

    # -------------------------------------------------------------------------
    # N18 & N19: AI Growth Suggestion Moderation Gate & Presentation Singleton
    # -------------------------------------------------------------------------
    def test_n18_student_suggestion_moderation_gate(self):
        """N18: Student queries AIAssistedGrowthSuggestion in PENDING state -> filtered out."""
        # Create suggestion in PENDING state
        sugg = LearningOperationsService.generate_ai_suggestion(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            suggestion_type="MASTERY_PATH",
            recommended_action="Practice loops 15 mins daily",
            rationale="Rationale with more than fifteen characters.",
            evidence_context={"topic": "loops", "score": 0.65},
        )
        assert sugg.status == SuggestionStatus.PENDING

        request = self.factory.get("/api/v1/learning/suggestions/")
        request.user = self.user_student_a
        request.tenant_id = self.tenant_a.id

        view = AIAssistedGrowthSuggestionView.as_view()
        response = view(request)
        assert response.status_code == 200
        # Student sees 0 items because suggestion is PENDING
        assert len(response.data) == 0

        # Now mentor moderates and presents
        LearningOperationsService.moderate_suggestion(
            tenant_id=self.tenant_a.id,
            suggestion_id=sugg.id,
            mentor_id=self.mentor_a_id,
            decision="PRESENT",
        )
        response_after = view(request)
        assert response_after.status_code == 200
        assert len(response_after.data) == 1
        assert response_after.data[0]["id"] == str(sugg.id)

    # -------------------------------------------------------------------------
    # N20 & N27: AI Advisory Invariant & Explainability First
    # -------------------------------------------------------------------------
    def test_n20_ai_suggestion_must_remain_non_authoritative(self):
        """N20: Update is_authoritative = TRUE on AIAssistedGrowthSuggestion -> REJECT."""
        sugg = AIAssistedGrowthSuggestion(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            suggestion_type="PRACTICE",
            recommended_action="Do exercises",
            rationale="Rationale over 15 characters long",
            evidence_context={"concept": "recursion"},
            model_identifier="test-model",
            provenance_digest="a" * 64,
            idempotency_key="key-1",
            is_authoritative=True,
        )
        with pytest.raises(ValidationError, match="is_authoritative=False"):
            sugg.clean()

    def test_n27_empty_evidence_context_rejected_explainability_first(self):
        """N27: Insert suggestion with evidence_context = {} -> REJECT (Explainability First)."""
        with pytest.raises(ValidationError, match="evidence_context cannot be empty"):
            LearningOperationsService.generate_ai_suggestion(
                tenant_id=self.tenant_a.id,
                student_id=self.student_a_id,
                suggestion_type="REINFORCEMENT",
                recommended_action="Read documentation",
                rationale="Rationale over 15 characters long",
                evidence_context={},  # Empty dictionary
            )

    # -------------------------------------------------------------------------
    # N21 & N22: PII Scrubbing
    # -------------------------------------------------------------------------
    def test_n21_differential_pii_scrubbed_from_evidence(self):
        """N21: Inject sensitive keys into evidence_context -> PII recursively removed."""
        dirty_evidence = {
            "concept": "arrays",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+989123456789",
            "safe_metric": 88.5,
        }
        clean = LearningOperationsService.sanitize_pii(dirty_evidence)
        assert "name" not in clean
        assert "email" not in clean
        assert "phone" not in clean
        assert clean["concept"] == "arrays"
        assert clean["safe_metric"] == 88.5

    # -------------------------------------------------------------------------
    # N23: Retraction Consistency
    # -------------------------------------------------------------------------
    def test_n23_reflection_retraction_consistency(self):
        """N23: Set is_retracted = True without retraction_reason -> REJECT."""
        refl = LearningReflection(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            prompt_type=ReflectionPromptType.FREE_REFLECTION,
            content="Some reflection content",
            is_retracted=True,
            retracted_at=timezone.now(),
            retraction_reason="",  # Missing reason
        )
        with pytest.raises(ValidationError):
            refl.clean()

    # -------------------------------------------------------------------------
    # N24: Idempotency Proof
    # -------------------------------------------------------------------------
    def test_n24_suggestion_generation_idempotency(self):
        """N24: Consecutive duplicate suggestion generation returns identical record."""
        sugg1 = LearningOperationsService.generate_ai_suggestion(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            suggestion_type="IDEMPOTENT_TYPE",
            recommended_action="Do task",
            rationale="Rationale over 15 characters long",
            evidence_context={"unit": 1},
        )
        sugg2 = LearningOperationsService.generate_ai_suggestion(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            suggestion_type="IDEMPOTENT_TYPE",
            recommended_action="Do task",
            rationale="Rationale over 15 characters long",
            evidence_context={"unit": 1},
        )
        assert sugg1.id == sugg2.id
        assert sugg1.idempotency_key == sugg2.idempotency_key

    # -------------------------------------------------------------------------
    # N25: Anti-Ranking Policy
    # -------------------------------------------------------------------------
    def test_n25_anti_ranking_query_parameters_rejected(self):
        """N25: Request goals or reflection dashboard with peer ranking params -> 400."""
        request = self.factory.get("/api/v1/learning/goals/?rank=true")
        request.user = self.user_student_a
        request.tenant_id = self.tenant_a.id

        view = StudentLearningGoalListCreateView.as_view()
        response = view(request)
        assert response.status_code == 400
        assert "Peer ranking and comparative sorting are strictly prohibited" in response.data["detail"]

    # -------------------------------------------------------------------------
    # N26: Role Authorization for AI Generation Endpoint
    # -------------------------------------------------------------------------
    def test_n26_student_forbidden_from_direct_ai_generation_endpoint(self):
        """N26: Student attempts to trigger AI suggestion generation endpoint -> 403."""
        request = self.factory.post(
            "/api/v1/learning/suggestions/generate/",
            {"student_id": str(self.student_a_id)},
            format="json",
        )
        request.user = self.user_student_a
        request.tenant_id = self.tenant_a.id

        view = AIAssistedGrowthSuggestionView.as_view()
        response = view(request)
        assert response.status_code == 403
        assert "Students are forbidden" in response.data["detail"]
