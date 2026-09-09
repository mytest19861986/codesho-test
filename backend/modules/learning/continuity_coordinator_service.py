from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection, transaction
from django.utils import timezone

from modules.platform_tenant.models import TenantMembership
from .models import (
    LearningMilestone,
    LearningReflection,
    LearningInsight,
    LearningStudentSuccessPlan,
    StudentLearningGoal,
    SuccessActionStep,
    SuccessActionStepStatus,
    SuccessAuditAction,
    SuccessAuditLog,
    SuccessPlanStatus,
    SuccessPlanTargetPeriod,
    SuccessTimelineEvent,
    SuccessTimelineEventType,
)


class ContinuityCoordinatorService:
    """
    P3-VS15 Service Layer: Learning Continuity & Student Success Planning.
    
    Invariants & Architectural Rules:
    1. Tenant Isolation & Fail-Closed Session Protocol:
       All DB operations run inside transaction.atomic() with SET LOCAL "app.current_tenant" = %s.
    2. Active Singleton Plan:
       Exactly 1 ACTIVE LearningStudentSuccessPlan per student per tenant.
       Serialized via transactional advisory lock:
       pg_advisory_xact_lock(hashtextextended(tenant_id || ':' || student_id, 15))
    3. FSM Validations:
       Strict state transition guards for SuccessPlan and SuccessActionStep.
    4. Non-Authoritative System/AI Boundary:
       System/agents can suggest or dispatch formative steps but can NEVER issue
       authoritative decisions (is_authoritative = False strictly enforced).
    5. 5-Way XOR Continuity Trail:
       Timeline events link exactly one verified target (Goal, Insight, Reflection, Action, Milestone).
    6. Append-Only Discipline & Idempotency:
       Timeline events cannot be edited or deleted. Amendments create compensatory
       TIMELINE_EVENT_AMENDED events referencing replaces_event_id. Duplicate submits
       with client_mutation_id are safely de-duplicated.
    7. Zero PII:
       13-key exclusion list scrubbed from all JSONB metadata and notes/detail regex validation.
    8. Anti-Ranking & Privacy:
       No peer comparison, ranking, or leaderboard queries permitted.
    """

    PROHIBITED_PII_KEYS = {
        "name", "phone", "email", "national_id", "location", "avatar_url",
        "phone_number", "fingerprint", "face_id", "voice_sample", "bank_account",
        "iban", "credit_card"
    }

    PII_REGEX = re.compile(
        r"(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)",
        re.IGNORECASE
    )

    VALID_PLAN_TRANSITIONS = {
        SuccessPlanStatus.ACTIVE: {SuccessPlanStatus.PAUSED, SuccessPlanStatus.COMPLETED, SuccessPlanStatus.SUPERSEDED, SuccessPlanStatus.ARCHIVED},
        SuccessPlanStatus.PAUSED: {SuccessPlanStatus.ACTIVE, SuccessPlanStatus.SUPERSEDED, SuccessPlanStatus.ARCHIVED},
        SuccessPlanStatus.COMPLETED: {SuccessPlanStatus.ARCHIVED},
        SuccessPlanStatus.SUPERSEDED: set(),
        SuccessPlanStatus.ARCHIVED: set(),
    }

    VALID_STEP_TRANSITIONS = {
        SuccessActionStepStatus.PENDING: {SuccessActionStepStatus.IN_PROGRESS, SuccessActionStepStatus.COMPLETED, SuccessActionStepStatus.SKIPPED, SuccessActionStepStatus.CANCELLED},
        SuccessActionStepStatus.IN_PROGRESS: {SuccessActionStepStatus.COMPLETED, SuccessActionStepStatus.SKIPPED, SuccessActionStepStatus.CANCELLED},
        SuccessActionStepStatus.COMPLETED: set(),
        SuccessActionStepStatus.SKIPPED: set(),
        SuccessActionStepStatus.CANCELLED: set(),
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
    def assert_no_pii_in_text(cls, text: Optional[str], field_name: str = "text") -> None:
        """Raises ValidationError if text contains sensitive PII patterns."""
        if text and cls.PII_REGEX.search(text):
            raise ValidationError(f"{field_name} contains prohibited PII or sensitive data.")

    @classmethod
    def acquire_student_advisory_lock(cls, tenant_id: uuid.UUID, student_id: uuid.UUID) -> None:
        """Acquires a PostgreSQL session-level transactional advisory lock scoped to tenant + student."""
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                lock_key = f"{tenant_id}:{student_id}:p3_vs15_success_plans"
                cursor.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 15));",
                    [lock_key],
                )

    @classmethod
    def establish_tenant_session(cls, tenant_id: uuid.UUID) -> None:
        """Sets the app.current_tenant GUC inside transaction.atomic() before queries."""
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL \"app.current_tenant\" = %s;", [str(tenant_id)])

    @classmethod
    def emit_audit_log(
        cls,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
        action: SuccessAuditAction,
        target_plan: Optional[LearningStudentSuccessPlan] = None,
        target_action_step: Optional[SuccessActionStep] = None,
        target_timeline_event: Optional[SuccessTimelineEvent] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SuccessAuditLog:
        """Emits an append-only audit log with XOR polymorphic target and zero PII."""
        sanitized_meta = cls.sanitize_pii(metadata or {})
        return SuccessAuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            target_plan=target_plan,
            target_action_step=target_action_step,
            target_timeline_event=target_timeline_event,
            metadata=sanitized_meta,
        )

    # -------------------------------------------------------------------------
    # 1. STUDENT SUCCESS PLAN METHODS
    # -------------------------------------------------------------------------

    @classmethod
    def create_success_plan(
        cls,
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        actor_id: uuid.UUID,
        title: str,
        target_period: SuccessPlanTargetPeriod,
        notes: Optional[str] = None,
    ) -> LearningStudentSuccessPlan:
        """
        Creates a new StudentSuccessPlan enforcing the Active Singleton invariant.
        If an existing active plan exists, it must either be paused, completed, or superseded first.
        """
        cls.assert_no_pii_in_text(title, "title")
        cls.assert_no_pii_in_text(notes, "notes")

        with transaction.atomic():
            cls.establish_tenant_session(tenant_id)
            cls.acquire_student_advisory_lock(tenant_id, student_id)

            # Check student membership in tenant
            if not TenantMembership.objects.filter(tenant_id=tenant_id, user_id=student_id).exists():
                raise ValidationError("Student must belong to the specified tenant.")

            # Enforce Active Singleton: No other active plan allowed for this student
            if LearningStudentSuccessPlan.objects.filter(
                tenant_id=tenant_id, student_id=student_id, status=SuccessPlanStatus.ACTIVE
            ).exists():
                raise ValidationError("Student already has an ACTIVE success plan. Complete, pause, or supersede it first.")

            plan = LearningStudentSuccessPlan(
                tenant_id=tenant_id,
                student_id=student_id,
                title=title.strip(),
                target_period=target_period,
                status=SuccessPlanStatus.ACTIVE,
                notes=notes,
            )
            plan.clean()
            plan.save()

            cls.emit_audit_log(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=SuccessAuditAction.CREATE_SUCCESS_PLAN,
                target_plan=plan,
                metadata={"title": plan.title, "target_period": plan.target_period},
            )
            return plan

    @classmethod
    def transition_plan_status(
        cls,
        tenant_id: uuid.UUID,
        plan_id: uuid.UUID,
        actor_id: uuid.UUID,
        new_status: SuccessPlanStatus,
    ) -> LearningStudentSuccessPlan:
        """Transitions StudentSuccessPlan status according to FSM state machine."""
        with transaction.atomic():
            cls.establish_tenant_session(tenant_id)
            plan = LearningStudentSuccessPlan.objects.select_for_update().filter(
                tenant_id=tenant_id, id=plan_id
            ).first()
            if not plan:
                raise ValidationError("Success plan not found in tenant.")

            cls.acquire_student_advisory_lock(tenant_id, plan.student_id)

            if new_status not in cls.VALID_PLAN_TRANSITIONS.get(plan.status, set()):
                raise ValidationError(f"Invalid plan transition from {plan.status} to {new_status}.")

            now = timezone.now()
            if new_status == SuccessPlanStatus.ACTIVE:
                # Re-check active singleton
                if LearningStudentSuccessPlan.objects.filter(
                    tenant_id=tenant_id, student_id=plan.student_id, status=SuccessPlanStatus.ACTIVE
                ).exclude(id=plan.id).exists():
                    raise ValidationError("Another ACTIVE plan already exists for this student.")
                plan.paused_at = None
            elif new_status == SuccessPlanStatus.PAUSED:
                plan.paused_at = now
            elif new_status == SuccessPlanStatus.COMPLETED:
                plan.completed_at = now
            elif new_status == SuccessPlanStatus.SUPERSEDED:
                plan.superseded_at = now
            elif new_status == SuccessPlanStatus.ARCHIVED:
                plan.archived_at = now

            old_status = plan.status
            plan.status = new_status
            plan.clean()
            plan.save()

            action_map = {
                SuccessPlanStatus.PAUSED: SuccessAuditAction.PAUSE_SUCCESS_PLAN,
                SuccessPlanStatus.ACTIVE: SuccessAuditAction.RESUME_SUCCESS_PLAN,
                SuccessPlanStatus.COMPLETED: SuccessAuditAction.COMPLETE_SUCCESS_PLAN,
                SuccessPlanStatus.SUPERSEDED: SuccessAuditAction.SUPERSEDE_SUCCESS_PLAN,
                SuccessPlanStatus.ARCHIVED: SuccessAuditAction.ARCHIVE_SUCCESS_PLAN,
            }
            audit_action = action_map.get(new_status, SuccessAuditAction.CREATE_SUCCESS_PLAN)

            cls.emit_audit_log(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=audit_action,
                target_plan=plan,
                metadata={"from_status": old_status, "to_status": new_status},
            )
            return plan

    # -------------------------------------------------------------------------
    # 2. SUCCESS ACTION STEP METHODS
    # -------------------------------------------------------------------------

    @classmethod
    def create_action_step(
        cls,
        tenant_id: uuid.UUID,
        plan_id: uuid.UUID,
        actor_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
        sequence_order: int = 1,
        target_date: Optional[Any] = None,
    ) -> SuccessActionStep:
        """Creates a sequential, non-authoritative action step under a success plan."""
        cls.assert_no_pii_in_text(title, "title")
        cls.assert_no_pii_in_text(description, "description")

        with transaction.atomic():
            cls.establish_tenant_session(tenant_id)
            plan = LearningStudentSuccessPlan.objects.filter(tenant_id=tenant_id, id=plan_id).first()
            if not plan:
                raise ValidationError("Parent success plan not found in tenant.")

            if sequence_order < 1:
                raise ValidationError("Sequence order must be >= 1.")

            if SuccessActionStep.objects.filter(tenant_id=tenant_id, plan_id=plan_id, sequence_order=sequence_order).exists():
                raise ValidationError(f"Action step with sequence_order={sequence_order} already exists for this plan.")

            step = SuccessActionStep(
                tenant_id=tenant_id,
                plan=plan,
                title=title.strip(),
                description=description,
                sequence_order=sequence_order,
                target_date=target_date,
                is_authoritative=False,
                status=SuccessActionStepStatus.PENDING,
            )
            step.clean()
            step.save()

            cls.emit_audit_log(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=SuccessAuditAction.CREATE_ACTION_STEP,
                target_action_step=step,
                metadata={"sequence_order": step.sequence_order, "title": step.title},
            )
            return step

    @classmethod
    def transition_step_status(
        cls,
        tenant_id: uuid.UUID,
        step_id: uuid.UUID,
        actor_id: uuid.UUID,
        new_status: SuccessActionStepStatus,
    ) -> SuccessActionStep:
        """Transitions action step status according to FSM rules."""
        with transaction.atomic():
            cls.establish_tenant_session(tenant_id)
            step = SuccessActionStep.objects.select_for_update().filter(tenant_id=tenant_id, id=step_id).first()
            if not step:
                raise ValidationError("Action step not found in tenant.")

            # Authorization: Student owner, mentor, or admin of tenant can transition
            membership = TenantMembership.objects.filter(tenant_id=tenant_id, user_id=actor_id).first()
            if not membership:
                raise PermissionDenied("Actor does not have membership in this tenant.")
            if membership.role == "student" and str(step.plan.student_id) != str(actor_id):
                raise PermissionDenied("Students cannot transition action steps belonging to other students.")

            if new_status not in cls.VALID_STEP_TRANSITIONS.get(step.status, set()):
                raise ValidationError(f"Invalid action step transition from {step.status} to {new_status}.")

            old_status = step.status
            if new_status == SuccessActionStepStatus.COMPLETED:
                step.completed_at = timezone.now()
            else:
                step.completed_at = None

            step.status = new_status
            step.clean()
            step.save()

            cls.emit_audit_log(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=SuccessAuditAction.TRANSITION_ACTION_STEP,
                target_action_step=step,
                metadata={"from_status": old_status, "to_status": new_status},
            )
            return step

    # -------------------------------------------------------------------------
    # 3. SUCCESS TIMELINE EVENT METHODS (Continuity Coordinator)
    # -------------------------------------------------------------------------

    @classmethod
    def append_timeline_event(
        cls,
        tenant_id: uuid.UUID,
        plan_id: uuid.UUID,
        actor_id: uuid.UUID,
        event_type: SuccessTimelineEventType,
        headline: str,
        detail: Optional[str] = None,
        target_goal_id: Optional[uuid.UUID] = None,
        target_insight_id: Optional[uuid.UUID] = None,
        target_reflection_id: Optional[uuid.UUID] = None,
        target_action_step_id: Optional[uuid.UUID] = None,
        target_milestone_id: Optional[uuid.UUID] = None,
        replaces_event_id: Optional[uuid.UUID] = None,
        client_mutation_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SuccessTimelineEvent:
        """
        Appends an immutable timeline event connecting formative learning nodes.
        Enforces 5-way XOR target linking, 1-to-1 type coupling, and client idempotency.
        """
        cls.assert_no_pii_in_text(headline, "headline")
        cls.assert_no_pii_in_text(detail, "detail")

        with transaction.atomic():
            cls.establish_tenant_session(tenant_id)

            # Idempotency check via client_mutation_id
            if client_mutation_id:
                existing = SuccessTimelineEvent.objects.filter(
                    tenant_id=tenant_id, client_mutation_id=client_mutation_id
                ).first()
                if existing:
                    return existing

            plan = LearningStudentSuccessPlan.objects.filter(tenant_id=tenant_id, id=plan_id).first()
            if not plan:
                raise ValidationError("Plan not found in tenant.")

            # Resolve targets with tenant verification
            target_goal = None
            if target_goal_id:
                target_goal = StudentLearningGoal.objects.filter(tenant_id=tenant_id, id=target_goal_id).first()
                if not target_goal:
                    raise ValidationError("Referenced learning goal not found in tenant.")

            target_insight = None
            if target_insight_id:
                target_insight = LearningInsight.objects.filter(tenant_id=tenant_id, id=target_insight_id).first()
                if not target_insight:
                    raise ValidationError("Referenced learning insight not found in tenant.")

            target_reflection = None
            if target_reflection_id:
                target_reflection = LearningReflection.objects.filter(tenant_id=tenant_id, id=target_reflection_id).first()
                if not target_reflection:
                    raise ValidationError("Referenced reflection not found in tenant.")

            target_action_step = None
            if target_action_step_id:
                target_action_step = SuccessActionStep.objects.filter(tenant_id=tenant_id, id=target_action_step_id).first()
                if not target_action_step:
                    raise ValidationError("Referenced action step not found in tenant.")

            target_milestone = None
            if target_milestone_id:
                target_milestone = LearningMilestone.objects.filter(tenant_id=tenant_id, id=target_milestone_id).first()
                if not target_milestone:
                    raise ValidationError("Referenced learning milestone not found in tenant.")

            replaces_event = None
            if replaces_event_id:
                replaces_event = SuccessTimelineEvent.objects.filter(tenant_id=tenant_id, id=replaces_event_id).first()
                if not replaces_event:
                    raise ValidationError("Referenced prior timeline event not found in tenant.")

            sanitized_meta = cls.sanitize_pii(metadata or {})

            event = SuccessTimelineEvent(
                tenant_id=tenant_id,
                plan=plan,
                actor_id=actor_id,
                event_type=event_type,
                headline=headline.strip(),
                detail=detail,
                target_goal=target_goal,
                target_insight=target_insight,
                target_reflection=target_reflection,
                target_action_step=target_action_step,
                target_milestone=target_milestone,
                replaces_event=replaces_event,
                client_mutation_id=client_mutation_id,
                metadata=sanitized_meta,
            )
            event.clean()
            event.save()

            cls.emit_audit_log(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=SuccessAuditAction.APPEND_TIMELINE_EVENT,
                target_timeline_event=event,
                metadata={"event_type": event.event_type, "headline": event.headline},
            )
            return event
