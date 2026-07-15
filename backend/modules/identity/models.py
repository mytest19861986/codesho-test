import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email"]


class PasscodeCredential(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="passcode_credential")
    encoded_hash = models.CharField(max_length=256)
    pepper_id = models.CharField(max_length=64)
    must_change = models.BooleanField(default=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    credential_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    def __repr__(self) -> str:
        return f"PasscodeCredential(user_id={self.user_id!s}, version={self.credential_version})"

    def __str__(self) -> str:
        return f"Passcode credential for user {self.user_id}"
