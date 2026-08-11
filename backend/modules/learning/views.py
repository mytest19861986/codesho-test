from __future__ import annotations

from uuid import UUID

from django.http import HttpRequest
from django.views.decorators.http import require_GET
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, PublicationState


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
    return request.tenant.id  # type: ignore[attr-defined]


class CourseListView(APIView):
    def get(self, request: Request) -> Response:
        pagination = _pagination(request)
        if isinstance(pagination, Response):
            return pagination
        page, page_size = pagination
        start = (page - 1) * page_size
        rows = (
            Course.objects.filter(tenant_id=_tenant_id(request), state=PublicationState.PUBLISHED)
            .order_by("code", "id")
            [start : start + page_size]
        )
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
        rows = (
            Lesson.objects.filter(
                course_id=course.id,
                tenant_id=_tenant_id(request),
                state=PublicationState.PUBLISHED,
            )
            .order_by("position", "code", "id")
            [start : start + page_size]
        )
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


@require_GET
def course_list(request: HttpRequest) -> Response:
    return CourseListView.as_view()(request)


@require_GET
def course_lesson_list(request: HttpRequest, course_id: str) -> Response:
    return CourseLessonListView.as_view()(request, course_id=course_id)
