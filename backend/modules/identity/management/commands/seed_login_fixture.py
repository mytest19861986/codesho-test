"""Create the synthetic, non-production fixture used by the bounded login gate."""

from __future__ import annotations

import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from modules.identity.models import User
from modules.identity.passcodes import InvalidPasscode, set_passcode, verify_passcode
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


class Command(BaseCommand):
    help = "Create or update the synthetic non-production login fixture."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--username", default="login-fixture")
        parser.add_argument("--email", default="login-fixture@example.test")
        parser.add_argument("--tenant-slug", default="login-fixture")
        parser.add_argument("--tenant-name", default="Login Fixture")
        parser.add_argument(
            "--passcode-stdin",
            action="store_true",
            help="Read the six-digit passcode from stdin; it is never accepted as an argument.",
        )

    def handle(self, *args, **options) -> str:
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "")
        if not settings.DEBUG or settings_module.endswith("production"):
            raise CommandError("login fixture command is limited to non-production settings")
        if not options["passcode_stdin"]:
            raise CommandError("passcode must be supplied through --passcode-stdin")

        passcode = sys.stdin.readline().rstrip("\r\n")
        try:
            if len(passcode) != 6 or not passcode.isascii() or not passcode.isdigit():
                raise InvalidPasscode("invalid fixture passcode")
        except InvalidPasscode as exc:
            raise CommandError("fixture passcode must contain exactly six ASCII digits") from exc

        with transaction.atomic():
            tenant, _ = Tenant.objects.update_or_create(
                slug=options["tenant_slug"],
                defaults={"name": options["tenant_name"], "status": Tenant.Status.ACTIVE},
            )
            user, _ = User.objects.update_or_create(
                username=options["username"],
                defaults={
                    "email": options["email"],
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            with tenant_atomic(tenant.id):
                TenantMembership.objects.update_or_create(
                    tenant=tenant,
                    user=user,
                    defaults={"role": TenantMembership.Role.LEARNER, "is_active": True},
                )
            credential = getattr(user, "passcode_credential", None)
            if (
                credential is None
                or not verify_passcode(user, passcode).valid
                or credential.must_change
            ):
                set_passcode(user, passcode, must_change=False)

        self.stdout.write("Login fixture ready.")
        return "Login fixture ready."
