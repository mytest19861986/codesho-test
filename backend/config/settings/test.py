from .base import *  # noqa: F403

SECRET_KEY = "test-only-secret"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CELERY_TASK_ALWAYS_EAGER = True
PASSCODE_ACTIVE_PEPPER_ID = "test-v1"
PASSCODE_PEPPERS = {"test-v1": "dGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3Q="}
