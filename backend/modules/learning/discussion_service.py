import uuid
from typing import Optional
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from modules.learning.models import (
    Cohort,
    Lesson,
    DiscussionThread,
    DiscussionComment,
    DiscussionModerationAction,
    DiscussionStatus,
    ModerationActionType,
    CourseEnrollment,
    EnrollmentStatus,
)


class DiscussionAccessPolicy:
    """
    Authoritative service policy governing access to discussion threads and comments.
    Enforces active enrollment, tenant boundary, and child-safety visibility tiers.
    """

    @staticmethod
    def can_view_thread(thread: DiscussionThread, user_id: uuid.UUID, role: str) -> bool:
        if role in ["STAFF", "ADMIN", "MENTOR"]:
            return True
        if thread.status == DiscussionStatus.APPROVED:
            return True
        if thread.status == DiscussionStatus.PENDING and str(thread.author_id) == str(user_id):
            return True
        return False

    @staticmethod
    def can_view_comment(comment: DiscussionComment, user_id: uuid.UUID, role: str) -> bool:
        if role in ["STAFF", "ADMIN", "MENTOR"]:
            return True
        if comment.status == DiscussionStatus.APPROVED:
            return True
        if comment.status == DiscussionStatus.PENDING and str(comment.author_id) == str(user_id):
            return True
        return False

    @staticmethod
    def verify_participation_eligibility(
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        cohort_id: Optional[uuid.UUID] = None,
        lesson_id: Optional[uuid.UUID] = None,
    ) -> None:
        """
        Verifies that user is either staff/mentor or has active enrollment in the target scope.
        Raises PermissionDenied if unauthorized.
        """
        if role in ["STAFF", "ADMIN", "MENTOR"]:
            return

        # For regular students, active enrollment is mandatory
        if cohort_id:
            cohort = Cohort.objects.filter(tenant_id=tenant_id, id=cohort_id).first()
            if not cohort:
                raise PermissionDenied("Cohort not found or access denied.")
            has_enrollment = CourseEnrollment.objects.filter(
                tenant_id=tenant_id,
                student_id=user_id,
                course_id=cohort.course_id,
                cohort_id=cohort_id,
                status=EnrollmentStatus.ACTIVE,
            ).exists()
            if not has_enrollment:
                raise PermissionDenied("Active enrollment in cohort is required to participate in discussions.")
        elif lesson_id:
            lesson = Lesson.objects.filter(tenant_id=tenant_id, id=lesson_id).first()
            if not lesson:
                raise PermissionDenied("Lesson not found or access denied.")
            has_enrollment = CourseEnrollment.objects.filter(
                tenant_id=tenant_id,
                student_id=user_id,
                course_id=lesson.course_id,
                status=EnrollmentStatus.ACTIVE,
            ).exists()
            if not has_enrollment:
                raise PermissionDenied("Active enrollment in course is required to participate in lesson discussions.")
        else:
            raise ValidationError("Either cohort_id or lesson_id must be provided.")


