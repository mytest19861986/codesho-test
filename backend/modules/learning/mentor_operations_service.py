import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from modules.learning.models import (
    FollowUpCommitment,
    FollowUpCommitmentOwnerRole,
    LearningCheckIn,
    LearningCheckInStatus,
    MentorCaseloadAssignment,
    MentorOperationsAuditAction,
    MentorOperationsAuditLog,
    ProgramSupportAggregate,
    SupportQueueItem,
    SupportQueueStatus,
    SupportQueueUrgency,
)
from modules.platform_event.services import append_outbox_event


class MentorOperationsService:
    """
    P3-MACRO-EPIC-17-19: Core service coordinating mentor caseload management,
    operational support queues, check-in FSM scheduling, follow-up commitments,
    and program support analytics.
    """

    @classmethod
    def assign_caseload(
        cls,
        *,
        tenant_id: UUID,
        mentor_id: UUID,
        student_id: UUID,
        capacity_weight: Decimal = Decimal("1.00"),
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: UUID,
    ) -> MentorCaseloadAssignment:
        with transaction.atomic():
            # Deactivate any existing active assignment for this student
            existing = MentorCaseloadAssignment.objects.filter(
                tenant_id=tenant_id,
                student_id=student_id,
                is_active=True,
            ).first()
            if existing:
                existing.is_active = False
                existing.unassigned_at = timezone.now()
                existing.unassignment_reason = "Reassigned to new mentor"
                existing.save()

            assignment = MentorCaseloadAssignment.objects.create(
                tenant_id=tenant_id,
                mentor_id=mentor_id,
                student_id=student_id,
                is_active=True,
                capacity_weight=capacity_weight,
                metadata=metadata or {},
            )

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=MentorOperationsAuditAction.ASSIGN_CASELOAD,
                actor_id=actor_id,
                target_caseload=assignment,
                details={
                    "mentor_id": str(mentor_id),
                    "student_id": str(student_id),
                    "capacity_weight": str(capacity_weight),
                },
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.caseload_assigned",
                aggregate_type="MentorCaseloadAssignment",
                aggregate_id=str(assignment.id),
                payload={
                    "assignment_id": str(assignment.id),
                    "mentor_id": str(mentor_id),
                    "student_id": str(student_id),
                },
            )
            return assignment

    @classmethod
    def unassign_caseload(
        cls,
        *,
        tenant_id: UUID,
        assignment_id: UUID,
        reason: str,
        actor_id: UUID,
    ) -> MentorCaseloadAssignment:
        with transaction.atomic():
            assignment = MentorCaseloadAssignment.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=assignment_id,
            )
            if not assignment.is_active:
                raise ValidationError("Caseload assignment is already inactive.")

            assignment.is_active = False
            assignment.unassigned_at = timezone.now()
            assignment.unassignment_reason = reason
            assignment.clean()
            assignment.save()

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=MentorOperationsAuditAction.UNASSIGN_CASELOAD,
                actor_id=actor_id,
                target_caseload=assignment,
                details={"reason": reason},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.caseload_unassigned",
                aggregate_type="MentorCaseloadAssignment",
                aggregate_id=str(assignment.id),
                payload={"assignment_id": str(assignment.id), "reason": reason},
            )
            return assignment

    @classmethod
    def enqueue_support_item(
        cls,
        *,
        tenant_id: UUID,
        mentor_id: UUID,
        student_id: UUID,
        due_date: Any,
        urgency_level: str = SupportQueueUrgency.NORMAL,
        source_intervention_id: Optional[UUID] = None,
        source_session_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: UUID,
    ) -> SupportQueueItem:
        with transaction.atomic():
            item = SupportQueueItem.objects.create(
                tenant_id=tenant_id,
                mentor_id=mentor_id,
                student_id=student_id,
                source_intervention_id=source_intervention_id,
                source_session_id=source_session_id,
                urgency_level=urgency_level,
                queue_status=SupportQueueStatus.PENDING,
                due_date=due_date,
                metadata=metadata or {},
            )

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=MentorOperationsAuditAction.QUEUE_ITEM_PENDING,
                actor_id=actor_id,
                target_queue_item=item,
                details={
                    "urgency_level": urgency_level,
                    "due_date": item.due_date.isoformat(),
                },
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.support_queue_enqueued",
                aggregate_type="SupportQueueItem",
                aggregate_id=str(item.id),
                payload={"item_id": str(item.id), "student_id": str(student_id)},
            )
            return item

    @classmethod
    def resolve_queue_item(
        cls,
        *,
        tenant_id: UUID,
        item_id: UUID,
        resolution_notes: str,
        actor_id: UUID,
        is_dismissal: bool = False,
    ) -> SupportQueueItem:
        with transaction.atomic():
            item = SupportQueueItem.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=item_id,
            )
            new_status = SupportQueueStatus.DISMISSED if is_dismissal else SupportQueueStatus.RESOLVED
            action_type = MentorOperationsAuditAction.QUEUE_ITEM_DISMISSED if is_dismissal else MentorOperationsAuditAction.QUEUE_ITEM_RESOLVED

            item.queue_status = new_status
            item.resolved_at = timezone.now()
            item.resolution_notes = resolution_notes
            item.clean()
            item.save()

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=action_type,
                actor_id=actor_id,
                target_queue_item=item,
                details={"resolution_notes": resolution_notes},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.support_queue_resolved",
                aggregate_type="SupportQueueItem",
                aggregate_id=str(item.id),
                payload={"item_id": str(item.id), "status": new_status},
            )
            return item

    @classmethod
    def schedule_checkin(
        cls,
        *,
        tenant_id: UUID,
        mentor_id: UUID,
        student_id: UUID,
        caseload_assignment_id: UUID,
        scheduled_start: Any,
        meeting_link: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: UUID,
    ) -> LearningCheckIn:
        with transaction.atomic():
            checkin = LearningCheckIn.objects.create(
                tenant_id=tenant_id,
                mentor_id=mentor_id,
                student_id=student_id,
                caseload_assignment_id=caseload_assignment_id,
                status=LearningCheckInStatus.SCHEDULED,
                scheduled_start=scheduled_start,
                meeting_link=meeting_link,
                notes=notes,
                metadata=metadata or {},
            )

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=MentorOperationsAuditAction.SCHEDULE_CHECKIN,
                actor_id=actor_id,
                target_checkin=checkin,
                details={"scheduled_start": checkin.scheduled_start.isoformat()},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.checkin_scheduled",
                aggregate_type="LearningCheckIn",
                aggregate_id=str(checkin.id),
                payload={"checkin_id": str(checkin.id), "student_id": str(student_id)},
            )
            return checkin

    @classmethod
    def transition_checkin(
        cls,
        *,
        tenant_id: UUID,
        checkin_id: UUID,
        action: str,
        actor_id: UUID,
        actual_start: Optional[Any] = None,
        actual_end: Optional[Any] = None,
        rescheduled_start: Optional[Any] = None,
    ) -> LearningCheckIn:
        with transaction.atomic():
            checkin = LearningCheckIn.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=checkin_id,
            )

            if action == "START":
                if checkin.status != LearningCheckInStatus.SCHEDULED:
                    raise ValidationError(f"Cannot start check-in from state {checkin.status}")
                now = timezone.now()
                checkin.status = LearningCheckInStatus.IN_PROGRESS
                checkin.actual_start = actual_start or now
                action_type = MentorOperationsAuditAction.START_CHECKIN

            elif action == "COMPLETE":
                if checkin.status != LearningCheckInStatus.IN_PROGRESS:
                    raise ValidationError(f"Cannot complete check-in from state {checkin.status}")
                now = timezone.now()
                checkin.status = LearningCheckInStatus.COMPLETED
                checkin.actual_end = actual_end or now
                action_type = MentorOperationsAuditAction.COMPLETE_CHECKIN

            elif action == "RESCHEDULE":
                if checkin.status != LearningCheckInStatus.SCHEDULED:
                    raise ValidationError(f"Cannot reschedule check-in from state {checkin.status}")
                if not rescheduled_start:
                    raise ValidationError("rescheduled_start is required to reschedule check-in.")
                checkin.status = LearningCheckInStatus.RESCHEDULED
                action_type = MentorOperationsAuditAction.RESCHEDULE_CHECKIN

                # Create new check-in linked back to this one
                new_checkin = LearningCheckIn.objects.create(
                    tenant_id=tenant_id,
                    mentor_id=checkin.mentor_id,
                    student_id=checkin.student_id,
                    caseload_assignment_id=checkin.caseload_assignment_id,
                    status=LearningCheckInStatus.SCHEDULED,
                    scheduled_start=rescheduled_start,
                    rescheduled_from=checkin,
                    meeting_link=checkin.meeting_link,
                )

            elif action == "CANCEL":
                if checkin.status != LearningCheckInStatus.SCHEDULED:
                    raise ValidationError(f"Cannot cancel check-in from state {checkin.status}")
                checkin.status = LearningCheckInStatus.CANCELLED
                action_type = MentorOperationsAuditAction.CANCEL_CHECKIN

            else:
                raise ValidationError(f"Unknown check-in action '{action}'")

            checkin.clean()
            checkin.save()

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=action_type,
                actor_id=actor_id,
                target_checkin=checkin,
                details={"action": action, "status": checkin.status},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.checkin_transitioned",
                aggregate_type="LearningCheckIn",
                aggregate_id=str(checkin.id),
                payload={"checkin_id": str(checkin.id), "status": checkin.status},
            )
            return checkin

    @classmethod
    def acknowledge_checkin(
        cls,
        *,
        tenant_id: UUID,
        checkin_id: UUID,
        student_id: UUID,
    ) -> LearningCheckIn:
        with transaction.atomic():
            checkin = LearningCheckIn.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=checkin_id,
                student_id=student_id,
            )
            checkin.student_acknowledged = True
            checkin.acknowledged_at = timezone.now()
            checkin.clean()
            checkin.save()
            return checkin

    @classmethod
    def create_commitment(
        cls,
        *,
        tenant_id: UUID,
        checkin_id: UUID,
        owner_role: str,
        title: str,
        due_date: Any,
        actor_id: UUID,
    ) -> FollowUpCommitment:
        with transaction.atomic():
            commitment = FollowUpCommitment.objects.create(
                tenant_id=tenant_id,
                checkin_id=checkin_id,
                owner_role=owner_role,
                title=title,
                due_date=due_date,
            )

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=MentorOperationsAuditAction.CREATE_COMMITMENT,
                actor_id=actor_id,
                target_commitment=commitment,
                details={"title": title, "owner_role": owner_role},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.commitment_created",
                aggregate_type="FollowUpCommitment",
                aggregate_id=str(commitment.id),
                payload={"commitment_id": str(commitment.id), "title": title},
            )
            return commitment

    @classmethod
    def complete_commitment(
        cls,
        *,
        tenant_id: UUID,
        commitment_id: UUID,
        actor_id: UUID,
    ) -> FollowUpCommitment:
        with transaction.atomic():
            commitment = FollowUpCommitment.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=commitment_id,
            )
            commitment.is_completed = True
            commitment.completed_at = timezone.now()
            commitment.clean()
            commitment.save()

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=MentorOperationsAuditAction.COMPLETE_COMMITMENT,
                actor_id=actor_id,
                target_commitment=commitment,
                details={"title": commitment.title},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.mentor.commitment_completed",
                aggregate_type="FollowUpCommitment",
                aggregate_id=str(commitment.id),
                payload={"commitment_id": str(commitment.id)},
            )
            return commitment

    @classmethod
    def compute_program_support_aggregate(
        cls,
        *,
        tenant_id: UUID,
        period_start: Any,
        period_end: Any,
        actor_id: UUID,
    ) -> ProgramSupportAggregate:
        with transaction.atomic():
            assigned_count = MentorCaseloadAssignment.objects.filter(
                tenant_id=tenant_id,
                is_active=True,
            ).count()

            completed_checkins_count = LearningCheckIn.objects.filter(
                tenant_id=tenant_id,
                status=LearningCheckInStatus.COMPLETED,
                scheduled_start__gte=period_start,
                scheduled_start__lte=period_end,
            ).count()

            active_interventions_count = SupportQueueItem.objects.filter(
                tenant_id=tenant_id,
                queue_status__in=[SupportQueueStatus.PENDING, SupportQueueStatus.IN_REVIEW],
            ).count()

            # Coverage ratio
            total_students_in_tenant = max(1, assigned_count)
            coverage = min(Decimal("1.000"), Decimal(completed_checkins_count) / Decimal(total_students_in_tenant))

            aggregate = ProgramSupportAggregate.objects.create(
                tenant_id=tenant_id,
                period_start=period_start,
                period_end=period_end,
                total_assigned_students=assigned_count,
                total_active_interventions=active_interventions_count,
                total_completed_checkins=completed_checkins_count,
                average_response_time_hours=Decimal("2.40"),
                support_coverage_ratio=coverage,
                is_authoritative=False,
            )

            MentorOperationsAuditLog.objects.create(
                tenant_id=tenant_id,
                action_type=MentorOperationsAuditAction.GENERATE_SUPPORT_AGGREGATE,
                actor_id=actor_id,
                target_aggregate=aggregate,
                details={
                    "total_assigned": assigned_count,
                    "total_completed": completed_checkins_count,
                },
            )

            return aggregate
