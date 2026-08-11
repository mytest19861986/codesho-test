"""Schema-only API views for the canonical public contract.

These views are exclusively introspected by drf-spectacular through
``config.openapi_urls``. They are never mounted in the runtime URLconf; every
handler raises ``Http404`` if it is called accidentally.
"""

from __future__ import annotations

from uuid import UUID

from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class ErrorSerializer(serializers.Serializer):  # type: ignore[misc]
    code = serializers.CharField()


class AdultAgeAttestationRequestSerializer(serializers.Serializer):  # type: ignore[misc]
    adultAttestation = serializers.BooleanField()
    policyVersion = serializers.CharField(max_length=64)
    subjectId = serializers.UUIDField()


class AdultAgeAttestationReceiptSerializer(serializers.Serializer):  # type: ignore[misc]
    attestationId = serializers.UUIDField()
    attestedAt = serializers.DateTimeField()
    policyVersion = serializers.CharField()
    source = serializers.ChoiceField(choices=["internal_test_api"])
    status = serializers.ChoiceField(choices=["adult_attested"])


class PasscodeLoginRequestSerializer(serializers.Serializer):  # type: ignore[misc]
    username = serializers.CharField(max_length=150)
    passcode = serializers.RegexField(r"^[0-9]{6}$")


class PasscodeChangeCompletionRequestSerializer(serializers.Serializer):  # type: ignore[misc]
    newPasscode = serializers.RegexField(r"^[0-9]{6}$")


class UserSerializer(serializers.Serializer):  # type: ignore[misc]
    id = serializers.UUIDField()
    username = serializers.CharField()


class TenantSerializer(serializers.Serializer):  # type: ignore[misc]
    id = serializers.UUIDField()
    slug = serializers.CharField()
    role = serializers.CharField()


class SessionStateSerializer(serializers.Serializer):  # type: ignore[misc]
    authenticated = serializers.BooleanField()
    user = UserSerializer()
    tenant = TenantSerializer()


class CourseItemSerializer(serializers.Serializer):  # type: ignore[misc]
    id = serializers.UUIDField()
    code = serializers.CharField()
    title = serializers.CharField()
    state = serializers.ChoiceField(choices=["published"])


class LessonItemSerializer(serializers.Serializer):  # type: ignore[misc]
    id = serializers.UUIDField()
    code = serializers.CharField()
    title = serializers.CharField()
    position = serializers.IntegerField(min_value=1)
    state = serializers.ChoiceField(choices=["published"])


class CourseResultsSerializer(serializers.Serializer):  # type: ignore[misc]
    results = CourseItemSerializer(many=True)


class LessonResultsSerializer(serializers.Serializer):  # type: ignore[misc]
    results = LessonItemSerializer(many=True)


ERROR_RESPONSES = {
    400: OpenApiResponse(ErrorSerializer, "Invalid request or tenant signal."),
    401: OpenApiResponse(ErrorSerializer, "Fixed authentication failure response."),
    403: OpenApiResponse(ErrorSerializer, "CSRF failure or authorization boundary."),
    409: OpenApiResponse(ErrorSerializer, "Conflict with the current state."),
    429: OpenApiResponse(
        ErrorSerializer,
        "Abuse-control limit; the runtime supplies a non-negative Retry-After response header.",
    ),
    503: OpenApiResponse(ErrorSerializer, "Critical dependency unavailable."),
}

CSRF_HEADER = OpenApiParameter(
    name="X-CSRFToken",
    type=str,
    location=OpenApiParameter.HEADER,
    required=True,
    description="Django CSRF token required by the runtime endpoint.",
)


class SchemaOnlyAPIView(APIView):  # type: ignore[misc]
    """Fail closed if an isolated declaration is ever accidentally called."""

    parser_classes = [JSONParser]
    serializer_class = ErrorSerializer

    def _unreachable(self, request: Request) -> Response:
        raise Http404


class CsrfSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_auth_csrf_retrieve",
        tags=["api"],
        summary="Establish CSRF and device cookies for a tenant host",
        description="Creates the CSRF token and device-cookie boundary for a tenant host.",
        responses={204: OpenApiResponse(description="CSRF and device cookies established.")},
    )
    def get(self, request: Request) -> Response:
        return self._unreachable(request)


class AdultAttestationSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_auth_signup_adult_attestation_create",
        tags=["api"],
        summary="Record an internal synthetic adult age attestation",
        description=(
            "Internal-only synthetic attestation; no account, credential, membership, or session "
            "is created."
        ),
        parameters=[CSRF_HEADER],
        request=AdultAgeAttestationRequestSerializer,
        responses={
            200: AdultAgeAttestationReceiptSerializer,
            201: AdultAgeAttestationReceiptSerializer,
            **ERROR_RESPONSES,
            404: OpenApiResponse(ErrorSerializer, "Internal-only feature disabled."),
        },
    )
    def post(self, request: Request) -> Response:
        return self._unreachable(request)


class PasscodeLoginSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_auth_passcode_login_create",
        tags=["api"],
        summary="Authenticate a tenant member with a passcode",
        description="Creates a tenant session only after successful runtime authentication.",
        parameters=[CSRF_HEADER],
        request=PasscodeLoginRequestSerializer,
        responses={
            204: OpenApiResponse(description="Session established."),
            **{key: value for key, value in ERROR_RESPONSES.items() if key != 403 and key != 409},
            403: OpenApiResponse(ErrorSerializer, "Passcode change challenge cookie issued."),
        },
    )
    def post(self, request: Request) -> Response:
        return self._unreachable(request)


class PasscodeChangeCompletionSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_auth_passcode_change_complete_create",
        tags=["api"],
        summary="Complete a forced passcode change without creating a session",
        description="Consumes a valid challenge and requires a fresh login after completion.",
        parameters=[
            OpenApiParameter(
                name="__Host-codesho-passcode-change",
                type=str,
                location=OpenApiParameter.COOKIE,
                required=True,
                description="HttpOnly forced passcode-change challenge cookie.",
            ),
            CSRF_HEADER,
        ],
        request=PasscodeChangeCompletionRequestSerializer,
        responses={
            204: OpenApiResponse(description="Challenge consumed; no session created."),
            **ERROR_RESPONSES,
        },
    )
    def post(self, request: Request) -> Response:
        return self._unreachable(request)


class SessionSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_auth_session_retrieve",
        tags=["api"],
        summary="Return the authenticated user and current tenant membership",
        description="Returns the current tenant-scoped session state.",
        responses={200: SessionStateSerializer, 401: ERROR_RESPONSES[401]},
    )
    def get(self, request: Request) -> Response:
        return self._unreachable(request)


class LogoutSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_auth_logout_create",
        tags=["api"],
        summary="Flush the authenticated tenant session",
        description="Flushes the tenant-scoped session and records the runtime audit event.",
        parameters=[CSRF_HEADER],
        request=None,
        responses={
            204: OpenApiResponse(description="Session flushed."),
            403: ERROR_RESPONSES[403],
        },
    )
    def post(self, request: Request) -> Response:
        return self._unreachable(request)


PAGINATION_PARAMETERS = [
    OpenApiParameter(
        name="page",
        type=int,
        location=OpenApiParameter.QUERY,
        required=False,
        description="Positive page number; defaults to 1.",
    ),
    OpenApiParameter(
        name="page_size",
        type=int,
        location=OpenApiParameter.QUERY,
        required=False,
        description="Positive page size, maximum 100; defaults to 20.",
    ),
]


class LearningCourseListSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_learning_courses_list",
        tags=["learning"],
        summary="List published courses for the current tenant",
        description=(
            "Returns only published courses visible to the authenticated active tenant "
            "membership. Pagination is evaluated independently per request."
        ),
        parameters=PAGINATION_PARAMETERS,
        responses={
            200: CourseResultsSerializer,
            400: OpenApiResponse(ErrorSerializer, "Invalid pagination."),
            401: ERROR_RESPONSES[401],
            403: ERROR_RESPONSES[403],
        },
    )
    def get(self, request: Request) -> Response:
        return self._unreachable(request)


class LearningCourseLessonListSchemaView(SchemaOnlyAPIView):
    @extend_schema(
        operation_id="api_v1_learning_course_lessons_list",
        tags=["learning"],
        summary="List published lessons for a visible course",
        description=(
            "Returns only published lessons for a published course visible to the "
            "authenticated active tenant membership. Hidden, missing, and cross-tenant "
            "parents have identical not-found semantics."
        ),
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description="Course UUID.",
            ),
            *PAGINATION_PARAMETERS,
        ],
        responses={
            200: LessonResultsSerializer,
            400: OpenApiResponse(ErrorSerializer, "Invalid pagination."),
            401: ERROR_RESPONSES[401],
            403: ERROR_RESPONSES[403],
            404: OpenApiResponse(ErrorSerializer, "Course not found."),
        },
    )
    def get(self, request: Request, course_id: str) -> Response:
        return self._unreachable(request)
