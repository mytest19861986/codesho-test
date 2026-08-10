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
    "modules.learning",
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
    "SERVE_URLCONF": "config.openapi_urls",
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.SessionAuthentication"],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SERVE_PUBLIC": False,
}

TENANT_BASE_DOMAIN = env("TENANT_BASE_DOMAIN", default="localhost")
TENANT_BYPASS_PATHS = (
    "/health/live/",
    "/health/ready/",
    "/api/schema/",
    "/api/schema/swagger-ui/",
)
TENANT_PREAUTH_PATHS = (
    "/api/v1/auth/csrf/",
    "/api/v1/auth/signup/adult-attestation/",
    "/api/v1/auth/passcode/login/",
    "/api/v1/auth/passcode/change/complete/",
)
ADULT_SIGNUP_MODE = env("ADULT_SIGNUP_MODE", default="disabled")
ADULT_SIGNUP_POLICY_VERSION = env(
    "ADULT_SIGNUP_POLICY_VERSION", default="adult-internal-2026-07-26"
)
if ADULT_SIGNUP_MODE not in {"disabled", "internal_test"}:
    raise ImproperlyConfigured("ADULT_SIGNUP_MODE must be disabled or internal_test")
if ADULT_SIGNUP_MODE == "internal_test" and not 1 <= len(ADULT_SIGNUP_POLICY_VERSION) <= 64:
    raise ImproperlyConfigured(
        "ADULT_SIGNUP_POLICY_VERSION must contain 1 to 64 characters in internal_test mode"
    )
ADULT_SIGNUP_RATE_WINDOW_SECONDS = env.int("ADULT_SIGNUP_RATE_WINDOW_SECONDS", default=900)
ADULT_SIGNUP_SUBJECT_MAX_ATTEMPTS = env.int("ADULT_SIGNUP_SUBJECT_MAX_ATTEMPTS", default=5)
ADULT_SIGNUP_IP_MAX_ATTEMPTS = env.int("ADULT_SIGNUP_IP_MAX_ATTEMPTS", default=30)
if (
    ADULT_SIGNUP_RATE_WINDOW_SECONDS <= 0
    or ADULT_SIGNUP_SUBJECT_MAX_ATTEMPTS <= 0
    or ADULT_SIGNUP_IP_MAX_ATTEMPTS <= 0
):
    raise ImproperlyConfigured("adult signup rate limits must be positive")
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
# Forced passcode completion has a separate, short abuse window.  These
# counters are deliberately not shared with login failures: a valid challenge
# must not inherit a lockout caused by password guessing on another endpoint.
PASSCODE_CHANGE_COMPLETION_WINDOW_SECONDS = env.int(
    "PASSCODE_CHANGE_COMPLETION_WINDOW_SECONDS", default=600
)
PASSCODE_CHANGE_COMPLETION_ACCOUNT_MAX_FAILURES = env.int(
    "PASSCODE_CHANGE_COMPLETION_ACCOUNT_MAX_FAILURES", default=5
)
PASSCODE_CHANGE_COMPLETION_CHALLENGE_MAX_FAILURES = env.int(
    "PASSCODE_CHANGE_COMPLETION_CHALLENGE_MAX_FAILURES", default=5
)
PASSCODE_CHANGE_COMPLETION_IP_MAX_FAILURES = env.int(
    "PASSCODE_CHANGE_COMPLETION_IP_MAX_FAILURES", default=30
)
PASSCODE_CHANGE_COMPLETION_DEVICE_MAX_FAILURES = env.int(
    "PASSCODE_CHANGE_COMPLETION_DEVICE_MAX_FAILURES", default=10
)
PASSCODE_CHANGE_COMPLETION_GLOBAL_ALERT_THRESHOLD = env.int(
    "PASSCODE_CHANGE_COMPLETION_GLOBAL_ALERT_THRESHOLD", default=100
)
PASSCODE_CHANGE_CLEANUP_BATCH_SIZE = env.int("PASSCODE_CHANGE_CLEANUP_BATCH_SIZE", default=100)
PASSCODE_CHANGE_TERMINAL_RETENTION_DAYS = env.int(
    "PASSCODE_CHANGE_TERMINAL_RETENTION_DAYS", default=30
)
if not 1 <= PASSCODE_CHANGE_CLEANUP_BATCH_SIZE <= 500:
    raise ImproperlyConfigured(
        "PASSCODE_CHANGE_CLEANUP_BATCH_SIZE must be between 1 and 500"
    )
if PASSCODE_CHANGE_TERMINAL_RETENTION_DAYS <= 0:
    raise ImproperlyConfigured("PASSCODE_CHANGE_TERMINAL_RETENTION_DAYS must be positive")
CODESHO_CLEANUP_CLAIMING_ENABLED = env.bool("CODESHO_CLEANUP_CLAIMING_ENABLED", default=False)
CODESHO_CLEANUP_CLAIMS_PER_CYCLE = env.int("CODESHO_CLEANUP_CLAIMS_PER_CYCLE", default=10)
CODESHO_CLEANUP_LEASE_SECONDS = env.int("CODESHO_CLEANUP_LEASE_SECONDS", default=120)
CODESHO_CLEANUP_MAX_RETRIES = env.int("CODESHO_CLEANUP_MAX_RETRIES", default=3)
CODESHO_CLEANUP_RETRY_DELAY_SECONDS = env.int("CODESHO_CLEANUP_RETRY_DELAY_SECONDS", default=60)
if not 1 <= CODESHO_CLEANUP_CLAIMS_PER_CYCLE <= 100:
    raise ImproperlyConfigured("CODESHO_CLEANUP_CLAIMS_PER_CYCLE must be between 1 and 100")
if not 30 <= CODESHO_CLEANUP_LEASE_SECONDS <= 900:
    raise ImproperlyConfigured("CODESHO_CLEANUP_LEASE_SECONDS must be between 30 and 900")
if not 0 <= CODESHO_CLEANUP_MAX_RETRIES <= 10:
    raise ImproperlyConfigured("CODESHO_CLEANUP_MAX_RETRIES must be between 0 and 10")
if not 10 <= CODESHO_CLEANUP_RETRY_DELAY_SECONDS <= 3600:
    raise ImproperlyConfigured("CODESHO_CLEANUP_RETRY_DELAY_SECONDS must be between 10 and 3600")
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
