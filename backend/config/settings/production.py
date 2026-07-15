from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

if SECRET_KEY == "unsafe-local-only":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be configured")

from modules.identity.pepper import validate_pepper_settings

validate_pepper_settings(PASSCODE_ACTIVE_PEPPER_ID, PASSCODE_PEPPERS)  # noqa: F405

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
