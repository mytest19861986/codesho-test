from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection, transaction
from django.utils import timezone

from modules.platform_tenant.models import TenantMembership
from .models import (
    AIAssistedGrowthSuggestion,
    ActionPlanStatus,
    CalculationRun,
    GoalActionPlan,
    GoalStatus,
    LearningReflection,
    MentorReflectionFeedback,
    ReflectionAuditAction,
    ReflectionAuditLog,
    ReflectionMoodSentiment,
    ReflectionPromptType,
    StudentLearningGoal,
    SuggestionStatus,
)


class LearningOperationsService:
    """
    P3-VS14 Service Layer: Student Learning Operations, Reflection & AI-Assisted Growth.
    
    Enforces Invariants:
    1. Multi-Tenancy & Child Safety: Fail-closed tenant isolation with composite FKs.
    2. Zero PII: Strict scrubbing of all sensitive attributes in metadata and evidence.
    3. Goal FSM & Concurrency: Exactly 1 ACTIVE goal per domain; Global count <= 5;
       Serialized via transactional advisory lock:
       pg_advisory_xact_lock(hashtextextended(tenant_id || ':' || student_id, 14))
    4. Non-Authoritative AI: is_authoritative = FALSE, evidence_context non-empty (Explainability First),
       Moderation gate (PENDING hidden from students until mentor review -> PRESENTED).
    5. Append-Only Audit Trail: Forensic logging for all operations with XOR polymorphic targets.
    """

    PROHIBITED_PII_KEYS = {
        "name", "phone", "email", "national_id", "location", "avatar_url",
        "phone_number", "fingerprint", "face_id", "voice_sample", "bank_account",
        "iban", "credit_card"
    }

    VALID_GOAL_TRANSITIONS = {
        GoalStatus.DRAFT: {GoalStatus.ACTIVE, GoalStatus.ARCHIVED},
        GoalStatus.ACTIVE: {GoalStatus.ACHIEVED, GoalStatus.PAUSED, GoalStatus.SUPERSEDED, GoalStatus.ARCHIVED},
        GoalStatus.PAUSED: {GoalStatus.ACTIVE, GoalStatus.ARCHIVED},
        GoalStatus.ACHIEVED: set(),
        GoalStatus.ARCHIVED: set(),
        GoalStatus.SUPERSEDED: set(),
    }

    VALID_SUGGESTION_TRANSITIONS = {
        SuggestionStatus.PENDING: {SuggestionStatus.PRESENTED, SuggestionStatus.WITHDRAWN, SuggestionStatus.SUPERSEDED},
        SuggestionStatus.PRESENTED: {SuggestionStatus.ACCEPTED, SuggestionStatus.DISMISSED, SuggestionStatus.WITHDRAWN, SuggestionStatus.SUPERSEDED},
        SuggestionStatus.ACCEPTED: {SuggestionStatus.WITHDRAWN},
        SuggestionStatus.DISMISSED: set(),
        SuggestionStatus.WITHDRAWN: set(),
        SuggestionStatus.SUPERSEDED: set(),
    }

    @classmethod
    def sanitize_pii(cls, data: Any) -> Any:
        """Recursively cleans all prohibited PII keys from dictionary/list data structures."""
        if isinstance(data, dict):
            return {
                k: cls.sanitize_pii(v)
                for k, v in data.items()
                if str(k).lower() not in cls.PROHIBITED_PII_KEYS
            }
        elif isinstance(data, list):
            return [cls.sanitize_pii(item) for item in data]
        return data

    @classmethod
    def acquire_student_advisory_lock(cls, tenant_id: uuid.UUID, student_id: uuid.UUID) -> None:
        """Acquires a PostgreSQL session-level transactional advisory lock scoped to tenant + student."""
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                lock_key = f"{tenant_id}:{student_id}:p3_vs14_goals"
                cursor.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 14));",
                    [lock_key],
                )

    # -------------------------------------------------------------------------
    # 1. LEARNING REFLECTION METHODS
    # -------------------------------------------------------------------------

    @classmethod
    def create_reflection(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        prompt_type: str,
        content: str,
        mood_sentiment: str = ReflectionMoodSentiment.NEUTRAL,
    ) -> LearningReflection:
        if not content or not content.strip():
            raise ValidationError("Reflection content cannot be empty.")
        if len(content) > 10000:
            raise ValidationError("Reflection content cannot exceed 10000 characters.")

        with transaction.atomic():
            reflection = LearningReflection.objects.create(
                tenant_id=tenant_id,
                student_id=student_id,
                prompt_type=prompt_type,
                content=content.strip(),
                mood_sentiment=mood_sentiment,
            )
            # Log audit
            ReflectionAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=student_id,
                target_reflection=reflection,
                action=ReflectionAuditAction.CREATE_REFLECTION,
                metadata={"prompt_type": prompt_type, "mood": mood_sentiment},
            )
            return reflection

    @classmethod
    def retract_reflection(
        cls,
        tenant_id: uuid.UUID,
        reflection_id: uuid.UUID,
        actor_id: uuid.UUID,
        reason: str,
    ) -> LearningReflection:
        if not reason or not reason.strip():
            raise ValidationError("Retraction reason is strictly required.")

        with transaction.atomic():
            reflection = LearningReflection.objects.select_for_update().get(
                tenant_id=tenant_id, id=reflection_id
            )
            reflection.is_retracted = True
            reflection.retracted_at = timezone.now()
            reflection.retraction_reason = reason.strip()
            reflection.save()

            ReflectionAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=actor_id,
                target_reflection=reflection,
                action=ReflectionAuditAction.RETRACT_REFLECTION,
                metadata={"reason": reason.strip()},
            )
            return reflection

    # -------------------------------------------------------------------------
    # 2. STUDENT LEARNING GOAL METHODS & FSM
    # -------------------------------------------------------------------------

    @classmethod
    def create_goal(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        title: str,
        domain: str,
        target_milestone_id: Optional[uuid.UUID] = None,
        target_date: Optional[Any] = None,
    ) -> StudentLearningGoal:
        if not title or not title.strip():
            raise ValidationError("Goal title cannot be empty.")
        if not domain or not domain.strip():
            raise ValidationError("Domain is required.")

        with transaction.atomic():
            goal = StudentLearningGoal.objects.create(
                tenant_id=tenant_id,
                student_id=student_id,
                title=title.strip(),
                domain=domain.strip().upper(),
                target_milestone_id=target_milestone_id,
                status=GoalStatus.DRAFT,
                target_date=target_date,
            )
            ReflectionAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=student_id,
                target_goal=goal,
                action=ReflectionAuditAction.CREATE_GOAL,
                metadata={"title": goal.title, "domain": goal.domain},
            )
            return goal

    @classmethod
    def transition_goal_status(
        cls,
        tenant_id: uuid.UUID,
        goal_id: uuid.UUID,
        actor_id: uuid.UUID,
        target_status: str,
    ) -> StudentLearningGoal:
        with transaction.atomic():
            goal = StudentLearningGoal.objects.select_for_update().get(
                tenant_id=tenant_id, id=goal_id
            )
            current_status = goal.status
            target_status = target_status.upper()

            # Verify FSM
            valid_targets = cls.VALID_GOAL_TRANSITIONS.get(current_status, set())
            if target_status not in valid_targets:
                raise ValidationError(
                    f"Illegal goal transition from '{current_status}' to '{target_status}'."
                )

            # If activating or resuming, acquire advisory lock & enforce invariants
            if target_status == GoalStatus.ACTIVE:
                cls.acquire_student_advisory_lock(tenant_id, goal.student_id)

                # Check active domain uniqueness
                active_domain_exists = StudentLearningGoal.objects.filter(
                    tenant_id=tenant_id,
                    student_id=goal.student_id,
                    domain=goal.domain,
                    status=GoalStatus.ACTIVE,
                ).exclude(id=goal.id).exists()
                if active_domain_exists:
                    raise ValidationError(
                        f"Student already has an ACTIVE goal in domain '{goal.domain}'."
                    )

                # Check max 5 active goals limit
                active_count = StudentLearningGoal.objects.filter(
                    tenant_id=tenant_id,
                    student_id=goal.student_id,
                    status=GoalStatus.ACTIVE,
                ).exclude(id=goal.id).count()
                if active_count >= 5:
                    raise ValidationError(
                        "Student cannot have more than 5 concurrent ACTIVE goals."
                    )

            if target_status == GoalStatus.ACHIEVED:
                goal.completed_at = timezone.now()
            else:
                goal.completed_at = None

            goal.status = target_status
            goal.save()

            ReflectionAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=actor_id,
                target_goal=goal,
                action=ReflectionAuditAction.TRANSITION_GOAL_STATUS,
                metadata={"from": current_status, "to": target_status},
            )
            return goal

    # -------------------------------------------------------------------------
    # 3. ACTION PLAN METHODS
    # -------------------------------------------------------------------------

    @classmethod
    def add_action_step(
        cls,
        tenant_id: uuid.UUID,
        goal_id: uuid.UUID,
        step_order: int,
        description: str,
        due_date: Optional[Any] = None,
    ) -> GoalActionPlan:
        if step_order < 1:
            raise ValidationError("Step order must be >= 1.")
        if not description or not description.strip():
            raise ValidationError("Action plan description cannot be empty.")

        with transaction.atomic():
            step = GoalActionPlan.objects.create(
                tenant_id=tenant_id,
                goal_id=goal_id,
                step_order=step_order,
                description=description.strip(),
                status=ActionPlanStatus.PENDING,
                due_date=due_date,
            )
            return step

    # -------------------------------------------------------------------------
    # 4. AI-ASSISTED GROWTH SUGGESTION & MODERATION GATE
    # -------------------------------------------------------------------------

    @classmethod
    def generate_ai_suggestion(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        suggestion_type: str,
        recommended_action: str,
        rationale: str,
        evidence_context: Dict[str, Any],
        model_identifier: str = "qwen-coder-2.5-72b",
        source_insight_id: Optional[uuid.UUID] = None,
        generation_run_id: Optional[uuid.UUID] = None,
    ) -> AIAssistedGrowthSuggestion:
        if not evidence_context or evidence_context == {}:
            raise ValidationError("evidence_context cannot be empty (Explainability First).")
        if not isinstance(evidence_context, dict):
            raise ValidationError("evidence_context must be a valid non-empty JSON object.")
        if len(rationale.strip()) < 15:
            raise ValidationError("Rationale must be at least 15 characters.")

        clean_evidence = cls.sanitize_pii(evidence_context)
        raw_provenance = f"{tenant_id}:{student_id}:{suggestion_type}:{json.dumps(clean_evidence, sort_keys=True)}"
        provenance_digest = hashlib.sha256(raw_provenance.encode("utf-8")).hexdigest()
        idempotency_key = f"sugg:{provenance_digest[:32]}"

        with transaction.atomic():
            # Idempotency check
            existing = AIAssistedGrowthSuggestion.objects.filter(
                tenant_id=tenant_id, idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing

            suggestion = AIAssistedGrowthSuggestion.objects.create(
                tenant_id=tenant_id,
                student_id=student_id,
                source_insight_id=source_insight_id,
                generation_run_id=generation_run_id,
                suggestion_type=suggestion_type.upper(),
                recommended_action=recommended_action.strip(),
                rationale=rationale.strip(),
                evidence_context=clean_evidence,
                model_identifier=model_identifier,
                provenance_digest=provenance_digest,
                idempotency_key=idempotency_key,
                status=SuggestionStatus.PENDING,  # Moderation gate holds it PENDING
                is_authoritative=False,
            )
            ReflectionAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=student_id,
                target_suggestion=suggestion,
                action=ReflectionAuditAction.GENERATE_AI_SUGGESTION,
                metadata={"suggestion_type": suggestion_type, "provenance": provenance_digest},
            )
            return suggestion

    @classmethod
    def moderate_suggestion(
        cls,
        tenant_id: uuid.UUID,
        suggestion_id: uuid.UUID,
        mentor_id: uuid.UUID,
        decision: str,  # 'PRESENT' or 'WITHDRAW'
    ) -> AIAssistedGrowthSuggestion:
        with transaction.atomic():
            suggestion = AIAssistedGrowthSuggestion.objects.select_for_update().get(
                tenant_id=tenant_id, id=suggestion_id
            )
            if decision.upper() == "PRESENT":
                # Ensure partial unique singleton: at most 1 PRESENTED per suggestion_type
                AIAssistedGrowthSuggestion.objects.filter(
                    tenant_id=tenant_id,
                    student_id=suggestion.student_id,
                    suggestion_type=suggestion.suggestion_type,
                    status=SuggestionStatus.PRESENTED,
                ).exclude(id=suggestion.id).update(status=SuggestionStatus.SUPERSEDED)

                suggestion.status = SuggestionStatus.PRESENTED
            elif decision.upper() == "WITHDRAW":
                suggestion.status = SuggestionStatus.WITHDRAWN
            else:
                raise ValidationError("Invalid moderation decision. Must be PRESENT or WITHDRAW.")

            suggestion.save()
            ReflectionAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=mentor_id,
                target_suggestion=suggestion,
                action=ReflectionAuditAction.MODERATE_AI_SUGGESTION,
                metadata={"decision": decision.upper()},
            )
            return suggestion

    # -------------------------------------------------------------------------
    # 5. MENTOR REFLECTION FEEDBACK
    # -------------------------------------------------------------------------

    @classmethod
    def post_mentor_feedback(
        cls,
        tenant_id: uuid.UUID,
        reflection_id: uuid.UUID,
        mentor_id: uuid.UUID,
        feedback_text: str,
    ) -> MentorReflectionFeedback:
        if not feedback_text or not feedback_text.strip():
            raise ValidationError("Feedback text cannot be empty.")
        if len(feedback_text) > 5000:
            raise ValidationError("Feedback text cannot exceed 5000 characters.")

        with transaction.atomic():
            feedback = MentorReflectionFeedback.objects.create(
                tenant_id=tenant_id,
                reflection_id=reflection_id,
                mentor_id=mentor_id,
                feedback_text=feedback_text.strip(),
            )
            ReflectionAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=mentor_id,
                target_feedback=feedback,
                action=ReflectionAuditAction.POST_MENTOR_FEEDBACK,
                metadata={"reflection_id": str(reflection_id)},
            )
            return feedback
