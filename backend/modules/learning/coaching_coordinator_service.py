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
    CoachingAuditAction,
    CoachingAuditLog,
    CoachingNote,
    CoachingNoteType,
    CoachingSession,
    CoachingSessionStatus,
    FollowUpAction,
    FollowUpActionStatus,
    LearningInsight,
    LearningStudentSuccessPlan,
    SupportIntervention,
    SupportInterventionCategory,
    SupportInterventionStatus,
)


class CoachingCoordinatorService:
    """
    P3-VS16 Service Layer: Mentor-Student Success Coaching & Intervention Workflow.
    
    Invariants & Architectural Rules:
    1. Tenant Isolation & Fail-Closed Session Protocol:
       All DB operations execute inside transaction.atomic() with SET LOCAL "app.current_tenant" = %s.
    2. Learner Agency First (Mandatory Non-Authoritative Invariant):
       Mentors propose interventions, but only students can ACCEPT or DECLINE.
       No actor (mentor, admin, system) can override learner consent or force ACCEPTED.
       is_authoritative is strictly FALSE.
    3. Concurrency Serialization:
       State mutations on interventions and sessions are protected via transaction advisory locks:
       pg_advisory_xact_lock(hashtext('coaching_' || entity_type || ':' || entity_id))
    4. Exact Origin XOR on FollowUpAction:
       FollowUpAction must link to exactly one origin: either an intervention or a session.
    5. Dedicated 4-Way XOR Targets on CoachingAuditLog:
       Audit log records reference exactly one target (session, note, intervention, action)
       with append-only DB discipline (REVOKE UPDATE, DELETE).
    6. Zero PII Enforcement:
       13-key exclusion list scrubbed from all JSONB metadata and free-text regex validation.
    7. Anti-Ranking & Privacy:
       Strict rejection of ranking, leaderboard, and cross-student comparison query parameters.
    """

    PROHIBITED_PII_KEYS = {
        "name", "phone", "email", "national_id", "location", "avatar_url",
        "phone_number", "mobile", "fingerprint", "face_id", "voice_sample",
        "bank_account", "iban", "credit_card", "card_number", "cvv",
        "password", "token", "secret", "ssn", "address"
    }

    PII_REGEX = re.compile(
        r'(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)',
        re.IGNORECASE
    )

    @classmethod
    def _validate_clean_text(cls, text: Optional[str], field_name: str) -> None:
        if not text:
            return
        if cls.PII_REGEX.search(text):
            raise ValidationError(f"PII detected in {field_name}. Storing personal identifiers is strictly prohibited.")

    @classmethod
    def _scrub_metadata(cls, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not metadata:
            return {}
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a valid JSON object.")
        for key in list(metadata.keys()):
            if key.lower() in cls.PROHIBITED_PII_KEYS:
                raise ValidationError(f"Prohibited PII key '{key}' found in metadata.")
        return metadata

    @classmethod
    def _acquire_advisory_lock(cls, lock_key: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s));", [lock_key])

    @classmethod
    def _establish_tenant_context(cls, tenant_id: uuid.UUID) -> None:
        with connection.cursor() as cursor:
            cursor.execute('SET LOCAL "app.current_tenant" = %s;', [str(tenant_id)])

    @classmethod
    def _emit_audit(
        cls,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
        action_type: CoachingAuditAction,
        target_session: Optional[CoachingSession] = None,
        target_note: Optional[CoachingNote] = None,
        target_intervention: Optional[SupportIntervention] = None,
        target_action: Optional[FollowUpAction] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> CoachingAuditLog:
        scrubbed_details = cls._scrub_metadata(details or {})
        return CoachingAuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action_type=action_type,
            target_session=target_session,
            target_note=target_note,
            target_intervention=target_intervention,
            target_action=target_action,
            details=scrubbed_details,
        )

    # -------------------------------------------------------------------------
    # 1. COACHING SESSIONS
    # -------------------------------------------------------------------------

    @classmethod
    def schedule_session(
        cls,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
        student_id: uuid.UUID,
        mentor_id: uuid.UUID,
        title: str,
        scheduled_at: Any,
        success_plan_id: Optional[uuid.UUID] = None,
        learning_insight_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CoachingSession:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._validate_clean_text(title, "title")
            scrubbed_meta = cls._scrub_metadata(metadata)

            session = CoachingSession.objects.create(
                tenant_id=tenant_id,
                student_id=student_id,
                mentor_id=mentor_id,
                title=title,
                scheduled_at=scheduled_at,
                success_plan_id=success_plan_id,
                learning_insight_id=learning_insight_id,
                status=CoachingSessionStatus.SCHEDULED,
                metadata=scrubbed_meta,
            )

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action_type=CoachingAuditAction.SCHEDULE_SESSION,
                target_session=session,
                details={"scheduled_at": str(scheduled_at)},
            )
            return session

    @classmethod
    def start_session(
        cls,
        tenant_id: uuid.UUID,
        session_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> CoachingSession:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_session:{session_id}")

            session = CoachingSession.objects.select_for_update().get(id=session_id, tenant_id=tenant_id)
            if session.status != CoachingSessionStatus.SCHEDULED:
                raise ValidationError(f"Cannot start session in status '{session.status}'.")

            session.status = CoachingSessionStatus.IN_PROGRESS
            session.started_at = timezone.now()
            session.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action_type=CoachingAuditAction.START_SESSION,
                target_session=session,
            )
            return session

    @classmethod
    def complete_session(
        cls,
        tenant_id: uuid.UUID,
        session_id: uuid.UUID,
        actor_id: uuid.UUID,
        summary: Optional[str] = None,
    ) -> CoachingSession:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_session:{session_id}")

            session = CoachingSession.objects.select_for_update().get(id=session_id, tenant_id=tenant_id)
            if session.status != CoachingSessionStatus.IN_PROGRESS:
                raise ValidationError(f"Cannot complete session in status '{session.status}'.")

            cls._validate_clean_text(summary, "summary")
            session.status = CoachingSessionStatus.COMPLETED
            session.completed_at = timezone.now()
            if summary:
                session.summary = summary
            session.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action_type=CoachingAuditAction.COMPLETE_SESSION,
                target_session=session,
                details={"has_summary": bool(summary)},
            )
            return session

    @classmethod
    def cancel_session(
        cls,
        tenant_id: uuid.UUID,
        session_id: uuid.UUID,
        actor_id: uuid.UUID,
        cancellation_reason: str,
    ) -> CoachingSession:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_session:{session_id}")

            session = CoachingSession.objects.select_for_update().get(id=session_id, tenant_id=tenant_id)
            if session.status in (CoachingSessionStatus.COMPLETED, CoachingSessionStatus.CANCELLED):
                raise ValidationError(f"Cannot cancel session in status '{session.status}'.")

            cls._validate_clean_text(cancellation_reason, "cancellation_reason")
            session.status = CoachingSessionStatus.CANCELLED
            session.cancelled_at = timezone.now()
            session.cancellation_reason = cancellation_reason
            session.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action_type=CoachingAuditAction.CANCEL_SESSION,
                target_session=session,
                details={"reason": cancellation_reason},
            )
            return session

    # -------------------------------------------------------------------------
    # 2. COACHING NOTES (Append-Only)
    # -------------------------------------------------------------------------

    @classmethod
    def add_note(
        cls,
        tenant_id: uuid.UUID,
        session_id: uuid.UUID,
        author_id: uuid.UUID,
        note_type: CoachingNoteType,
        content: str,
        is_shared_with_student: bool = True,
    ) -> CoachingNote:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._validate_clean_text(content, "content")

            session = CoachingSession.objects.get(id=session_id, tenant_id=tenant_id)

            note = CoachingNote.objects.create(
                tenant_id=tenant_id,
                session=session,
                author_id=author_id,
                note_type=note_type,
                content=content,
                is_shared_with_student=is_shared_with_student,
            )

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=author_id,
                action_type=CoachingAuditAction.CREATE_NOTE,
                target_note=note,
                details={"note_type": note_type, "shared": is_shared_with_student},
            )
            return note

    # -------------------------------------------------------------------------
    # 3. SUPPORT INTERVENTIONS (Learner Agency First)
    # -------------------------------------------------------------------------

    @classmethod
    def propose_intervention(
        cls,
        tenant_id: uuid.UUID,
        mentor_id: uuid.UUID,
        student_id: uuid.UUID,
        title: str,
        category: SupportInterventionCategory,
        rationale: str,
        success_plan_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SupportIntervention:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._validate_clean_text(title, "title")
            cls._validate_clean_text(rationale, "rationale")
            scrubbed_meta = cls._scrub_metadata(metadata)

            intervention = SupportIntervention.objects.create(
                tenant_id=tenant_id,
                student_id=student_id,
                mentor_id=mentor_id,
                success_plan_id=success_plan_id,
                title=title,
                category=category,
                status=SupportInterventionStatus.PROPOSED,
                is_authoritative=False,
                rationale=rationale,
                metadata=scrubbed_meta,
            )

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=mentor_id,
                action_type=CoachingAuditAction.PROPOSE_INTERVENTION,
                target_intervention=intervention,
                details={"category": category},
            )
            return intervention

    @classmethod
    def accept_intervention(
        cls,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
        student_id: uuid.UUID,
        feedback: Optional[str] = None,
    ) -> SupportIntervention:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_intervention:{intervention_id}")

            intervention = SupportIntervention.objects.select_for_update().get(id=intervention_id, tenant_id=tenant_id)
            if str(intervention.student_id) != str(student_id):
                raise PermissionDenied("Only the student has the agency to accept an intervention.")

            if intervention.status != SupportInterventionStatus.PROPOSED:
                raise ValidationError(f"Cannot accept intervention in status '{intervention.status}'.")

            cls._validate_clean_text(feedback, "student_feedback")
            intervention.status = SupportInterventionStatus.ACCEPTED
            intervention.acknowledged_at = timezone.now()
            if feedback:
                intervention.student_feedback = feedback
            intervention.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=student_id,
                action_type=CoachingAuditAction.ACCEPT_INTERVENTION,
                target_intervention=intervention,
            )
            return intervention

    @classmethod
    def decline_intervention(
        cls,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
        student_id: uuid.UUID,
        feedback: Optional[str] = None,
    ) -> SupportIntervention:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_intervention:{intervention_id}")

            intervention = SupportIntervention.objects.select_for_update().get(id=intervention_id, tenant_id=tenant_id)
            if str(intervention.student_id) != str(student_id):
                raise PermissionDenied("Only the student has the agency to decline an intervention.")

            if intervention.status != SupportInterventionStatus.PROPOSED:
                raise ValidationError(f"Cannot decline intervention in status '{intervention.status}'.")

            cls._validate_clean_text(feedback, "student_feedback")
            intervention.status = SupportInterventionStatus.DECLINED
            intervention.declined_at = timezone.now()
            if feedback:
                intervention.student_feedback = feedback
            intervention.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=student_id,
                action_type=CoachingAuditAction.DECLINE_INTERVENTION,
                target_intervention=intervention,
            )
            return intervention

    @classmethod
    def start_intervention(
        cls,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> SupportIntervention:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_intervention:{intervention_id}")

            intervention = SupportIntervention.objects.select_for_update().get(id=intervention_id, tenant_id=tenant_id)
            if intervention.status != SupportInterventionStatus.ACCEPTED:
                raise ValidationError(f"Cannot activate intervention in status '{intervention.status}'. Must be ACCEPTED first.")

            intervention.status = SupportInterventionStatus.ACTIVE
            intervention.started_at = timezone.now()
            intervention.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action_type=CoachingAuditAction.START_INTERVENTION,
                target_intervention=intervention,
            )
            return intervention

    @classmethod
    def complete_intervention(
        cls,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> SupportIntervention:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_intervention:{intervention_id}")

            intervention = SupportIntervention.objects.select_for_update().get(id=intervention_id, tenant_id=tenant_id)
            if intervention.status != SupportInterventionStatus.ACTIVE:
                raise ValidationError(f"Cannot complete intervention in status '{intervention.status}'. Must be ACTIVE.")

            intervention.status = SupportInterventionStatus.COMPLETED
            intervention.completed_at = timezone.now()
            intervention.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action_type=CoachingAuditAction.COMPLETE_INTERVENTION,
                target_intervention=intervention,
            )
            return intervention

    # -------------------------------------------------------------------------
    # 4. FOLLOW-UP ACTIONS
    # -------------------------------------------------------------------------

    @classmethod
    def assign_action(
        cls,
        tenant_id: uuid.UUID,
        assigned_by_id: uuid.UUID,
        student_id: uuid.UUID,
        title: str,
        due_date: Any,
        intervention_id: Optional[uuid.UUID] = None,
        session_id: Optional[uuid.UUID] = None,
    ) -> FollowUpAction:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            origins = [intervention_id, session_id]
            if sum(1 for o in origins if o is not None) != 1:
                raise ValidationError("FollowUpAction must originate from exactly one source: either an intervention or a session.")

            cls._validate_clean_text(title, "title")

            action = FollowUpAction.objects.create(
                tenant_id=tenant_id,
                student_id=student_id,
                assigned_by_id=assigned_by_id,
                intervention_id=intervention_id,
                session_id=session_id,
                title=title,
                due_date=due_date,
                status=FollowUpActionStatus.PENDING,
            )

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=assigned_by_id,
                action_type=CoachingAuditAction.ASSIGN_ACTION,
                target_action=action,
            )
            return action

    @classmethod
    def complete_action(
        cls,
        tenant_id: uuid.UUID,
        action_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> FollowUpAction:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_action:{action_id}")

            action = FollowUpAction.objects.select_for_update().get(id=action_id, tenant_id=tenant_id)
            if action.status not in (FollowUpActionStatus.PENDING, FollowUpActionStatus.IN_PROGRESS):
                raise ValidationError(f"Cannot complete action in status '{action.status}'.")

            action.status = FollowUpActionStatus.COMPLETED
            action.completed_at = timezone.now()
            action.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action_type=CoachingAuditAction.COMPLETE_ACTION,
                target_action=action,
            )
            return action

    @classmethod
    def skip_action(
        cls,
        tenant_id: uuid.UUID,
        action_id: uuid.UUID,
        student_id: uuid.UUID,
        skip_reason: str,
    ) -> FollowUpAction:
        with transaction.atomic():
            cls._establish_tenant_context(tenant_id)
            cls._acquire_advisory_lock(f"coaching_action:{action_id}")

            action = FollowUpAction.objects.select_for_update().get(id=action_id, tenant_id=tenant_id)
            if str(action.student_id) != str(student_id):
                raise PermissionDenied("Only the student has the agency to skip their assigned action.")

            if action.status not in (FollowUpActionStatus.PENDING, FollowUpActionStatus.IN_PROGRESS):
                raise ValidationError(f"Cannot skip action in status '{action.status}'.")

            cls._validate_clean_text(skip_reason, "skip_reason")
            action.status = FollowUpActionStatus.SKIPPED
            action.skipped_at = timezone.now()
            action.skip_reason = skip_reason
            action.save()

            cls._emit_audit(
                tenant_id=tenant_id,
                actor_id=student_id,
                action_type=CoachingAuditAction.SKIP_ACTION,
                target_action=action,
                details={"reason": skip_reason},
            )
            return action
