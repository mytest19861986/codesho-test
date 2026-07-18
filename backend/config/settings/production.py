from django.core.exceptions import ImproperlyConfigured

# Settings are intentionally imported through the project-wide star import.
# ruff: noqa: F405
from .base import *  # noqa: F403

if SECRET_KEY == "unsafe-local-only":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be configured")

from modules.identity.challenge_cookie import (
    COOKIE_DOMAIN,
    COOKIE_HTTPONLY,
    COOKIE_NAME,
    COOKIE_PATH,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
)
from modules.identity.pepper import validate_pepper_settings
from modules.identity.request_signals import validate_abuse_settings

validate_pepper_settings(PASSCODE_ACTIVE_PEPPER_ID, PASSCODE_PEPPERS)  # noqa: F405
validate_abuse_settings(  # noqa: F405
    REDIS_URL,
    PASSCODE_SIGNAL_HMAC_KEY,
    PASSCODE_ATTEMPT_WINDOW_SECONDS,
    PASSCODE_ACCOUNT_MAX_FAILURES,
    PASSCODE_LOCKOUT_SECONDS,
    PASSCODE_IP_MAX_FAILURES,
    PASSCODE_DEVICE_MAX_FAILURES,
    PASSCODE_GLOBAL_ALERT_THRESHOLD,
    PASSCODE_GLOBAL_WINDOW_SECONDS,
    PASSCODE_PROGRESSIVE_DELAYS_MS,
)

if (
    COOKIE_NAME != "__Host-codesho-passcode-change"
    or not COOKIE_SECURE
    or not COOKIE_HTTPONLY
    or COOKIE_SAMESITE != "Lax"
    or COOKIE_PATH != "/"
    or COOKIE_DOMAIN is not None
):
    raise ImproperlyConfigured("forced passcode-change cookie policy is unsafe")

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
