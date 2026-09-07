from __future__ import annotations

from typing import Protocol, cast
from uuid import UUID

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.views.decorators.http import require_GET
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Assignment,
    AssignmentState,
    Course,
    Feedback,
    LearningPath,
    Lesson,
    Module,
    Progress,
    PublicationState,
    Submission,
)
from .serializers import (
    AssignmentSerializer,
    CourseSerializer,
    FeedbackSerializer,
    LearningPathSerializer,
    LessonSerializer,
    MentorSubmissionQueueSerializer,
    ModuleSerializer,
    ParentStudentSummarySerializer,
    ProgressSerializer,
    SubmissionSerializer,
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
