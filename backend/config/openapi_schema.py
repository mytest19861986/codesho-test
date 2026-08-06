"""Schema-only API views for the canonical public contract.

These views are exclusively introspected by drf-spectacular through
``config.openapi_urls``. They are never mounted in the runtime URLconf; every
handler raises ``Http404`` if it is called accidentally.
"""

from __future__ import annotations

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
        summary="Establish CSRF and device cookies for a tenant host",
        description="Creates the CSRF token and device-cookie boundary for a tenant host.",
        responses={204: OpenApiResponse(description="CSRF and device cookies established.")},
    )
    def get(self, request: Request) -> Response:
        return self._unreachable(request)


class AdultAttestationSchemaView(SchemaOnlyAPIView):
    @extend_schema(
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
        summary="Return the authenticated user and current tenant membership",
        description="Returns the current tenant-scoped session state.",
        responses={200: SessionStateSerializer, 401: ERROR_RESPONSES[401]},
    )
    def get(self, request: Request) -> Response:
        return self._unreachable(request)


class LogoutSchemaView(SchemaOnlyAPIView):
    @extend_schema(
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
