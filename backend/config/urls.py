from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Explicit static import for platform admin site registration in Composition Root
from config import auth_views
from config import platform_admin as _platform_admin  # noqa: F401
from config.adult_signup import adult_age_attestation
from modules.learning.views import course_lesson_list, course_list
from modules.platform_event.views import health_live, health_ready

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/live/", health_live, name="health-live"),
    path("health/ready/", health_ready, name="health-ready"),
    path("api/v1/auth/csrf/", auth_views.csrf, name="auth-csrf"),
    path(
        "api/v1/auth/signup/adult-attestation/",
        adult_age_attestation,
        name="adult-age-attestation",
    ),
    path("api/v1/auth/passcode/login/", auth_views.passcode_login, name="passcode-login"),
    path(
        "api/v1/auth/passcode/change/complete/",
        auth_views.passcode_change_complete,
        name="passcode-change-complete",
    ),
    path("api/v1/auth/session/", auth_views.session, name="auth-session"),
    path("api/v1/auth/logout/", auth_views.logout, name="auth-logout"),
    path(
        "api/v1/learning/courses/",
        course_list,
        name="learning-course-list",
    ),
    path(
        "api/v1/learning/courses/<str:course_id>/lessons/",
        course_lesson_list,
        name="learning-course-lesson-list",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
