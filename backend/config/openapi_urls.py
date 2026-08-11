"""Isolated URLconf used only while generating the public OpenAPI contract."""

from django.urls import path

from config.openapi_schema import (
    AdultAttestationSchemaView,
    CsrfSchemaView,
    LearningCourseLessonListSchemaView,
    LearningCourseListSchemaView,
    LogoutSchemaView,
    PasscodeChangeCompletionSchemaView,
    PasscodeLoginSchemaView,
    SessionSchemaView,
)

urlpatterns = [
    path("api/v1/auth/csrf/", CsrfSchemaView.as_view(), name="auth-csrf"),
    path(
        "api/v1/auth/signup/adult-attestation/",
        AdultAttestationSchemaView.as_view(),
        name="adult-age-attestation",
    ),
    path("api/v1/auth/passcode/login/", PasscodeLoginSchemaView.as_view(), name="passcode-login"),
    path(
        "api/v1/auth/passcode/change/complete/",
        PasscodeChangeCompletionSchemaView.as_view(),
        name="passcode-change-complete",
    ),
    path("api/v1/auth/session/", SessionSchemaView.as_view(), name="auth-session"),
    path("api/v1/auth/logout/", LogoutSchemaView.as_view(), name="auth-logout"),
    path(
        "api/v1/learning/courses/",
        LearningCourseListSchemaView.as_view(),
        name="learning-course-list",
    ),
    path(
        "api/v1/learning/courses/<str:course_id>/lessons/",
        LearningCourseLessonListSchemaView.as_view(),
        name="learning-course-lesson-list",
    ),
]
