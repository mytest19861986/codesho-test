from __future__ import annotations

from typing import Protocol, cast
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
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
    if hasattr(request, "tenant"):
        return request.tenant.id
    if hasattr(request, "tenant_id"):
        return request.tenant_id
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


class MentorCohortAnalyticsView(APIView):
    """
    GET /api/v1/learning/mentor/cohorts/<cohort_id>/analytics/
    Returns presentation-only aggregated analytics for a supervised cohort.
    Enforces Pattern A: returns 404 for unassigned cohorts.
    """

    def get(self, request, cohort_id):
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response({"detail": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND)

        user = getattr(request, "user", None)
        mentor_id = getattr(request, "user_id", None) or (str(user.id) if user and user.is_authenticated else None)

        if not mentor_id:
            # Fallback to test/anonymous mentor header or fail closed
            mentor_id = request.headers.get("X-Mentor-Id")
            if not mentor_id:
                return Response({"detail": "Mentor identification required."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = bool(user and (user.is_staff or getattr(user, "is_tenant_admin", False)))

        from modules.learning.supervision import CohortSupervisionAccessService, CohortSupervisionService
        from modules.learning.models import CohortProgressAggregate, Cohort

        try:
            cohort = CohortSupervisionAccessService.check_access(
                tenant_id=str(tenant.id),
                mentor_id=str(mentor_id),
                cohort_id=str(cohort_id),
                is_admin=is_admin,
            )
        except Cohort.DoesNotExist:
            return Response({"detail": "Cohort not found or unassigned."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch or compute latest aggregate projection
        agg = CohortProgressAggregate.objects.filter(
            tenant=tenant,
            cohort=cohort,
        ).first()

        if not agg:
            agg = CohortSupervisionService.refresh_cohort_progress_aggregate(
                tenant_id=str(tenant.id),
                cohort_id=str(cohort.id),
            )

        return Response({
            "cohort_id": str(cohort.id),
            "cohort_code": cohort.code,
            "cohort_title": cohort.title,
            "total_enrolled": agg.total_enrolled,
            "active_students": agg.active_students,
            "completed_students": agg.completed_students,
            "average_progress_percentage": str(agg.average_progress_percentage),
            "average_assessment_score": str(agg.average_assessment_score),
            "completion_rate": str(agg.completion_rate),
            "as_of": agg.updated_at.isoformat(),
        }, status=status.HTTP_200_OK)


class MentorCohortAlertsView(APIView):
    """
    GET /api/v1/learning/mentor/cohorts/<cohort_id>/alerts/
    POST /api/v1/learning/mentor/cohorts/<cohort_id>/alerts/<alert_id>/transition/
    Supervision alerts query and FSM lifecycle management.
    """

    def get(self, request, cohort_id):
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response({"detail": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND)

        user = getattr(request, "user", None)
        mentor_id = getattr(request, "user_id", None) or (str(user.id) if user and user.is_authenticated else None)
        if not mentor_id:
            mentor_id = request.headers.get("X-Mentor-Id")
            if not mentor_id:
                return Response({"detail": "Mentor identification required."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = bool(user and (user.is_staff or getattr(user, "is_tenant_admin", False)))

        from modules.learning.supervision import CohortSupervisionAccessService
        from modules.learning.models import StudentSupervisionAlert, Cohort

        try:
            cohort = CohortSupervisionAccessService.check_access(
                tenant_id=str(tenant.id),
                mentor_id=str(mentor_id),
                cohort_id=str(cohort_id),
                is_admin=is_admin,
            )
        except Cohort.DoesNotExist:
            return Response({"detail": "Cohort not found or unassigned."}, status=status.HTTP_404_NOT_FOUND)

        status_filter = request.query_params.get("status")
        qs = StudentSupervisionAlert.objects.filter(
            tenant=tenant,
            cohort=cohort,
        )
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        qs = qs.order_by("-created_at")

        data = [
            {
                "id": str(a.id),
                "student_id": str(a.student_id),
                "alert_type": a.alert_type,
                "severity": a.severity,
                "status": a.status,
                "details": a.details,
                "created_at": a.created_at.isoformat(),
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
            }
            for a in qs[:100]
        ]
        return Response({"alerts": data}, status=status.HTTP_200_OK)

    def post(self, request, cohort_id, alert_id=None):
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response({"detail": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND)

        user = getattr(request, "user", None)
        mentor_id = getattr(request, "user_id", None) or (str(user.id) if user and user.is_authenticated else None)
        if not mentor_id:
            mentor_id = request.headers.get("X-Mentor-Id")
            if not mentor_id:
                return Response({"detail": "Mentor identification required."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = bool(user and (user.is_staff or getattr(user, "is_tenant_admin", False)))

        from modules.learning.supervision import CohortSupervisionAccessService, CohortSupervisionService
        from modules.learning.models import Cohort, StudentSupervisionAlert

        try:
            cohort = CohortSupervisionAccessService.check_access(
                tenant_id=str(tenant.id),
                mentor_id=str(mentor_id),
                cohort_id=str(cohort_id),
                is_admin=is_admin,
            )
        except Cohort.DoesNotExist:
            return Response({"detail": "Cohort not found or unassigned."}, status=status.HTTP_404_NOT_FOUND)

        target_status = request.data.get("status")
        if not target_status:
            return Response({"detail": "target 'status' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            alert = CohortSupervisionService.transition_alert_status(
                tenant_id=str(tenant.id),
                alert_id=str(alert_id),
                target_status=target_status.upper(),
                actor_id=str(mentor_id),
            )
            return Response({
                "id": str(alert.id),
                "status": alert.status,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DiscussionThreadListCreateView(APIView):
    """
    List and create discussion threads within a cohort or lesson scope.
    Enforces child-safety visibility tiers: peers see ONLY approved threads.
    """

    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        cohort_id = request.query_params.get("cohort_id")
        lesson_id = request.query_params.get("lesson_id")

        if bool(cohort_id) == bool(lesson_id):
            return Response({"detail": "Exactly one of cohort_id or lesson_id must be provided."}, status=400)

        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        role = _get_membership_role(request) or "STUDENT"

        from modules.learning.models import DiscussionThread, DiscussionStatus
        from modules.learning.serializers import DiscussionThreadSerializer

        qs = DiscussionThread.objects.filter(tenant_id=tenant_id)
        if cohort_id:
            qs = qs.filter(cohort_id=cohort_id)
        else:
            qs = qs.filter(lesson_id=lesson_id)

        # Visibility filter based on role and author
        if role not in ["STAFF", "ADMIN", "MENTOR"]:
            if user_id:
                qs = qs.filter(models.Q(status=DiscussionStatus.APPROVED) | (models.Q(status=DiscussionStatus.PENDING) & models.Q(author_id=user_id)))
            else:
                qs = qs.filter(status=DiscussionStatus.APPROVED)

        qs = qs.order_by("-is_pinned", "-created_at")
        serializer = DiscussionThreadSerializer(qs, many=True)
        return Response(serializer.data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        role = _get_membership_role(request) or "STUDENT"
        cohort_id = request.data.get("cohort_id")
        lesson_id = request.data.get("lesson_id")
        title = request.data.get("title", "")
        body = request.data.get("body", "")

        from modules.learning.discussion_service import DiscussionService
        from modules.learning.serializers import DiscussionThreadSerializer
        from django.core.exceptions import PermissionDenied, ValidationError

        try:
            thread = DiscussionService.create_thread(
                tenant_id=tenant_id,
                author_id=user_id,
                role=role,
                title=title,
                body=body,
                cohort_id=cohort_id,
                lesson_id=lesson_id,
            )
            return Response(DiscussionThreadSerializer(thread).data, status=201)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)


class DiscussionThreadDetailView(APIView):
    """
    Retrieve single discussion thread and its hierarchical comments.
    """

    def get(self, request: Request, thread_id: str) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        role = _get_membership_role(request) or "STUDENT"

        from modules.learning.models import DiscussionThread, DiscussionComment, DiscussionStatus
        from modules.learning.serializers import DiscussionThreadSerializer, DiscussionCommentSerializer
        from modules.learning.discussion_service import DiscussionAccessPolicy

        thread = DiscussionThread.objects.filter(tenant_id=tenant_id, id=thread_id).first()
        if not thread:
            return Response({"detail": "Thread not found."}, status=404)

        if not DiscussionAccessPolicy.can_view_thread(thread, user_id, role):
            return Response({"detail": "Thread is pending review or not accessible."}, status=404)

        comments_qs = DiscussionComment.objects.filter(tenant_id=tenant_id, thread_id=thread.id)
        if role not in ["STAFF", "ADMIN", "MENTOR"]:
            if user_id:
                comments_qs = comments_qs.filter(
                    models.Q(status=DiscussionStatus.APPROVED) | (models.Q(status=DiscussionStatus.PENDING) & models.Q(author_id=user_id))
                )
            else:
                comments_qs = comments_qs.filter(status=DiscussionStatus.APPROVED)

        comments_qs = comments_qs.order_by("created_at")

        thread_data = DiscussionThreadSerializer(thread).data
        thread_data["comments"] = DiscussionCommentSerializer(comments_qs, many=True).data
        return Response(thread_data, status=200)


class DiscussionCommentCreateView(APIView):
    """
    Add a comment or reply to an existing discussion thread.
    """

    def post(self, request: Request, thread_id: str) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        role = _get_membership_role(request) or "STUDENT"
        body = request.data.get("body", "")
        parent_id = request.data.get("parent_id")

        from modules.learning.discussion_service import DiscussionService
        from modules.learning.serializers import DiscussionCommentSerializer
        from django.core.exceptions import PermissionDenied, ValidationError

        try:
            comment = DiscussionService.create_comment(
                tenant_id=tenant_id,
                author_id=user_id,
                role=role,
                thread_id=thread_id,
                body=body,
                parent_id=parent_id,
            )
            return Response(DiscussionCommentSerializer(comment).data, status=201)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)


class DiscussionCommentEndorseView(APIView):
    """
    Mentor/Staff endorsement for high-quality community answers.
    """

    def post(self, request: Request, comment_id: str) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        role = _get_membership_role(request) or "STUDENT"

        from modules.learning.discussion_service import DiscussionService
        from modules.learning.serializers import DiscussionCommentSerializer
        from django.core.exceptions import PermissionDenied, ValidationError

        try:
            comment = DiscussionService.endorse_comment(
                tenant_id=tenant_id,
                comment_id=comment_id,
                mentor_id=user_id,
                role=role,
            )
            return Response(DiscussionCommentSerializer(comment).data, status=200)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)


class DiscussionThreadPinView(APIView):
    """
    Mentor/Staff toggle for pinning threads to top.
    """

    def post(self, request: Request, thread_id: str) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        role = _get_membership_role(request) or "STUDENT"
        is_pinned = bool(request.data.get("is_pinned", True))

        from modules.learning.discussion_service import DiscussionService
        from modules.learning.serializers import DiscussionThreadSerializer
        from django.core.exceptions import PermissionDenied, ValidationError

        try:
            thread = DiscussionService.pin_thread(
                tenant_id=tenant_id,
                thread_id=thread_id,
                user_id=user_id,
                role=role,
                is_pinned=is_pinned,
            )
            return Response(DiscussionThreadSerializer(thread).data, status=200)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)


class DiscussionModerationActionView(APIView):
    """
    Perform moderation on threads or comments (Approve, Flag, Remove, Restore).
    Creates immutable audit trail record.
    """

    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        role = _get_membership_role(request) or "STUDENT"
        if role not in ["MENTOR", "STAFF", "ADMIN"]:
            return Response({"detail": "Only staff and mentors can perform moderation."}, status=403)

        thread_id = request.data.get("thread_id")
        comment_id = request.data.get("comment_id")
        action = request.data.get("action")
        reason = request.data.get("reason", "Standard moderation review")
        note = request.data.get("note", "")

        from modules.learning.discussion_service import DiscussionService
        from modules.learning.models import ModerationActionType
        from django.core.exceptions import PermissionDenied, ValidationError

        try:
            if thread_id:
                DiscussionService.moderate_thread(
                    tenant_id=tenant_id,
                    thread_id=thread_id,
                    action=ModerationActionType(action),
                    performed_by=user_id,
                    reason=reason,
                    note=note,
                )
            elif comment_id:
                DiscussionService.moderate_comment(
                    tenant_id=tenant_id,
                    comment_id=comment_id,
                    action=ModerationActionType(action),
                    performed_by=user_id,
                    reason=reason,
                    note=note,
                )
            else:
                return Response({"detail": "Either thread_id or comment_id must be provided."}, status=400)

            return Response({"status": "SUCCESS", "action": action}, status=200)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)
        except (ValidationError, ValueError) as e:
            return Response({"detail": str(e)}, status=400)


# =============================================================================
# Phase 3 VS11: Adaptive Progression and Personalization Views
# =============================================================================

class StudentProfileView(APIView):
    """
    GET /api/v1/learning/personalization/profile/
    POST /api/v1/learning/personalization/profile/rebuild/
    Retrieves or triggers deterministic rebuild of the student's learning profile.
    """

    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        from modules.learning.models import StudentLearningProfile
        from modules.learning.serializers import StudentLearningProfileSerializer
        from modules.learning.personalization_service import PersonalizationService

        profile = StudentLearningProfile.objects.filter(tenant_id=tenant_id, student_id=user_id).first()
        if not profile:
            profile = PersonalizationService.rebuild_student_profile(tenant_id=tenant_id, student_id=user_id)

        serializer = StudentLearningProfileSerializer(profile)
        return Response(serializer.data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        from modules.learning.personalization_service import PersonalizationService
        from modules.learning.serializers import StudentLearningProfileSerializer

        profile = PersonalizationService.rebuild_student_profile(tenant_id=tenant_id, student_id=user_id)
        serializer = StudentLearningProfileSerializer(profile)
        return Response(serializer.data, status=200)


class RecommendationListView(APIView):
    """
    GET /api/v1/learning/personalization/recommendations/
    Returns active recommendations for the authenticated student.
    """

    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        from modules.learning.models import LearningRecommendation, RecommendationStatus
        from modules.learning.serializers import LearningRecommendationSerializer

        recs = LearningRecommendation.objects.filter(
            tenant_id=tenant_id,
            student_id=user_id,
            status__in=[RecommendationStatus.GENERATED, RecommendationStatus.VIEWED, RecommendationStatus.ACCEPTED],
        ).select_related("target_skill", "target_lesson", "target_course").order_by("priority", "-created_at")

        serializer = LearningRecommendationSerializer(recs, many=True)
        return Response(serializer.data, status=200)


class RecommendationActionView(APIView):
    """
    POST /api/v1/learning/personalization/recommendations/<uuid:recommendation_id>/action/
    Action: VIEWED, ACCEPTED, DISMISSED
    """

    def post(self, request: Request, recommendation_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        user = getattr(request, "user", None)
        user_id = getattr(request, "user_id", None) or (user.id if user and user.is_authenticated else None)
        if not user_id:
            return Response({"detail": "Authentication required."}, status=401)

        action = request.data.get("action")
        reason = request.data.get("reason", "")

        from modules.learning.models import LearningRecommendation, TransitionActorType
        from modules.learning.personalization_service import PersonalizationService
        from modules.learning.serializers import LearningRecommendationSerializer

        rec = LearningRecommendation.objects.filter(tenant_id=tenant_id, id=recommendation_id).first()
        if not rec:
            return Response({"detail": "Recommendation not found."}, status=404)
        if str(rec.student_id) != str(user_id):
            return Response({"detail": "Cannot modify recommendations belonging to another student."}, status=403)

        try:
            updated_rec = PersonalizationService.transition_recommendation(
                tenant_id=tenant_id,
                recommendation_id=recommendation_id,
                target_status=action,
                actor_id=user_id,
                actor_type=TransitionActorType.STUDENT,
                reason=reason,
            )
            serializer = LearningRecommendationSerializer(updated_rec)
            return Response(serializer.data, status=200)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)


class SkillGraphView(APIView):
    """
    GET /api/v1/learning/personalization/skills/
    Returns the active skill definitions and dependency edges for the tenant.
    """

    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        from modules.learning.models import SkillDefinition, SkillDependency
        from modules.learning.serializers import SkillDefinitionSerializer

        skills = SkillDefinition.objects.filter(tenant_id=tenant_id, is_active=True).order_by("category", "difficulty_level")
        deps = SkillDependency.objects.filter(tenant_id=tenant_id)

        skill_data = SkillDefinitionSerializer(skills, many=True).data
        edges = [
            {
                "id": str(d.id),
                "source": str(d.source_skill_id),
                "target": str(d.target_skill_id),
                "is_strict": d.is_strict,
            }
            for d in deps
        ]

        return Response({"skills": skill_data, "dependencies": edges}, status=200)


class StudentPortfolioView(APIView):
    """
    GET /api/v1/learning/portfolio/
    POST /api/v1/learning/portfolio/
    PATCH /api/v1/learning/portfolio/visibility/
    Student Learning Portfolio management.
    """
    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        student_id = getattr(request.user, "id", None)
        if not student_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.learning.models import LearningPortfolio
        from modules.learning.serializers import LearningPortfolioSerializer

        portfolio = LearningPortfolio.objects.filter(tenant_id=tenant_id, student_id=student_id).first()
        if not portfolio:
            return Response({"detail": "Portfolio not found"}, status=404)
        return Response(LearningPortfolioSerializer(portfolio).data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        student_id = getattr(request.user, "id", None)
        if not student_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.learning.portfolio_service import PortfolioService
        from modules.learning.serializers import LearningPortfolioSerializer

        headline = request.data.get("headline", "")
        summary_narrative = request.data.get("summary_narrative", "")
        try:
            portfolio = PortfolioService.create_or_get_portfolio(
                tenant_id=tenant_id,
                student_id=student_id,
                headline=headline,
                summary_narrative=summary_narrative,
            )
            return Response(LearningPortfolioSerializer(portfolio).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)


class ParentPortfolioView(APIView):
    """
    GET /api/v1/learning/portfolio/guardian/<student_id>/
    Guardian access to student portfolio, strictly guarded by active GuardianAccessGrant.
    """
    def get(self, request: Request, student_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        guardian_user_id = getattr(request.user, "id", None)
        if not guardian_user_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.platform_tenant.models import GuardianAccessGrant
        from modules.learning.models import LearningPortfolio, PortfolioVisibility
        from modules.learning.serializers import LearningPortfolioSerializer

        # Check active grant
        grant = GuardianAccessGrant.objects.filter(
            tenant_id=tenant_id,
            guardian_user_id=guardian_user_id,
            student_id=student_id,
            status=GuardianAccessGrant.Status.ACTIVE,
        ).first()

        if not grant:
            return Response({"detail": "Active guardian grant required to view portfolio"}, status=403)

        portfolio = LearningPortfolio.objects.filter(
            tenant_id=tenant_id,
            student_id=student_id,
            visibility__in=[PortfolioVisibility.GUARDIAN_SHARED, PortfolioVisibility.TENANT_PUBLIC],
        ).first()

        if not portfolio:
            return Response({"detail": "Portfolio is private or does not exist"}, status=404)

        return Response(LearningPortfolioSerializer(portfolio).data, status=200)


class AchievementArtifactView(APIView):
    """
    POST /api/v1/learning/portfolio/<portfolio_id>/artifacts/
    Attaches a verified achievement artifact.
    """
    def post(self, request: Request, portfolio_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        from modules.learning.portfolio_service import PortfolioService
        from modules.learning.serializers import AchievementArtifactSerializer

        artifact_type = request.data.get("artifact_type")
        title = request.data.get("title", "")
        reflection_notes = request.data.get("reflection_notes", "")
        source_submission_id = request.data.get("source_submission_id")
        source_certificate_id = request.data.get("source_certificate_id")
        is_featured = bool(request.data.get("is_featured", False))

        try:
            artifact = PortfolioService.attach_achievement_artifact(
                tenant_id=tenant_id,
                portfolio_id=portfolio_id,
                artifact_type=artifact_type,
                title=title,
                reflection_notes=reflection_notes,
                source_submission_id=UUID(source_submission_id) if source_submission_id else None,
                source_certificate_id=UUID(source_certificate_id) if source_certificate_id else None,
                is_featured=is_featured,
            )
            return Response(AchievementArtifactSerializer(artifact).data, status=201)
        except (ValidationError, ValueError) as e:
            return Response({"detail": str(e)}, status=400)


class JourneyTimelineView(APIView):
    """
    GET /api/v1/learning/portfolio/journey/<student_id>/
    Returns the chronological journey narrative timeline for a student.
    """
    def get(self, request: Request, student_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        from modules.learning.models import StudentJourneyTimeline
        from modules.learning.serializers import StudentJourneyTimelineSerializer

        milestones = StudentJourneyTimeline.objects.filter(
            tenant_id=tenant_id,
            student_id=student_id,
        ).order_by("-milestone_date")

        return Response(StudentJourneyTimelineSerializer(milestones, many=True).data, status=200)


# =============================================================================
# Phase 3 VS13: Growth Insights & Longitudinal Learning Intelligence Views
# =============================================================================

class StudentGrowthInsightFeedView(APIView):
    """
    GET /api/v1/learning/insights/<student_id>/
    Returns active formative insights for a student.
    Strictly forbids peer comparison or ranking metrics.
    """
    def get(self, request: Request, student_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        # Reject any peer-comparison or ranking query parameters (Anti-Ranking Guard)
        forbidden_params = {"peer", "rank", "percentile", "compare", "leaderboard", "class_average"}
        if any(p in request.query_params for p in forbidden_params):
            return Response(
                {"detail": "Peer comparison and ranking queries are strictly prohibited by child protection policy."},
                status=400,
            )

        from modules.learning.growth_insight_service import GrowthInsightService
        if not GrowthInsightService.verify_insight_access(tenant_id, actor_id, student_id):
            return Response({"detail": "Access denied to student growth insights."}, status=403)

        from modules.learning.models import LearningInsight, InsightLifecycleStatus
        from modules.learning.serializers import LearningInsightSerializer

        insights = LearningInsight.objects.filter(
            tenant_id=tenant_id,
            student_id=student_id,
            lifecycle_status=InsightLifecycleStatus.ACTIVE,
        ).order_by("-created_at")

        return Response(LearningInsightSerializer(insights, many=True).data, status=200)


class StudentGrowthTrendsView(APIView):
    """
    GET /api/v1/learning/insights/trends/<student_id>/
    Returns longitudinal competency vectors and snapshot progress.
    """
    def get(self, request: Request, student_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        forbidden_params = {"peer", "rank", "percentile", "compare", "leaderboard", "class_average"}
        if any(p in request.query_params for p in forbidden_params):
            return Response(
                {"detail": "Peer comparison and ranking queries are strictly prohibited."},
                status=400,
            )

        from modules.learning.growth_insight_service import GrowthInsightService
        if not GrowthInsightService.verify_insight_access(tenant_id, actor_id, student_id):
            return Response({"detail": "Access denied to student growth trends."}, status=403)

        from modules.learning.models import StudentGrowthTrend, GrowthMetricSnapshot
        from modules.learning.serializers import StudentGrowthTrendSerializer, GrowthMetricSnapshotSerializer

        trends = StudentGrowthTrend.objects.filter(tenant_id=tenant_id, student_id=student_id)
        snapshots = GrowthMetricSnapshot.objects.filter(
            tenant_id=tenant_id,
            student_id=student_id,
        ).order_by("-snapshot_date")[:30]

        return Response(
            {
                "trends": StudentGrowthTrendSerializer(trends, many=True).data,
                "snapshots": GrowthMetricSnapshotSerializer(snapshots, many=True).data,
            },
            status=200,
        )


class StudentMilestoneTimelineView(APIView):
    """
    GET /api/v1/learning/insights/milestones/<student_id>/
    Returns formative milestone achievements and auditable history.
    """
    def get(self, request: Request, student_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.learning.growth_insight_service import GrowthInsightService
        if not GrowthInsightService.verify_insight_access(tenant_id, actor_id, student_id):
            return Response({"detail": "Access denied to student milestones."}, status=403)

        from modules.learning.models import LearningMilestone
        from modules.learning.serializers import LearningMilestoneSerializer

        include_retracted = request.query_params.get("include_retracted", "false").lower() == "true"
        qs = LearningMilestone.objects.filter(tenant_id=tenant_id, student_id=student_id)
        if not include_retracted:
            qs = qs.filter(status="ACHIEVED")

        milestones = qs.order_by("-achieved_at")
        return Response(LearningMilestoneSerializer(milestones, many=True).data, status=200)


class InsightRecalculationView(APIView):
    """
    POST /api/v1/learning/insights/recalculate/
    Triggers an idempotent deterministic derivation run under PostgreSQL advisory lock.
    Restricted to Assigned Mentors, Staff, and Admins.
    """
    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        student_id = request.data.get("student_id")
        event_key = request.data.get("event_key")
        if not student_id or not event_key:
            return Response({"detail": "student_id and event_key are required."}, status=400)

        try:
            student_uuid = UUID(str(student_id))
        except ValueError:
            return Response({"detail": "Invalid student_id UUID format."}, status=400)

        # Actor must not be student or guardian
        role = _get_membership_role(request)
        if role not in ["OWNER", "ADMIN", "STAFF", "MENTOR"]:
            return Response({"detail": "Only staff or assigned mentors may trigger recalculation."}, status=403)

        from modules.learning.growth_insight_service import GrowthInsightService
        try:
            calc_run = GrowthInsightService.trigger_recalculation(
                tenant_id=tenant_id,
                student_id=student_uuid,
                triggered_by=actor_id,
                event_key=str(event_key),
            )
            return Response(
                {
                    "calculation_run_id": calc_run.id,
                    "status": calc_run.status,
                    "metrics_computed_count": calc_run.metrics_computed_count,
                    "completed_at": calc_run.completed_at,
                },
                status=200,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class MilestoneRetractionView(APIView):
    """
    PATCH /api/v1/learning/insights/milestones/<milestone_id>/retract/
    Retracts or restores a milestone record.
    """
    def patch(self, request: Request, milestone_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        action = request.data.get("action", "RETRACT").upper()
        reason = request.data.get("reason", "")

        from modules.learning.growth_insight_service import GrowthInsightService
        from modules.learning.serializers import LearningMilestoneSerializer

        try:
            if action == "RETRACT":
                milestone = GrowthInsightService.retract_milestone(
                    tenant_id=tenant_id,
                    milestone_id=milestone_id,
                    actor_user_id=actor_id,
                    reason=reason,
                )
            elif action == "RESTORE":
                milestone = GrowthInsightService.restore_milestone(
                    tenant_id=tenant_id,
                    milestone_id=milestone_id,
                    actor_user_id=actor_id,
                )
            else:
                return Response({"detail": "Invalid action. Must be RETRACT or RESTORE."}, status=400)

            return Response(LearningMilestoneSerializer(milestone).data, status=200)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


# ============================================================================
# P3-VS14: STUDENT LEARNING OPERATIONS, REFLECTION & AI-ASSISTED GROWTH VIEWS
# ============================================================================

class LearningReflectionListCreateView(APIView):
    """
    GET  /api/v1/learning/reflections/ - List reflections (Student owns or Mentor assigned)
    POST /api/v1/learning/reflections/ - Create reflection (Student only)
    """
    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.learning.models import LearningReflection
        from modules.learning.serializers import LearningReflectionSerializer

        student_id_param = request.query_params.get("student_id")
        target_student_id = UUID(student_id_param) if student_id_param else actor_id

        # Enforce Anti-ranking: reject peer ranking query params
        for prohibited in ["rank", "percentile", "leaderboard", "compare"]:
            if prohibited in request.query_params:
                return Response({"detail": "Peer ranking and comparative sorting are strictly prohibited."}, status=400)

        queryset = LearningReflection.objects.filter(
            tenant_id=tenant_id,
            student_id=target_student_id,
            is_retracted=False,
        ).order_by("-created_at")

        serializer = LearningReflectionSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        prompt_type = request.data.get("prompt_type", "WEEKLY_REVIEW")
        content = request.data.get("content", "")
        mood_sentiment = request.data.get("mood_sentiment", "NEUTRAL")

        from modules.learning.learning_operations_service import LearningOperationsService
        from modules.learning.serializers import LearningReflectionSerializer

        try:
            reflection = LearningOperationsService.create_reflection(
                tenant_id=tenant_id,
                student_id=actor_id,
                prompt_type=prompt_type,
                content=content,
                mood_sentiment=mood_sentiment,
            )
            return Response(LearningReflectionSerializer(reflection).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class LearningReflectionRetractView(APIView):
    """
    POST /api/v1/learning/reflections/<reflection_id>/retract/
    Retracts a previously published reflection entry with audited reason.
    """
    def post(self, request: Request, reflection_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        reason = request.data.get("reason", "")
        from modules.learning.learning_operations_service import LearningOperationsService
        from modules.learning.serializers import LearningReflectionSerializer

        try:
            reflection = LearningOperationsService.retract_reflection(
                tenant_id=tenant_id,
                reflection_id=reflection_id,
                actor_id=actor_id,
                reason=reason,
            )
            return Response(LearningReflectionSerializer(reflection).data, status=200)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class StudentLearningGoalListCreateView(APIView):
    """
    GET  /api/v1/learning/goals/ - List goals (Student owns or Mentor assigned)
    POST /api/v1/learning/goals/ - Create personal goal in DRAFT state
    """
    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.learning.models import StudentLearningGoal
        from modules.learning.serializers import StudentLearningGoalSerializer

        student_id_param = request.query_params.get("student_id")
        target_student_id = UUID(student_id_param) if student_id_param else actor_id

        # Anti-ranking check
        for prohibited in ["rank", "percentile", "leaderboard", "compare"]:
            if prohibited in request.query_params:
                return Response({"detail": "Peer ranking and comparative sorting are strictly prohibited."}, status=400)

        queryset = StudentLearningGoal.objects.filter(
            tenant_id=tenant_id,
            student_id=target_student_id,
        ).prefetch_related("action_steps").order_by("-created_at")

        serializer = StudentLearningGoalSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        title = request.data.get("title", "")
        domain = request.data.get("domain", "")
        target_milestone_id = request.data.get("target_milestone_id")
        target_date = request.data.get("target_date")

        from modules.learning.learning_operations_service import LearningOperationsService
        from modules.learning.serializers import StudentLearningGoalSerializer

        try:
            goal = LearningOperationsService.create_goal(
                tenant_id=tenant_id,
                student_id=actor_id,
                title=title,
                domain=domain,
                target_milestone_id=UUID(target_milestone_id) if target_milestone_id else None,
                target_date=target_date,
            )
            return Response(StudentLearningGoalSerializer(goal).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class StudentLearningGoalTransitionView(APIView):
    """
    POST /api/v1/learning/goals/<goal_id>/transition/
    Transitions a goal through the approved FSM: DRAFT -> ACTIVE -> ACHIEVED/PAUSED/ARCHIVED/SUPERSEDED
    """
    def post(self, request: Request, goal_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        target_status = request.data.get("target_status", "")
        from modules.learning.learning_operations_service import LearningOperationsService
        from modules.learning.serializers import StudentLearningGoalSerializer

        try:
            goal = LearningOperationsService.transition_goal_status(
                tenant_id=tenant_id,
                goal_id=goal_id,
                actor_id=actor_id,
                target_status=target_status,
            )
            return Response(StudentLearningGoalSerializer(goal).data, status=200)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class GoalActionPlanCreateView(APIView):
    """
    POST /api/v1/learning/goals/<goal_id>/action-steps/
    Adds an actionable step to a student learning goal.
    """
    def post(self, request: Request, goal_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        step_order = int(request.data.get("step_order", 1))
        description = request.data.get("description", "")
        due_date = request.data.get("due_date")

        from modules.learning.learning_operations_service import LearningOperationsService
        from modules.learning.serializers import GoalActionPlanSerializer

        try:
            step = LearningOperationsService.add_action_step(
                tenant_id=tenant_id,
                goal_id=goal_id,
                step_order=step_order,
                description=description,
                due_date=due_date,
            )
            return Response(GoalActionPlanSerializer(step).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)


class AIAssistedGrowthSuggestionView(APIView):
    """
    GET  /api/v1/learning/suggestions/ - List suggestions (Students see only PRESENTED; Mentors see PENDING & PRESENTED)
    POST /api/v1/learning/suggestions/generate/ - Trigger AI suggestion (Staff/Mentor only; Students 403)
    """
    def get(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.learning.models import AIAssistedGrowthSuggestion
        from modules.learning.serializers import AIAssistedGrowthSuggestionSerializer
        from modules.platform_tenant.models import TenantMembership

        # Determine role
        membership = TenantMembership.objects.filter(tenant_id=tenant_id, user_id=actor_id).first()
        is_mentor_or_admin = membership and membership.role in ["mentor", "admin", "owner", "staff"]

        student_id_param = request.query_params.get("student_id")
        target_student_id = UUID(student_id_param) if student_id_param else actor_id

        # Anti-ranking check
        for prohibited in ["rank", "percentile", "leaderboard", "compare"]:
            if prohibited in request.query_params:
                return Response({"detail": "Peer ranking and comparative sorting are strictly prohibited."}, status=400)

        queryset = AIAssistedGrowthSuggestion.objects.filter(
            tenant_id=tenant_id,
            student_id=target_student_id,
        )

        if not is_mentor_or_admin:
            # Student moderation gate: PENDING suggestions are strictly filtered out
            queryset = queryset.filter(status="PRESENTED")

        queryset = queryset.order_by("-created_at")
        serializer = AIAssistedGrowthSuggestionSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def post(self, request: Request) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.platform_tenant.models import TenantMembership
        membership = TenantMembership.objects.filter(tenant_id=tenant_id, user_id=actor_id).first()
        if not membership or membership.role not in ["mentor", "admin", "owner", "staff"]:
            return Response({"detail": "Students are forbidden from directly generating authoritative suggestions."}, status=403)

        student_id = UUID(request.data.get("student_id"))
        suggestion_type = request.data.get("suggestion_type", "CONCEPT_REINFORCEMENT")
        recommended_action = request.data.get("recommended_action", "")
        rationale = request.data.get("rationale", "")
        evidence_context = request.data.get("evidence_context", {})

        from modules.learning.learning_operations_service import LearningOperationsService
        from modules.learning.serializers import AIAssistedGrowthSuggestionSerializer

        try:
            sugg = LearningOperationsService.generate_ai_suggestion(
                tenant_id=tenant_id,
                student_id=student_id,
                suggestion_type=suggestion_type,
                recommended_action=recommended_action,
                rationale=rationale,
                evidence_context=evidence_context,
            )
            return Response(AIAssistedGrowthSuggestionSerializer(sugg).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)


class MentorReflectionFeedbackCreateView(APIView):
    """
    POST /api/v1/learning/reflections/<reflection_id>/feedback/
    Posts mentor pedagogical guidance to an assigned student reflection.
    """
    def post(self, request: Request, reflection_id: UUID) -> Response:
        tenant_id = _tenant_id(request)
        actor_id = getattr(request.user, "id", None)
        if not actor_id:
            return Response({"detail": "Authentication required"}, status=401)

        from modules.platform_tenant.models import TenantMembership
        membership = TenantMembership.objects.filter(tenant_id=tenant_id, user_id=actor_id).first()
        if not membership or membership.role not in ["mentor", "admin", "owner"]:
            return Response({"detail": "Only authorized mentors can submit reflection feedback."}, status=403)

        feedback_text = request.data.get("feedback_text", "")
        from modules.learning.learning_operations_service import LearningOperationsService
        from modules.learning.serializers import MentorReflectionFeedbackSerializer

        try:
            feedback = LearningOperationsService.post_mentor_feedback(
                tenant_id=tenant_id,
                reflection_id=reflection_id,
                mentor_id=actor_id,
                feedback_text=feedback_text,
            )
            return Response(MentorReflectionFeedbackSerializer(feedback).data, status=201)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)

