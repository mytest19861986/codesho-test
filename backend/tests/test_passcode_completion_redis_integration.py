"""Real-Redis contract for forced passcode completion abuse counters."""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from time import monotonic, sleep
from uuid import uuid4

import pytest

from modules.identity.abuse import (
    CompletionDimensions,
    CompletionSignals,
    _client,
    _completion_distinct_key,
    _completion_keys,
    record_failed_completion_attempt,
)


@pytest.fixture
def real_completion_redis(settings):
    settings.PASSCODE_SIGNAL_HMAC_KEY = base64.b64encode(b"r" * 32).decode()
    settings.PASSCODE_RATE_LIMIT_REDIS_PREFIX = f"codesho:test:completion:{uuid4()}"
    client = _client()
    try:
        client.ping()
    except Exception as exc:
        pytest.skip(f"real Redis unavailable: {exc}")
    yield client
    client.delete(*client.keys(f"{settings.PASSCODE_RATE_LIMIT_REDIS_PREFIX}:*"))


def _signals(subject: str) -> CompletionSignals:
    return CompletionSignals(
        "127.0.0.1",
        "a" * 32,
        account_subject=f"tenant:{subject}",
        challenge_subject=f"challenge:{subject}",
        global_subject=f"selector:{subject}",
    )


def test_completion_global_redis_window_and_distinct_are_atomic(real_completion_redis, settings):
    dimensions = CompletionDimensions(ip=True, device=True, global_detection=True)
    first = _signals("one")
    assert not record_failed_completion_attempt(first, dimensions).global_alert
    keys = _completion_keys(first)
    assert 0 < real_completion_redis.pttl(keys[4]) <= 600000
    assert 0 < real_completion_redis.pttl(_completion_distinct_key()) <= 600000
    for _ in range(97):
        record_failed_completion_attempt(first, dimensions)
    assert not record_failed_completion_attempt(first, dimensions).global_alert
    assert record_failed_completion_attempt(first, dimensions).global_alert
    assert real_completion_redis.zcard(_completion_distinct_key()) == 1
    real_completion_redis.delete(*real_completion_redis.keys(f"{settings.PASSCODE_RATE_LIMIT_REDIS_PREFIX}:*"))
    for number in range(19):
        assert not record_failed_completion_attempt(_signals(str(number)), dimensions).global_alert
    assert record_failed_completion_attempt(_signals("20"), dimensions).global_alert
    assert real_completion_redis.zcard(_completion_distinct_key()) == 20


def test_completion_global_redis_repeated_event_does_not_slide_window(real_completion_redis):
    dimensions = CompletionDimensions(ip=True, device=True, global_detection=True)
    signals = _signals("fixed-window")
    record_failed_completion_attempt(signals, dimensions)
    total_key = _completion_keys(signals)[4]
    distinct_key = _completion_distinct_key()
    initial_total_ttl = real_completion_redis.pttl(total_key)
    initial_distinct_ttl = real_completion_redis.pttl(distinct_key)
    sleep(0.02)
    record_failed_completion_attempt(signals, dimensions)
    assert real_completion_redis.pttl(total_key) <= initial_total_ttl
    assert real_completion_redis.pttl(distinct_key) <= initial_distinct_ttl


def test_completion_global_redis_expiry_starts_a_clean_window(real_completion_redis):
    dimensions = CompletionDimensions(ip=True, device=True, global_detection=True)
    signals = _signals("expiry")
    record_failed_completion_attempt(signals, dimensions)
    total_key = _completion_keys(signals)[4]
    distinct_key = _completion_distinct_key()
    real_completion_redis.pexpire(total_key, 20)
    real_completion_redis.pexpire(distinct_key, 20)
    deadline = monotonic() + 1
    while monotonic() < deadline and (
        real_completion_redis.exists(total_key) or real_completion_redis.exists(distinct_key)
    ):
        sleep(0.01)
    assert not real_completion_redis.exists(total_key)
    assert not real_completion_redis.exists(distinct_key)
    result = record_failed_completion_attempt(signals, dimensions)
    assert not result.global_alert
    assert int(real_completion_redis.get(total_key)) == 1
    assert real_completion_redis.zcard(distinct_key) == 1
    assert 0 < real_completion_redis.pttl(total_key) <= 600000
    assert 0 < real_completion_redis.pttl(distinct_key) <= 600000


def test_completion_global_redis_concurrent_updates_preserve_counts(real_completion_redis):
    dimensions = CompletionDimensions(ip=True, device=True, global_detection=True)
    with ThreadPoolExecutor(max_workers=12) as executor:
        list(
            executor.map(
                lambda number: record_failed_completion_attempt(_signals(str(number)), dimensions),
                range(20),
            )
        )
    key = _completion_keys(_signals("0"))[4]
    assert int(real_completion_redis.get(key)) == 20
    assert real_completion_redis.zcard(_completion_distinct_key()) == 20
    assert real_completion_redis.pttl(key) > 0
    assert real_completion_redis.pttl(_completion_distinct_key()) > 0
