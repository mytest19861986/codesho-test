import base64
from unittest.mock import patch

from modules.identity.abuse import (
    AbuseReason,
    AttemptSignals,
    CompletionDimensions,
    CompletionSignals,
    _completion_decision,
    _completion_keys,
    _decision,
    preflight_attempt,
    record_failed_completion_attempt,
    record_successful_attempt,
)
from modules.identity.models import PasscodeCredential, User
from modules.identity.request_signals import validate_abuse_settings


def test_preflight_fails_closed_when_redis_unavailable(settings):
    settings.PASSCODE_SIGNAL_HMAC_KEY = base64.b64encode(b"k" * 32).decode()
    settings.REDIS_URL = "redis://127.0.0.1:1/0"
    with patch("modules.identity.abuse._client") as factory:
        factory.side_effect = OSError("unavailable")
        decision = preflight_attempt(
            credential=None,
            signals=AttemptSignals("account", "127.0.0.1"),
        )
    assert decision.reason is AbuseReason.BACKEND_UNAVAILABLE
    assert not decision.allowed


def test_decision_progressive_and_limits(settings):
    settings.PASSCODE_PROGRESSIVE_DELAYS_MS = (250, 500, 1000, 2000)
    settings.PASSCODE_GLOBAL_ALERT_THRESHOLD = 1000
    assert _decision([1, 0, 0, 0, 1000], [900000] * 5, None).progressive_delay_ms == 250
    assert _decision([5, 0, 0, 0, 0], [1000] * 5, None).reason is AbuseReason.ACCOUNT_LIMIT
    assert _decision([0, 0, 30, 0, 0], [1000] * 5, None).reason is AbuseReason.IP_LIMIT
    assert _decision([0, 0, 0, 20, 0], [1000] * 5, None).reason is AbuseReason.DEVICE_LIMIT


def test_abuse_settings_require_strong_key():
    validate_abuse_settings(
        "redis://redis:6379/0",
        base64.b64encode(b"x" * 32).decode(),
        900,
        5,
        900,
        30,
        20,
        1000,
        300,
        (250, 500, 1000, 2000),
    )


def test_malformed_and_negative_ttl_responses_fail_closed(settings):
    settings.PASSCODE_SIGNAL_HMAC_KEY = base64.b64encode(b"k" * 32).decode()
    for response in ([1, 2], [-1], [1] * 8 + [-1, 1]):
        with patch("modules.identity.abuse._client") as factory:
            factory.return_value.eval.return_value = response
            decision = preflight_attempt(credential=None, signals=AttemptSignals("a", "127.0.0.1"))
        assert decision.reason is AbuseReason.BACKEND_UNAVAILABLE
        assert decision.allowed is False


def test_success_clear_timeout_is_atomic_and_fails_closed(settings, db):
    settings.PASSCODE_SIGNAL_HMAC_KEY = base64.b64encode(b"k" * 32).decode()
    user = User.objects.create_user(username="learner", email="learner@example.com")
    credential = PasscodeCredential.objects.create(
        user=user, encoded_hash="placeholder", pepper_id="test", must_change=False
    )
    with patch("modules.identity.abuse._client") as factory:
        factory.return_value.eval.side_effect = TimeoutError("redis timeout")
        decision = record_successful_attempt(
            credential=credential,
            signals=AttemptSignals("tenant:learner", "127.0.0.1"),
        )
    assert decision.reason is AbuseReason.BACKEND_UNAVAILABLE
    assert decision.allowed is False


def test_completion_counter_dimensions_and_distinct_alert_thresholds(settings):
    settings.PASSCODE_SIGNAL_HMAC_KEY = base64.b64encode(b"k" * 32).decode()
    settings.PASSCODE_CHANGE_COMPLETION_WINDOW_SECONDS = 600
    signals = CompletionSignals(
        "127.0.0.1",
        "a" * 32,
        account_subject="tenant:user",
        challenge_subject="challenge-id",
        global_subject="selector-id",
    )
    with patch("modules.identity.abuse._client") as factory:
        factory.return_value.eval.return_value = [
            0, 0, 0, 0, 1, 600000, 1, 600000, 99, 600000, 19, 600000
        ]
        decision = record_failed_completion_attempt(
            signals, CompletionDimensions(ip=True, device=True, global_detection=True)
        )
    assert decision.allowed and not decision.global_alert
    call = factory.return_value.eval.call_args
    assert call.args[1] == 6
    assert call.args[2:8] == (
        *_completion_keys(signals),
        "codesho:passcode:v1:completion:global-distinct",
    )
    assert call.args[-6:-1] == ("0", "0", "1", "1", "1")
    assert call.args[-1] != signals.global_subject
    assert not _completion_decision(
        [0, 0, 0, 0, 99], [600000] * 5, distinct_subjects=19
    ).global_alert
    assert _completion_decision(
        [0, 0, 0, 0, 99], [600000] * 5, distinct_subjects=20
    ).global_alert
    assert _completion_decision(
        [0, 0, 0, 0, 100], [600000] * 5, distinct_subjects=1
    ).global_alert
