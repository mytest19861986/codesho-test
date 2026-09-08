from __future__ import annotations

from typing import Protocol, cast
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest
from django.views.decorators.http import require_GET
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.platform_event.services import append_outbox_event

from .events import LearningDomainEvents
from .models import (
    Assignment,
    AssignmentState,
    AssignmentSubmissionMetrics,
    Course,
    CourseProgressAggregate,
    Feedback,
    LearningPath,
    Lesson,
    Module,
    Progress,
    PublicationState,
    RoleActivityFeed,
    Submission,
    SyntheticMediaAttachment,
    NotificationItem,
)
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionMetricsSerializer,
    CourseProgressAggregateSerializer,
    CourseSerializer,
    FeedbackSerializer,
    LearningPathSerializer,
    LessonSerializer,
    MentorSubmissionQueueSerializer,
    ModuleSerializer,
    NotificationItemSerializer,
    ParentStudentSummarySerializer,
    ProgressSerializer,
    RoleActivityFeedSerializer,
    SubmissionSerializer,
    SyntheticMediaAttachmentSerializer,
)
from .services import (
    AssignmentStateMachine,
    ContentStateMachine,
    ParentLearningSummaryService,
    SubmissionStateMachine,
)


class _Tenant(Protocol):
    id: UUID


class _Membership(Protocol):
    role: str
    is_active: bool


class _TenantRequest(Protocol):
    tenant: _Tenant
    tenant_membership: _Membership


def _invalid_pagination() -> Response:
    return Response({"code": "invalid_pagination"}, status=400)


def _pagination(request: Request) -> tuple[int, int] | Response:
    try:
        page = int(request.query_params.get("page", "1"))
        page_size = int(request.query_params.get("page_size", "20"))
    except (TypeError, ValueError):
        return _invalid_pagination()
    if page <= 0 or page_size <= 0 or page_size > 100:
        return _invalid_pagination()
    return page, page_size


def _tenant_id(request: HttpRequest) -> UUID:
    tenant_request = cast(_TenantRequest, request)
    return tenant_request.tenant.id


def _get_membership_role(request: HttpRequest) -> str | None:
    tenant_request = cast(_TenantRequest, request)
    membership = getattr(tenant_request, "tenant_membership", None)
    if not membership or not getattr(membership, "is_active", False):
        return None
    return getattr(membership, "role", None)


class LearningPathListView(APIView):
    def get(self, request: Request) -> Response:
        pagination = _pagination(request)
        if isinstance(pagination, Response):
            return pagination
        page, page_size = pagination
        start = (page - 1) * page_size
        rows = LearningPath.objects.filter(
            tenant_id=_tenant_id(request), state=PublicationState.PUBLISHED
        ).order_by("code", "id")[start : start + page_size]
        return Response({"results": LearningPathSerializer(rows, many=True).data})


class CourseListView(APIView):
    def get(self, request: Request) -> Response:
        pagination = _pagination(request)
        if isinstance(pagination, Response):
            return pagination
        page, page_size = pagination
        start = (page - 1) * page_size
        rows = Course.objects.filter(
            tenant_id=_tenant_id(request), state=PublicationState.PUBLISHED
        ).order_by("code", "id")[start : start + page_size]
        return Response(
            {
                "results": [
                    {"id": str(row.id), "code": row.code, "title": row.title, "state": row.state}
                    for row in rows
                ]
            }
        )


class CourseLessonListView(APIView):
    def get(self, request: Request, course_id: str) -> Response:
        pagination = _pagination(request)
        if isinstance(pagination, Response):
            return pagination
        try:
            parsed_course_id = UUID(course_id)
        except (ValueError, AttributeError):
            return Response({"code": "not_found"}, status=404)
        course = Course.objects.filter(
            id=parsed_course_id,
            tenant_id=_tenant_id(request),
            state=PublicationState.PUBLISHED,
        ).first()
        if course is None:
            return Response({"code": "not_found"}, status=404)
        page, page_size = pagination
        start = (page - 1) * page_size
        rows = Lesson.objects.filter(
            course_id=course.id,
            tenant_id=_tenant_id(request),
            state=PublicationState.PUBLISHED,
        ).order_by("position", "code", "id")[start : start + page_size]
        return Response(
            {
                "results": [
                    {
                        "id": str(row.id),
                        "code": row.code,
                        "title": row.title,
                        "position": row.position,
                        "state": row.state,
                    }
                    for row in rows
                ]
            }
        )