class DiscussionService:
    """
    Core business logic and transaction service for learning community discussions.
    Guarantees atomic replies_count updates and audit immutability.
    """

    @classmethod
    @transaction.atomic
    def create_thread(
        cls,
        tenant_id: uuid.UUID,
        author_id: uuid.UUID,
        role: str,
        title: str,
        body: str,
        cohort_id: Optional[uuid.UUID] = None,
        lesson_id: Optional[uuid.UUID] = None,
    ) -> DiscussionThread:
        DiscussionAccessPolicy.verify_participation_eligibility(
            tenant_id=tenant_id,
            user_id=author_id,
            role=role,
            cohort_id=cohort_id,
            lesson_id=lesson_id,
        )

        thread = DiscussionThread(
            tenant_id=tenant_id,
            author_id=author_id,
            cohort_id=cohort_id,
            lesson_id=lesson_id,
            title=title.strip(),
            body=body.strip(),
            status=DiscussionStatus.PENDING,  # Child Safety Default
            is_pinned=False,
            is_locked=False,
            replies_count=0,
        )
        thread.full_clean()
        thread.save()
        return thread

    @classmethod
    @transaction.atomic
    def create_comment(
        cls,
        tenant_id: uuid.UUID,
        author_id: uuid.UUID,
        role: str,
        thread_id: uuid.UUID,
        body: str,
        parent_id: Optional[uuid.UUID] = None,
    ) -> DiscussionComment:
        thread = DiscussionThread.objects.select_for_update().filter(tenant_id=tenant_id, id=thread_id).first()
        if not thread:
            raise PermissionDenied("Thread not found or access denied.")

        if thread.is_locked:
            raise PermissionDenied("Discussion thread is locked. New replies cannot be added.")

        DiscussionAccessPolicy.verify_participation_eligibility(
            tenant_id=tenant_id,
            user_id=author_id,
            role=role,
            cohort_id=thread.cohort_id,
            lesson_id=thread.lesson_id,
        )

        if parent_id:
            parent = DiscussionComment.objects.filter(tenant_id=tenant_id, id=parent_id).first()
            if not parent or parent.thread_id != thread.id:
                raise ValidationError("Parent comment does not exist in this discussion thread.")

        comment = DiscussionComment(
            tenant_id=tenant_id,
            thread=thread,
            author_id=author_id,
            body=body.strip(),
            parent_id=parent_id,
            status=DiscussionStatus.PENDING,  # Child Safety Default
            is_mentor_endorsed=False,
        )
        comment.full_clean()
        comment.save()
        return comment

    @classmethod
    @transaction.atomic
    def moderate_thread(
        cls,
        tenant_id: uuid.UUID,
        thread_id: uuid.UUID,
        action: ModerationActionType,
        performed_by: uuid.UUID,
        reason: str,
        note: str = "",
    ) -> DiscussionThread:
        thread = DiscussionThread.objects.select_for_update().filter(tenant_id=tenant_id, id=thread_id).first()
        if not thread:
            raise PermissionDenied("Thread not found.")

        old_status = thread.status
        if action == ModerationActionType.APPROVE:
            new_status = DiscussionStatus.APPROVED
        elif action == ModerationActionType.FLAG:
            new_status = DiscussionStatus.FLAGGED
        elif action == ModerationActionType.REMOVE:
            new_status = DiscussionStatus.REMOVED
        elif action == ModerationActionType.RESTORE:
            new_status = DiscussionStatus.APPROVED
        else:
            raise ValidationError(f"Invalid moderation action {action}")

        thread.status = new_status
        thread.save(update_fields=["status", "updated_at"])

        # Create immutable audit entry
        action_entry = DiscussionModerationAction(
            tenant_id=tenant_id,
            target_thread=thread,
            action=action,
            previous_status=old_status,
            new_status=new_status,
            performed_by=performed_by,
            reason=reason,
            note=note,
        )
        action_entry.full_clean()
        action_entry.save()

        return thread

    @classmethod
    @transaction.atomic
    def moderate_comment(
        cls,
        tenant_id: uuid.UUID,
        comment_id: uuid.UUID,
        action: ModerationActionType,
        performed_by: uuid.UUID,
        reason: str,
        note: str = "",
    ) -> DiscussionComment:
        comment = (
            DiscussionComment.objects.select_for_update()
            .select_related("thread")
            .filter(tenant_id=tenant_id, id=comment_id)
            .first()
        )
        if not comment:
            raise PermissionDenied("Comment not found.")

        old_status = comment.status
        if action == ModerationActionType.APPROVE:
            new_status = DiscussionStatus.APPROVED
        elif action == ModerationActionType.FLAG:
            new_status = DiscussionStatus.FLAGGED
        elif action == ModerationActionType.REMOVE:
            new_status = DiscussionStatus.REMOVED
            if comment.is_mentor_endorsed:
                comment.is_mentor_endorsed = False
                comment.endorsed_by_id = None
                comment.endorsed_at = None
        elif action == ModerationActionType.RESTORE:
            new_status = DiscussionStatus.APPROVED
        else:
            raise ValidationError(f"Invalid moderation action {action}")

        comment.status = new_status
        comment.save(update_fields=["status", "is_mentor_endorsed", "endorsed_by_id", "endorsed_at", "updated_at"])

        # Atomic updates to thread.replies_count ONLY on transitions to/from APPROVED
        if old_status != DiscussionStatus.APPROVED and new_status == DiscussionStatus.APPROVED:
            DiscussionThread.objects.filter(id=comment.thread_id).update(replies_count=F("replies_count") + 1)
        elif old_status == DiscussionStatus.APPROVED and new_status != DiscussionStatus.APPROVED:
            DiscussionThread.objects.filter(id=comment.thread_id, replies_count__gt=0).update(
                replies_count=F("replies_count") - 1
            )

        # Create immutable audit entry
        action_entry = DiscussionModerationAction(
            tenant_id=tenant_id,
            target_comment=comment,
            action=action,
            previous_status=old_status,
            new_status=new_status,
            performed_by=performed_by,
            reason=reason,
            note=note,
        )
        action_entry.full_clean()
        action_entry.save()

        return comment

    @classmethod
    @transaction.atomic
    def endorse_comment(
        cls,
        tenant_id: uuid.UUID,
        comment_id: uuid.UUID,
        mentor_id: uuid.UUID,
        role: str,
    ) -> DiscussionComment:
        if role not in ["MENTOR", "STAFF", "ADMIN"]:
            raise PermissionDenied("Only mentors and staff can endorse comments.")

        comment = DiscussionComment.objects.select_for_update().filter(tenant_id=tenant_id, id=comment_id).first()
        if not comment:
            raise PermissionDenied("Comment not found.")

        if comment.status != DiscussionStatus.APPROVED:
            raise ValidationError("Only approved comments can be endorsed by a mentor.")

        comment.is_mentor_endorsed = True
        comment.endorsed_by_id = mentor_id
        comment.endorsed_at = timezone.now()
        comment.save(update_fields=["is_mentor_endorsed", "endorsed_by_id", "endorsed_at", "updated_at"])
        return comment

    @classmethod
    @transaction.atomic
    def pin_thread(
        cls,
        tenant_id: uuid.UUID,
        thread_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        is_pinned: bool,
    ) -> DiscussionThread:
        if role not in ["MENTOR", "STAFF", "ADMIN"]:
            raise PermissionDenied("Only mentors and staff can pin/unpin discussion threads.")

        thread = DiscussionThread.objects.select_for_update().filter(tenant_id=tenant_id, id=thread_id).first()
        if not thread:
            raise PermissionDenied("Thread not found.")

        thread.is_pinned = is_pinned
        thread.save(update_fields=["is_pinned", "updated_at"])
        return thread
