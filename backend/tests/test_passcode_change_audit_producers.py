from uuid import uuid4

import pytest

from modules.platform_event.security_audit import (
    PasscodeChangeAuditMetadata,
    ReasonCode,
    SecurityEventType,
    passcode_change_challenge_consumed,
    passcode_change_challenge_expired,
    passcode_change_challenge_issued,
    passcode_change_challenge_revoked_for_pepper_rotation,
    passcode_change_challenge_superseded,
    passcode_change_rejected,
)


@pytest.fixture
def metadata():
    return PasscodeChangeAuditMetadata(
        uuid4(), uuid4(), uuid4(), uuid4(), 1, idempotency_key="change-1"
    )


def test_every_permitted_dormant_audit_combination_is_typed(metadata):
    events = [
        passcode_change_challenge_issued(metadata),
        passcode_change_challenge_superseded(metadata),
        passcode_change_challenge_consumed(metadata),
        passcode_change_challenge_expired(metadata),
        passcode_change_rejected(metadata, ReasonCode.CHALLENGE_INVALID),
        passcode_change_rejected(metadata, ReasonCode.PASSCODE_SAME_AS_CURRENT),
        passcode_change_challenge_revoked_for_pepper_rotation(metadata),
    ]
    assert {event.event_type for event in events} == {
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_ISSUED,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_REVOKED,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_CONSUMED,
        SecurityEventType.PASSCODE_CHANGE_CHALLENGE_EXPIRED,
        SecurityEventType.PASSCODE_CHANGE_REJECTED,
    }
    assert all(event.event_id == metadata.event_id for event in events)


@pytest.mark.parametrize("reason", [ReasonCode.LOGIN_FAILED, "free text", None])
def test_rejected_producer_rejects_unknown_or_free_text_reasons(metadata, reason):
    with pytest.raises(ValueError, match="invalid passcode change audit reason"):
        passcode_change_rejected(metadata, reason)  # type: ignore[arg-type]


@pytest.mark.parametrize("version,key", [(0, None), (1, ""), (1, "x" * 256)])
def test_metadata_rejects_unbounded_or_invalid_values(version, key):
    with pytest.raises(ValueError, match="invalid passcode change audit metadata"):
        PasscodeChangeAuditMetadata(
            uuid4(), uuid4(), uuid4(), uuid4(), version, idempotency_key=key
        )


def test_metadata_rejects_non_uuid_identifiers():
    with pytest.raises(ValueError, match="invalid passcode change audit metadata"):
        PasscodeChangeAuditMetadata(
            "not-an-event-id", uuid4(), uuid4(), uuid4(), 1  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "sensitive_name", ["passcode", "secret", "digest", "cookie", "raw_ip", "device", "selector"]
)
def test_metadata_has_no_sensitive_signal_surface(sensitive_name):
    values = {
        "event_id": uuid4(),
        "correlation_id": uuid4(),
        "tenant_id": uuid4(),
        "subject_user_id": uuid4(),
        "credential_version": 1,
        sensitive_name: "not-allowed",
    }
    with pytest.raises(TypeError) as exc_info:
        PasscodeChangeAuditMetadata(**values)  # type: ignore[call-arg]
    assert "not-allowed" not in str(exc_info.value)