class StudentDashboardSummaryView(APIView):
    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        courses = Course.objects.filter(
            tenant_id=tenant_id, state=PublicationState.PUBLISHED
        ).order_by("code")
        first_course = courses.first()
        lessons = []
        if first_course:
            lessons = Lesson.objects.filter(
                course=first_course, tenant_id=tenant_id, state=PublicationState.PUBLISHED
            ).order_by("position")

        return Response(
            {
                "courses": CourseSerializer(courses[:10], many=True).data,
                "current_course": CourseSerializer(first_course).data if first_course else None,
                "lessons": LessonSerializer(lessons[:10], many=True).data,
                "progress_summary": {
                    "completed_lessons": 0,
                    "total_lessons": len(lessons),
                    "completion_percentage": 0,
                },
            }
        )


class SubmissionDraftView(APIView):
    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        assignment_id = request.data.get("assignment_id")
        content = request.data.get("content", "")
        student_id = request.data.get("student_id")

        if not assignment_id or not student_id:
            return Response({"code": "invalid_parameters"}, status=400)

        try:
            parsed_aid = UUID(str(assignment_id))
            parsed_sid = UUID(str(student_id))
        except (ValueError, TypeError):
            return Response({"code": "invalid_uuid"}, status=400)

        assignment = Assignment.objects.filter(id=parsed_aid, tenant_id=tenant_id).first()
        if not assignment:
            return Response({"code": "assignment_not_found"}, status=404)

        submission, _ = Submission.objects.update_or_create(
            tenant_id=tenant_id,
            assignment=assignment,
            student_id=parsed_sid,
            defaults={"content": content},
        )
        return Response(SubmissionSerializer(submission).data, status=200)


