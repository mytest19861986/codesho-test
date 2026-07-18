"""Transactional issuance for the forced-passcode-change login branch."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID, uuid4

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError
from django.utils import timezone

from modules.identity.challenge import (
    ChallengeMaterial,
    digest_challenge_secret,
    generate_challenge_material,
)
from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.platform_event.security_audit import (
    PasscodeChangeAuditMetadata,
    SecurityAuditError,
    append_security_event,
    passcode_change_challenge_issued,
    passcode_change_challenge_superseded,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


class ChallengeIssuanceError(RuntimeError):
    """The issuance transaction did not commit and must fail closed."""


@dataclass(frozen=True, slots=True)
class IssuedChallenge:
    """Opaque material retained only until the response cookie is written."""

    material: ChallengeMaterial


def _metadata(
    *,
    tenant: Tenant,
    user: User,
    credential: PasscodeCredential,
    correlation_id: UUID,
    idempotency_key: str,
) -> PasscodeChangeAuditMetadata:
    return PasscodeChangeAuditMetadata(
        event_id=uuid4(),
        correlation_id=correlation_id,
        tenant_id=tenant.id,
        subject_user_id=user.id,
        actor_user_id=user.id,
        credential_version=credential.credential_version,
        idempotency_key=idempotency_key,
    )


def issue_forced_passcode_change_challenge(
    *, tenant: Tenant, user: User, credential: PasscodeCredential, correlation_id: UUID
) -> IssuedChallenge:
    """Replace any active challenge and append bounded audit evidence atomically."""

    try:
        material = generate_challenge_material()
        with tenant_atomic(tenant.id):
            # The credential lock serializes repeat logins before the partial unique
            # index becomes a final defensive backstop.
            locked_credential = PasscodeCredential.objects.select_for_update().get(pk=credential.pk)
            now = timezone.now()
            active_challenges = list(
                PasscodeChangeChallenge.objects.select_for_update().filter(
                    tenant=tenant,
                    credential=locked_credential,
                    purpose=PasscodeChangeChallenge.Purpose.FORCED_PASSCODE_CHANGE,
                    state=PasscodeChangeChallenge.State.ACTIVE,
                )
            )
            for active in active_challenges:
                active.state = PasscodeChangeChallenge.State.REVOKED
                active.secret_digest = None
                active.revoked_at = now
                active.save(update_fields=["state", "secret_digest", "revoked_at"])
                append_security_event(
                    passcode_change_challenge_superseded(
                        _metadata(
                            tenant=tenant,
                            user=user,
                            credential=locked_credential,
                            correlation_id=correlation_id,
                            # This is an internal row identifier, never the
                            # cookie selector or any bearer-equivalent value.
                            idempotency_key=f"passcode-change:revoke:{active.id}",
                        )
                    )
                )

            pepper_id = settings.PASSCODE_ACTIVE_PEPPER_ID
            issued = PasscodeChangeChallenge.objects.create(
                selector=material.selector,
                tenant=tenant,
                credential=locked_credential,
                credential_version=locked_credential.credential_version,
                purpose=PasscodeChangeChallenge.Purpose.FORCED_PASSCODE_CHANGE,
                secret_digest=digest_challenge_secret(material.secret, pepper_id),
                pepper_id=pepper_id,
                state=PasscodeChangeChallenge.State.ACTIVE,
                issued_at=now,
                expires_at=now + timedelta(seconds=600),
            )
            append_security_event(
                passcode_change_challenge_issued(
                    _metadata(
                        tenant=tenant,
                        user=user,
                        credential=locked_credential,
                        correlation_id=correlation_id,
                        # This is an internal row identifier, never the
                        # cookie selector or any bearer-equivalent value.
                        idempotency_key=f"passcode-change:issue:{issued.id}",
                    )
                )
            )
    except (
        DatabaseError,
        ImproperlyConfigured,
        RuntimeError,
        SecurityAuditError,
        ValueError,
    ) as exc:
        raise ChallengeIssuanceError("forced passcode change issuance unavailable") from exc
    return IssuedChallenge(material=material)
