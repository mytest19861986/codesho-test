from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config import auth_views
from modules.platform_event.views import health_live, health_ready

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/live/", health_live, name="health-live"),
    path("health/ready/", health_ready, name="health-ready"),
    path("api/v1/auth/csrf/", auth_views.csrf, name="auth-csrf"),
    path("api/v1/auth/passcode/login/", auth_views.passcode_login, name="passcode-login"),
    path(
        "api/v1/auth/passcode/change/complete/",
        auth_views.passcode_change_complete,
        name="passcode-change-complete",
    ),
    path("api/v1/auth/session/", auth_views.session, name="auth-session"),
    path("api/v1/auth/logout/", auth_views.logout, name="auth-logout"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