class SubmissionSubmitView(APIView):
    def post(self, request: Request, submission_id: str) -> Response:
        tenant_id = _tenant_id(request)
        try:
            parsed_id = UUID(submission_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_uuid"}, status=404)

        submission = Submission.objects.filter(id=parsed_id, tenant_id=tenant_id).first()
        if not submission:
            return Response({"code": "not_found"}, status=404)

        try:
            SubmissionStateMachine.submit(submission)
        except ValidationError as e:
            return Response({"code": "invalid_transition", "detail": str(e)}, status=409)

        return Response(SubmissionSerializer(submission).data, status=200)


class MentorReviewQueueView(APIView):
    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        state = request.query_params.get("state")
        qs = Submission.objects.filter(tenant_id=tenant_id)
        if state:
            qs = qs.filter(state=state)
        else:
            qs = qs.filter(state__in=["submitted", "under_review", "reviewed"])

        submissions = qs.select_related("assignment", "assignment__lesson").order_by(
            "-submitted_at", "-created_at"
        )
        return Response({"results": MentorSubmissionQueueSerializer(submissions, many=True).data})


class MentorSubmissionDetailView(APIView):
    def get(self, request: Request, submission_id: str) -> Response:
        tenant_id = _tenant_id(request)
        try:
            parsed_id = UUID(submission_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_uuid"}, status=404)

        submission = (
            Submission.objects.filter(id=parsed_id, tenant_id=tenant_id)
            .select_related("assignment", "assignment__lesson")
            .first()
        )
        if not submission:
            return Response({"code": "not_found"}, status=404)

        return Response(MentorSubmissionQueueSerializer(submission).data)


class MentorStartReviewView(APIView):
    def post(self, request: Request, submission_id: str) -> Response:
        tenant_id = _tenant_id(request)
        try:
            parsed_id = UUID(submission_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_uuid"}, status=404)

        submission = Submission.objects.filter(id=parsed_id, tenant_id=tenant_id).first()
        if not submission:
            return Response({"code": "not_found"}, status=404)

        try:
            SubmissionStateMachine.start_review(submission)
        except ValidationError as e:
            return Response({"code": "invalid_transition", "detail": str(e)}, status=409)

        return Response(MentorSubmissionQueueSerializer(submission).data, status=200)


class MentorCompleteReviewView(APIView):
    def post(self, request: Request, submission_id: str) -> Response:
        tenant_id = _tenant_id(request)
        try:
            parsed_id = UUID(submission_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_uuid"}, status=404)

        submission = Submission.objects.filter(id=parsed_id, tenant_id=tenant_id).first()
        if not submission:
            return Response({"code": "not_found"}, status=404)

        mentor_id = request.data.get("mentor_id")
        feedback_content = request.data.get("feedback", "")
        if not mentor_id:
            return Response({"code": "mentor_id_required"}, status=400)

        try:
            parsed_mentor_id = UUID(str(mentor_id))
        except (ValueError, TypeError):
            return Response({"code": "invalid_mentor_id"}, status=400)

        try:
            feedback = SubmissionStateMachine.complete_review(
                submission=submission,
                mentor_id=parsed_mentor_id,
                feedback_content=feedback_content,
            )
        except ValidationError as e:
            return Response({"code": "invalid_transition", "detail": str(e)}, status=409)

        return Response(FeedbackSerializer(feedback).data, status=200)


class StudentFeedbackView(APIView):
    def get(self, request: Request, submission_id: str) -> Response:
        tenant_id = _tenant_id(request)
        try:
            parsed_id = UUID(submission_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_uuid"}, status=404)

        submission = Submission.objects.filter(id=parsed_id, tenant_id=tenant_id).first()
        if not submission:
            return Response({"code": "not_found"}, status=404)

        feedbacks = Feedback.objects.filter(submission=submission, tenant_id=tenant_id).order_by(
            "-created_at"
        )
        return Response({"results": FeedbackSerializer(feedbacks, many=True).data})


# =========================================================================
# VS3 TRACK A: PARENT EXPERIENCE API VIEWS
# =========================================================================


class ParentStudentSummaryView(APIView):
    def get(self, request: Request, student_id: str) -> Response:
        tenant_request = cast(_TenantRequest, request)
        tenant = tenant_request.tenant
        role = _get_membership_role(request)

        # Authorization: Parent/Guardian or Admin/Owner only. Learner/Mentor denied.
        if role not in ("guardian", "admin", "owner"):
            return Response({"code": "forbidden"}, status=403)

        try:
            parsed_student_id = UUID(student_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_student_id"}, status=400)

        # Fail closed if student has no presence or is in another tenant
        has_tenant_activity = (
            Progress.objects.filter(tenant=tenant, student_id=parsed_student_id).exists()
            or Submission.objects.filter(tenant=tenant, student_id=parsed_student_id).exists()
        )
        if not has_tenant_activity:
            return Response({"code": "student_not_found"}, status=404)

        summary_data = ParentLearningSummaryService.get_summary_for_student(
            tenant=tenant, student_id=parsed_student_id
        )
        return Response(ParentStudentSummarySerializer(summary_data).data, status=200)


class ParentStudentProgressListView(APIView):
    def get(self, request: Request, student_id: str) -> Response:
        tenant_request = cast(_TenantRequest, request)
        tenant = tenant_request.tenant
        role = _get_membership_role(request)

        if role not in ("guardian", "admin", "owner"):
            return Response({"code": "forbidden"}, status=403)

        try:
            parsed_student_id = UUID(student_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_student_id"}, status=400)

        progresses = (
            Progress.objects.filter(tenant=tenant, student_id=parsed_student_id)
            .select_related("lesson")
            .order_by("-completed_at", "lesson__position")
        )
        return Response({"results": ProgressSerializer(progresses, many=True).data})


class ParentStudentFeedbackListView(APIView):
    def get(self, request: Request, student_id: str) -> Response:
        tenant_request = cast(_TenantRequest, request)
        tenant = tenant_request.tenant
        role = _get_membership_role(request)

        if role not in ("guardian", "admin", "owner"):
            return Response({"code": "forbidden"}, status=403)

        try:
            parsed_student_id = UUID(student_id)
        except (ValueError, TypeError):
            return Response({"code": "invalid_student_id"}, status=400)

        feedbacks = (
            Feedback.objects.filter(tenant=tenant, submission__student_id=parsed_student_id)
            .select_related("submission", "submission__assignment")
            .order_by("-created_at")
        )
        return Response({"results": FeedbackSerializer(feedbacks, many=True).data})


# =========================================================================
# VS3 TRACK B: ADMIN LEARNING OPERATIONS API VIEWS
# =========================================================================


class AdminLearningCurriculumView(APIView):
    def get(self, request: Request) -> Response:
        tenant_request = cast(_TenantRequest, request)
        tenant = tenant_request.tenant
        role = _get_membership_role(request)

        if role not in ("admin", "owner"):
            return Response({"code": "forbidden"}, status=403)

        paths = LearningPath.objects.filter(tenant=tenant).order_by("code")
        courses = Course.objects.filter(tenant=tenant).order_by("code")
        modules = Module.objects.filter(tenant=tenant).order_by("position")
        lessons = Lesson.objects.filter(tenant=tenant).order_by("position")
        assignments = Assignment.objects.filter(tenant=tenant).order_by("code")

        return Response(
            {
                "paths": LearningPathSerializer(paths, many=True).data,
                "courses": CourseSerializer(courses, many=True).data,
                "modules": ModuleSerializer(modules, many=True).data,
                "lessons": LessonSerializer(lessons, many=True).data,
                "assignments": AssignmentSerializer(assignments, many=True).data,
            }
        )

    def post(self, request: Request) -> Response:
        tenant_request = cast(_TenantRequest, request)
        tenant = tenant_request.tenant
        role = _get_membership_role(request)

        if role not in ("admin", "owner"):
            return Response({"code": "forbidden"}, status=403)

        entity_type = request.data.get("type")
        code = request.data.get("code")
        title = request.data.get("title")

        if not entity_type or not code or not title:
            return Response({"code": "invalid_parameters"}, status=400)

        if entity_type == "course":
            lp_id = request.data.get("learning_path_id")
            lp = LearningPath.objects.filter(id=lp_id, tenant=tenant).first() if lp_id else None
            course = Course.objects.create(
                tenant=tenant,
                learning_path=lp,
                code=code,
                title=title,
                state=PublicationState.DRAFT,
            )
            return Response(CourseSerializer(course).data, status=201)

        elif entity_type == "lesson":
            course_id = request.data.get("course_id")
            try:
                parsed_cid = UUID(str(course_id))
            except (ValueError, TypeError):
                return Response({"code": "invalid_course_id"}, status=400)
            course = Course.objects.filter(id=parsed_cid, tenant=tenant).first()
            if not course:
                return Response({"code": "course_not_found"}, status=404)
            pos = int(request.data.get("position", 1))
            lesson = Lesson.objects.create(
                tenant=tenant,
                course=course,
                code=code,
                title=title,
                position=pos,
                state=PublicationState.DRAFT,
            )
            return Response(LessonSerializer(lesson).data, status=201)

        elif entity_type == "assignment":
            lesson_id = request.data.get("lesson_id")
            try:
                parsed_lid = UUID(str(lesson_id))
            except (ValueError, TypeError):
                return Response({"code": "invalid_lesson_id"}, status=400)
            lesson = Lesson.objects.filter(id=parsed_lid, tenant=tenant).first()
            if not lesson:
                return Response({"code": "lesson_not_found"}, status=404)
            assignment = Assignment.objects.create(
                tenant=tenant,
                lesson=lesson,
                code=code,
                title=title,
                state=AssignmentState.DRAFT,
            )
            return Response(AssignmentSerializer(assignment).data, status=201)

        return Response({"code": "unsupported_entity_type"}, status=400)


class AdminLearningTransitionView(APIView):
    def post(self, request: Request) -> Response:
        tenant_request = cast(_TenantRequest, request)
        tenant = tenant_request.tenant
        role = _get_membership_role(request)

        if role not in ("admin", "owner"):
            return Response({"code": "forbidden"}, status=403)

        entity_type = request.data.get("type")
        entity_id = request.data.get("id")
        action = request.data.get("action")  # "publish", "archive"

        if not entity_type or not entity_id or not action:
            return Response({"code": "invalid_parameters"}, status=400)

        try:
            parsed_id = UUID(str(entity_id))
        except (ValueError, TypeError):
            return Response({"code": "invalid_id"}, status=400)

        if action not in ("publish", "archive"):
            return Response({"code": "invalid_action"}, status=400)

        if entity_type == "course":
            course = Course.objects.filter(id=parsed_id, tenant=tenant).first()
            if not course:
                return Response({"code": "not_found"}, status=404)
            target = (
                PublicationState.PUBLISHED if action == "publish" else PublicationState.ARCHIVED
            )
            try:
                ContentStateMachine.transition(course, target)
            except ValidationError as e:
                return Response({"code": "invalid_transition", "detail": str(e)}, status=409)
            return Response(CourseSerializer(course).data, status=200)

        elif entity_type == "lesson":
            lesson = Lesson.objects.filter(id=parsed_id, tenant=tenant).first()
            if not lesson:
                return Response({"code": "not_found"}, status=404)
            target = (
                PublicationState.PUBLISHED if action == "publish" else PublicationState.ARCHIVED
            )
            try:
                ContentStateMachine.transition(lesson, target)
            except ValidationError as e:
                return Response({"code": "invalid_transition", "detail": str(e)}, status=409)
            return Response(LessonSerializer(lesson).data, status=200)

        elif entity_type == "assignment":
            assignment = Assignment.objects.filter(id=parsed_id, tenant=tenant).first()
            if not assignment:
                return Response({"code": "not_found"}, status=404)
            target = AssignmentState.PUBLISHED if action == "publish" else AssignmentState.CLOSED
            try:
                AssignmentStateMachine.transition(assignment, target)
            except ValidationError as e:
                return Response({"code": "invalid_transition", "detail": str(e)}, status=409)
            return Response(AssignmentSerializer(assignment).data, status=200)

        return Response({"code": "unsupported_entity_type"}, status=400)


@require_GET
def course_list(request: HttpRequest) -> Response:
    return CourseListView.as_view()(request)


@require_GET
def course_lesson_list(request: HttpRequest, course_id: str) -> Response:
    return CourseLessonListView.as_view()(request, course_id=course_id)


class SyntheticMediaAttachmentView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request, lesson_id: str) -> Response:
        tr = cast(_TenantRequest, request)
        tenant = getattr(tr, "tenant", None)
        if not tenant or not hasattr(tenant, "id"):
            return Response({"code": "tenant_required"}, status=403)
        try:
            parsed_lesson_id = UUID(lesson_id)
        except ValueError:
            return Response({"code": "invalid_id"}, status=400)

        lesson = Lesson.objects.filter(id=parsed_lesson_id, tenant=tenant).first()
        if not lesson:
            return Response({"code": "not_found"}, status=404)

        attachments = SyntheticMediaAttachment.objects.filter(lesson=lesson, tenant=tenant)
        serializer = SyntheticMediaAttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=200)

    def post(self, request: Request, lesson_id: str) -> Response:
        raw_req = getattr(request, "_request", None)
        tenant = getattr(request, "tenant", None) or getattr(raw_req, "tenant", None)
        membership = getattr(request, "tenant_membership", None) or getattr(
            raw_req, "tenant_membership", None
        )
        if (
            not tenant
            or not hasattr(tenant, "id")
            or not membership
            or getattr(membership, "role", None) != "admin"
        ):
            return Response({"code": "forbidden"}, status=403)

        try:
            parsed_lesson_id = UUID(lesson_id)
        except ValueError:
            return Response({"code": "invalid_id"}, status=400)

        lesson = Lesson.objects.filter(id=parsed_lesson_id, tenant=tenant).first()
        if not lesson:
            return Response({"code": "not_found"}, status=404)

        data = request.data.copy()
        data["lesson"] = str(lesson.id)

        # Enforce G4 Storage Key Tenant Prefix: {tenant_id}/media/
        storage_key = data.get("storage_key", "")
        expected_prefix = f"{tenant.id}/media/"
        if not storage_key.startswith(expected_prefix):
            data["storage_key"] = f"{expected_prefix}{storage_key.lstrip('/')}"

        serializer = SyntheticMediaAttachmentSerializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                instance = serializer.save(tenant=tenant)
                event = LearningDomainEvents.media_attached(
                    tenant_id=tenant.id,
                    media_id=instance.id,
                    lesson_id=lesson.id,
                    title=instance.title,
                    storage_key=instance.storage_key,
                )
                append_outbox_event(
                    topic=event.event_type,
                    aggregate_type="synthetic_media_attachment",
                    aggregate_id=str(instance.id),
                    payload=event.payload,
                    tenant_id=tenant.id,
                )
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class StudentCourseAnalyticsView(APIView):
    """
    Student learning analytics projection endpoint.
    Only allows access to the requesting student's own aggregates.
    """

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if (
            not tenant
            or not membership
            or not getattr(membership, "is_active", False)
            or getattr(membership, "role", None) != "student"
        ):
            return Response({"code": "forbidden"}, status=403)

        student_id = request.user.id
        aggregates = CourseProgressAggregate.objects.filter(
            tenant=tenant, student_id=student_id
        ).select_related("course")

        serializer = CourseProgressAggregateSerializer(aggregates, many=True)
        return Response(serializer.data, status=200)


class MentorMetricsView(APIView):
    """
    Mentor assignment submission queue metrics projection endpoint.
    """

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if (
            not tenant
            or not membership
            or not getattr(membership, "is_active", False)
            or getattr(membership, "role", None) not in ("mentor", "admin")
        ):
            return Response({"code": "forbidden"}, status=403)

        metrics = AssignmentSubmissionMetrics.objects.filter(tenant=tenant).select_related(
            "assignment"
        )

        serializer = AssignmentSubmissionMetricsSerializer(metrics, many=True)
        return Response(serializer.data, status=200)


class RoleActivityFeedView(APIView):
    """
    Role-specific activity feed projection endpoint.
    Strictly Zero-PII and bounded to requesting role and tenant.
    """

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        role = getattr(membership, "role", None)
        user_id = request.user.id

        qs = RoleActivityFeed.objects.filter(tenant=tenant)
        if role == "student":
            qs = qs.filter(target_role=RoleActivityFeed.ActivityRole.STUDENT, user_id=user_id)
        elif role == "mentor":
            qs = qs.filter(target_role=RoleActivityFeed.ActivityRole.MENTOR)
        elif role == "parent":
            qs = qs.filter(target_role=RoleActivityFeed.ActivityRole.PARENT)
        elif role == "admin":
            qs = qs.all()
        else:
            return Response({"code": "forbidden"}, status=403)

        qs = qs.order_by("-occurred_at")[:50]
        serializer = RoleActivityFeedSerializer(qs, many=True)
        return Response(serializer.data, status=200)


class NotificationListView(APIView):
    """
    List user notifications partitioned by role, strictly Zero-PII and tenant-isolated.
    """

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        role = getattr(membership, "role", None)
        user_id = request.user.id

        qs = NotificationItem.objects.filter(tenant=tenant, user_id=user_id, role=role).order_by(
            "-created_at"
        )[:50]

        serializer = NotificationItemSerializer(qs, many=True)
        unread_count = NotificationItem.objects.filter(
            tenant=tenant, user_id=user_id, role=role, read_at__isnull=True
        ).count()

        return Response(
            {
                "unread_count": unread_count,
                "notifications": serializer.data,
            },
            status=200,
        )


class NotificationMarkReadView(APIView):
    """
    Marks a single notification or all user notifications as read.
    """

    def post(self, request: Request, notification_id: str | None = None) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        role = getattr(membership, "role", None)
        user_id = request.user.id
        from django.utils import timezone
        now = timezone.now()

        if notification_id == "all":
            updated = NotificationItem.objects.filter(
                tenant=tenant,
                user_id=user_id,
                role=role,
                read_at__isnull=True,
            ).update(read_at=now)
            return Response({"marked_count": updated}, status=200)

        item = NotificationItem.objects.filter(
            tenant=tenant,
            user_id=user_id,
            id=notification_id,
        ).first()

        if not item:
            return Response({"code": "not_found"}, status=404)

        if not item.read_at:
            item.read_at = now
            item.save(update_fields=["read_at"])

        return Response(NotificationItemSerializer(item).data, status=200)


class StudentGamificationView(APIView):
    """
    Student Gamification & Progression View.
    Returns authoritative profile, earned badges, and available badge definitions.
    Strictly Zero-PII, tenant-bounded.
    """

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if (
            not tenant
            or not membership
            or not getattr(membership, "is_active", False)
            or getattr(membership, "role", None) != "student"
        ):
            return Response({"code": "forbidden"}, status=403)

        student_id = request.user.id

        from .gamification import GamificationEngine
        GamificationEngine.ensure_default_badges()

        profile, _ = StudentProgressionProfile.objects.get_or_create(
            tenant=tenant,
            student_id=student_id,
            defaults={"current_streak_days": 0, "longest_streak_days": 0, "total_xp": 0, "level": 1},
        )

        badges = StudentBadgeAward.objects.filter(
            tenant=tenant, student_id=student_id
        ).select_related("badge").order_by("-awarded_at")

        available_badges = BadgeDefinition.objects.all().order_by("threshold")

        from .serializers import (
            BadgeDefinitionSerializer,
            StudentBadgeAwardSerializer,
            StudentProgressionProfileSerializer,
        )

        return Response(
            {
                "profile": StudentProgressionProfileSerializer(profile).data,
                "badges": StudentBadgeAwardSerializer(badges, many=True).data,
                "available_badges": BadgeDefinitionSerializer(available_badges, many=True).data,
            },
            status=200,
        )


class StudentEnrollmentView(APIView):
    """
    GET /api/v1/learning/student/enrollments/
    Lists current student enrollments and available courses.
    Role-aware: Student only.
    """

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if (
            not tenant
            or not membership
            or not getattr(membership, "is_active", False)
            or getattr(membership, "role", None) != "student"
        ):
            return Response({"code": "forbidden"}, status=403)

        student_id = request.user.id
        from .models import CourseEnrollment
        from .serializers import CourseEnrollmentSerializer

        enrollments = CourseEnrollment.objects.filter(
            tenant=tenant,
            student_id=student_id,
        ).select_related("course", "cohort").order_by("-enrolled_at")

        return Response(
            {"enrollments": CourseEnrollmentSerializer(enrollments, many=True).data},
            status=200,
        )


class StudentEnrollActionView(APIView):
    """
    POST /api/v1/learning/student/enroll/
    Performs atomic enrollment with select_for_update cohort capacity locks.
    Role-aware: Student only.
    """

    def post(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if (
            not tenant
            or not membership
            or not getattr(membership, "is_active", False)
            or getattr(membership, "role", None) != "student"
        ):
            return Response({"code": "forbidden"}, status=403)

        from .serializers import StudentEnrollRequestSerializer, CourseEnrollmentSerializer
        from .enrollment import (
            EnrollmentEngine,
            CohortCapacityExceededError,
            PrerequisiteNotMetError,
            CohortMandatoryError,
        )

        serializer = StudentEnrollRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"code": "invalid_input", "errors": serializer.errors}, status=400)

        course_id = serializer.validated_data["course_id"]
        cohort_id = serializer.validated_data.get("cohort_id")
        idempotency_key = serializer.validated_data.get("idempotency_key")
        student_id = request.user.id

        try:
            enrollment = EnrollmentEngine.enroll_student(
                tenant_id=tenant.id,
                student_id=student_id,
                course_id=course_id,
                cohort_id=cohort_id,
                idempotency_key=idempotency_key,
            )
            return Response(
                {"enrollment": CourseEnrollmentSerializer(enrollment).data},
                status=201,
            )
        except CohortCapacityExceededError as e:
            return Response({"code": "cohort_capacity_exceeded", "detail": str(e)}, status=409)
        except PrerequisiteNotMetError as e:
            return Response({"code": "prerequisite_not_met", "detail": str(e)}, status=400)
        except CohortMandatoryError as e:
            return Response({"code": "cohort_mandatory", "detail": str(e)}, status=400)
        except ValidationError as e:
            return Response({"code": "validation_error", "detail": str(e)}, status=400)


class CohortListView(APIView):
    """
    GET /api/v1/learning/courses/<course_id>/cohorts/
    Lists available cohorts for a course with live occupied capacity.
    """

    def get(self, request: Request, course_id: UUID) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        from .models import Cohort
        from .serializers import CohortSerializer

        cohorts = Cohort.objects.filter(
            tenant=tenant,
            course_id=course_id,
            is_active=True,
        ).order_by("created_at")

        return Response(
            {"cohorts": CohortSerializer(cohorts, many=True).data},
            status=200,
        )


class CodeAssessmentListView(APIView):
    """
    GET /api/v1/learning/lessons/<lesson_id>/assessments/
    Returns active code assessment details for a lesson.
    """

    def get(self, request: Request, lesson_id: UUID) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        from .models import CodeAssessment
        from .serializers import CodeAssessmentSerializer

        assessments = CodeAssessment.objects.filter(
            tenant=tenant,
            lesson_id=lesson_id,
            is_active=True,
        )
        return Response(
            {"assessments": CodeAssessmentSerializer(assessments, many=True, context={"request": request}).data},
            status=200,
        )


class CodePlaygroundRunView(APIView):
    """
    POST /api/v1/learning/playground/run/
    Executes code in ephemeral isolated playground sandbox without grade persistence.
    """

    def post(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        from .assessments import AssessmentEngine
        from .serializers import CodePlaygroundRunRequestSerializer

        serializer = CodePlaygroundRunRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        code = serializer.validated_data["code"]
        language = serializer.validated_data.get("language", "python")

        res = AssessmentEngine.run_playground_dryrun(
            tenant_id=tenant.id,
            user_id=membership.user_id,
            code=code,
            language=language,
        )
        return Response(res, status=200)


class CodeAssessmentSubmitView(APIView):
    """
    POST /api/v1/learning/assessments/<assessment_id>/submit/
    Submits code for authoritative evaluation against assessment testcases.
    """

    def post(self, request: Request, assessment_id: UUID) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        from .assessments import AssessmentEngine, ConcurrencyLockError
        from .serializers import (
            AssessmentResultSerializer,
            CodeExecutionRunSerializer,
            CodeSubmitAssessmentRequestSerializer,
        )

        serializer = CodeSubmitAssessmentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        code = serializer.validated_data["code"]
        idempotency_key = serializer.validated_data.get("idempotency_key")

        try:
            run, result = AssessmentEngine.submit_and_evaluate_assessment(
                tenant_id=tenant.id,
                student_id=membership.user_id,
                assessment_id=assessment_id,
                code=code,
                idempotency_key=idempotency_key,
            )
            return Response(
                {
                    "run": CodeExecutionRunSerializer(run).data,
                    "result": AssessmentResultSerializer(result).data,
                },
                status=200,
            )
        except ConcurrencyLockError as e:
            return Response({"code": "concurrency_lock", "detail": str(e)}, status=409)
        except ValidationError as e:
            return Response({"code": "validation_error", "detail": str(e)}, status=400)


class AssessmentResultListView(APIView):
    """
    GET /api/v1/learning/student/assessments/results/
    Returns student's final assessment results.
    """

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        from .models import AssessmentResult
        from .serializers import AssessmentResultSerializer

        results = AssessmentResult.objects.filter(
            tenant=tenant,
            student_id=membership.user_id,
        ).order_by("-created_at")

        return Response(
            {"results": AssessmentResultSerializer(results, many=True).data},
            status=200,
        )



from .models import (
    CertificateTemplate,
    CourseCertificate,
    CertificateVerificationRecord,
)
from .serializers import (
    CertificateTemplateSerializer,
    CourseCertificateSerializer,
    CertificateVerificationRecordSerializer,
    LearningAchievementTimelineItemSerializer,
)
from .certificates import (
    CertificateIssuanceService,
    CertificateVerificationService,
)


class StudentCertificateListView(APIView):
    """
    GET /api/v1/learning/student/certificates/
    """
    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        certs = CourseCertificate.objects.filter(
            tenant=tenant,
            student_id=membership.user_id,
        ).order_by("-issued_at")

        return Response(
            {"certificates": CourseCertificateSerializer(certs, many=True).data},
            status=200,
        )


class StudentCertificateDetailView(APIView):
    """
    GET /api/v1/learning/student/certificates/{id}/
    """
    def get(self, request: Request, certificate_id: str) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        cert = CourseCertificate.objects.filter(
            tenant=tenant,
            id=certificate_id,
            student_id=membership.user_id,
        ).first()
        if not cert:
            return Response({"code": "not_found"}, status=404)

        return Response(
            {"certificate": CourseCertificateSerializer(cert).data},
            status=200,
        )


class PublicCertificateVerificationView(APIView):
    """
    GET /api/v1/learning/certificates/verify/?number=CERT-XXX
    Zero PII, timing-safe verification.
    """
    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response({"code": "tenant_required"}, status=400)

        certificate_number = request.query_params.get("number")
        if not certificate_number:
            return Response({"code": "number_required", "detail": "Certificate number is required."}, status=400)

        role = "anonymous"
        membership = getattr(request, "membership", None)
        if membership and getattr(membership, "role", None):
            role = str(membership.role)

        result = CertificateVerificationService.verify_by_number(
            tenant=tenant,
            certificate_number=certificate_number,
            queried_by_role=role,
        )
        return Response(result, status=200 if result["is_valid"] else 404)


class StudentAchievementTimelineView(APIView):
    """
    GET /api/v1/learning/student/achievements/
    Chronological milestone events for student.
    """
    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "membership", None)
        if not tenant or not membership or not getattr(membership, "is_active", False):
            return Response({"code": "forbidden"}, status=403)

        student_id = membership.user_id
        timeline_items = []

        # 1. Issued Certificates
        certs = CourseCertificate.objects.filter(
            tenant=tenant,
            student_id=student_id,
        ).order_by("-issued_at")
        for c in certs:
            timeline_items.append({
                "id": f"cert-{c.id}",
                "event_type": "CERTIFICATE_ISSUED",
                "title": f"گواهی پایان دوره: {c.course.title}",
                "description": f"شماره گواهی: {c.certificate_number} با نمره نهایی {c.final_score}",
                "occurred_at": c.issued_at,
                "metadata": {"certificate_number": c.certificate_number, "score": str(c.final_score)},
            })

        # 2. Badges
        from .models import StudentBadgeAward
        badges = StudentBadgeAward.objects.filter(
            tenant=tenant,
            student_id=student_id,
        ).select_related("badge_definition").order_by("-awarded_at")
        for b in badges:
            timeline_items.append({
                "id": f"badge-{b.id}",
                "event_type": "BADGE_AWARDED",
                "title": f"کسب نشان: {b.badge_definition.title}",
                "description": b.badge_definition.description or "",
                "occurred_at": b.awarded_at,
                "metadata": {"badge_slug": b.badge_definition.slug},
            })

        # 3. Passed Submissions
        subs = Submission.objects.filter(
            tenant=tenant,
            student_id=student_id,
            state="reviewed",
        ).select_related("assignment").order_by("-reviewed_at")
        for s in subs:
            timeline_items.append({
                "id": f"sub-{s.id}",
                "event_type": "ASSIGNMENT_REVIEWED",
                "title": f"تأیید تمرین: {s.assignment.title}",
                "description": f"نمره کسب‌شده: {s.score or '100.00'}",
                "occurred_at": s.reviewed_at or s.submitted_at,
                "metadata": {"assignment_id": str(s.assignment_id)},
            })

        # Sort combined timeline DESC
        timeline_items.sort(key=lambda x: x["occurred_at"], reverse=True)

        return Response(
            {"timeline": LearningAchievementTimelineItemSerializer(timeline_items[:50], many=True).data},
            status=200,
        )
