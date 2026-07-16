import json
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env()

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-local-only")
DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost"])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "modules.identity",
    "modules.platform_tenant",
    "modules.platform_event",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "modules.platform_tenant.middleware.SessionEpochMiddleware",
    "modules.platform_tenant.middleware.TenantCandidateMiddleware",
    "modules.platform_tenant.middleware.TenantTransactionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///:memory:")}
database_test_name = env("DATABASE_TEST_NAME", default=None)
if database_test_name:
    DATABASES["default"]["TEST"] = {"NAME": database_test_name}
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"].setdefault("OPTIONS", {})["options"] = "-c search_path=codesho,public"
DATABASES["default"]["CONN_MAX_AGE"] = 0
DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

AUTH_USER_MODEL = "identity.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Codesho API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

TENANT_BASE_DOMAIN = env("TENANT_BASE_DOMAIN", default="localhost")
TENANT_BYPASS_PATHS = (
    "/health/live/",
    "/health/ready/",
    "/api/schema/",
    "/api/schema/swagger-ui/",
)
TENANT_PREAUTH_PATHS = ("/api/v1/auth/csrf/", "/api/v1/auth/passcode/login/")
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=43_200)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_FAILURE_VIEW = "config.auth_views.csrf_failure"

REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")
PASSCODE_SIGNAL_HMAC_KEY = env("PASSCODE_SIGNAL_HMAC_KEY", default="")
PASSCODE_ATTEMPT_WINDOW_SECONDS = env.int("PASSCODE_ATTEMPT_WINDOW_SECONDS", default=900)
PASSCODE_ACCOUNT_MAX_FAILURES = env.int("PASSCODE_ACCOUNT_MAX_FAILURES", default=5)
PASSCODE_LOCKOUT_SECONDS = env.int("PASSCODE_LOCKOUT_SECONDS", default=900)
PASSCODE_IP_MAX_FAILURES = env.int("PASSCODE_IP_MAX_FAILURES", default=30)
PASSCODE_DEVICE_MAX_FAILURES = env.int("PASSCODE_DEVICE_MAX_FAILURES", default=20)
PASSCODE_GLOBAL_ALERT_THRESHOLD = env.int("PASSCODE_GLOBAL_ALERT_THRESHOLD", default=1000)
PASSCODE_GLOBAL_WINDOW_SECONDS = env.int("PASSCODE_GLOBAL_WINDOW_SECONDS", default=300)
PASSCODE_PROGRESSIVE_DELAYS_MS = tuple(
    int(value)
    for value in env.list("PASSCODE_PROGRESSIVE_DELAYS_MS", default=["250", "500", "1000", "2000"])
)
PASSCODE_RATE_LIMIT_REDIS_PREFIX = env(
    "PASSCODE_RATE_LIMIT_REDIS_PREFIX", default="codesho:passcode:v1"
)
PASSCODE_BACKEND_FAILURE_RETRY_SECONDS = env.int(
    "PASSCODE_BACKEND_FAILURE_RETRY_SECONDS", default=5
)
TRUSTED_PROXY_CIDRS = tuple(env.list("TRUSTED_PROXY_CIDRS", default=[]))
PASSCODE_DEVICE_COOKIE_NAME = env("PASSCODE_DEVICE_COOKIE_NAME", default="codesho_device")
PASSCODE_DEVICE_MAX_AGE_SECONDS = env.int("PASSCODE_DEVICE_MAX_AGE_SECONDS", default=2_592_000)

PASSCODE_ACTIVE_PEPPER_ID = env("PASSCODE_ACTIVE_PEPPER_ID", default="")
try:
    PASSCODE_PEPPERS = json.loads(env("PASSCODE_PEPPERS", default="{}"))
except json.JSONDecodeError as exc:
    raise ImproperlyConfigured("PASSCODE_PEPPERS must be valid JSON") from exc
if not isinstance(PASSCODE_PEPPERS, dict):
    raise ImproperlyConfigured("PASSCODE_PEPPERS must be a JSON object")

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_ALWAYS_EAGER = False
