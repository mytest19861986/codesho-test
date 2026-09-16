"""
Cryptographic Token Service for Synthetic Pilot Activation.
Implements HMAC-SHA256 signing, verification, nonce tracking, and negative checks.
"""

import hmac
import hashlib
import json
import uuid
import datetime
from typing import Dict, Any, Set, Tuple
from .domain import ActivationToken, RehearsalScope

SYNTHETIC_HMAC_SECRET = b"codesho_synthetic_rehearsal_secret_20260916"

class TokenService:
    def __init__(self):
        self.used_nonces: Set[str] = set()
        self.revoked_tokens: Set[str] = set()

    def generate_token(self, scope: RehearsalScope, decision_ref: str, valid_hours: int = 24) -> ActivationToken:
        scope_dict = scope.model_dump()
        canonical_scope = json.dumps(scope_dict, sort_keys=True)
        scope_digest = hashlib.sha256(canonical_scope.encode("utf-8")).hexdigest()

        now = datetime.datetime.now(datetime.timezone.utc)
        expires = now + datetime.timedelta(hours=valid_hours)
        nonce = uuid.uuid4().hex
        token_id = str(uuid.uuid4())

        payload = f"{token_id}:{scope.tenant_id}:{scope_digest}:{nonce}:{expires.isoformat()}"
        signature = hmac.new(SYNTHETIC_HMAC_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return ActivationToken(
            token_id=token_id,
            tenant_id=scope.tenant_id,
            authorized_scope=scope_dict,
            scope_digest=scope_digest,
            issued_at=now,
            expires_at=expires,
            purpose="SYNTHETIC_ACTIVATION_REHEARSAL",
            decision_reference=decision_ref,
            nonce=nonce,
            revoked=False,
            signature=signature
        )

    def revoke_token(self, token_id: str) -> None:
        self.revoked_tokens.add(token_id)

    def validate_token(self, token: ActivationToken, active_tenant_id: str, current_scope: RehearsalScope) -> Tuple[bool, str]:
        # 1. Revocation check
        if token.revoked or token.token_id in self.revoked_tokens:
            return False, "REVOKED_TOKEN"

        # 2. Time check
        now = datetime.datetime.now(datetime.timezone.utc)
        if now > token.expires_at:
            return False, "EXPIRED_TOKEN"

        # 3. Purpose check
        if token.purpose != "SYNTHETIC_ACTIVATION_REHEARSAL":
            return False, "WRONG_PURPOSE_TOKEN"

        # 4. Tenant binding check (app.current_tenant)
        if token.tenant_id != active_tenant_id:
            return False, "WRONG_TENANT_TOKEN"

        # 5. Nonce / Replay defense
        if token.nonce in self.used_nonces:
            return False, "REPLAYED_TOKEN"

        # 6. Scope digest and drift check
        current_canonical = json.dumps(current_scope.model_dump(), sort_keys=True)
        current_digest = hashlib.sha256(current_canonical.encode("utf-8")).hexdigest()
        if token.scope_digest != current_digest:
            return False, "ALTERED_SCOPE_DIGEST"

        # 7. Signature check
        payload = f"{token.token_id}:{token.tenant_id}:{token.scope_digest}:{token.nonce}:{token.expires_at.isoformat()}"
        expected_sig = hmac.new(SYNTHETIC_HMAC_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(token.signature, expected_sig):
            return False, "INVALID_TOKEN_SIGNATURE"

        return True, "TOKEN_VALID"

    def consume_nonce(self, token: ActivationToken) -> None:
        self.used_nonces.add(token.nonce)
