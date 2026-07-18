import logging
from uuid import uuid4

import pytest

from modules.identity.challenge_cookie import (
    CHALLENGE_SECRET_MIN_BYTES,
    COOKIE_DOMAIN,
    COOKIE_HTTPONLY,
    COOKIE_NAME,
    COOKIE_PATH,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    COOKIE_TTL_SECONDS,
    ChallengeCookieValue,
    parse_challenge_cookie,
    serialize_challenge_cookie,
)


def test_cookie_contract_round_trip_and_immutable_policy():
    value = ChallengeCookieValue(selector=uuid4(), secret=b"x" * CHALLENGE_SECRET_MIN_BYTES)
    serialized = serialize_challenge_cookie(value)
    assert parse_challenge_cookie(serialized) == value
    assert (
        COOKIE_NAME,
        COOKIE_SECURE,
        COOKIE_HTTPONLY,
        COOKIE_SAMESITE,
        COOKIE_PATH,
        COOKIE_DOMAIN,
        COOKIE_TTL_SECONDS,
    ) == ("__Host-codesho-passcode-change", True, True, "Lax", "/", None, 600)


@pytest.mark.parametrize(
    "value",
    [
        ChallengeCookieValue(selector=uuid4(), secret=b"x" * 31),
        ChallengeCookieValue(selector=uuid4(), secret=b"x" * 400),
        ChallengeCookieValue(selector="not-a-uuid", secret=b"x" * 32),  # type: ignore[arg-type]
        ChallengeCookieValue(selector=uuid4(), secret="secret"),  # type: ignore[arg-type]
    ],
)
def test_cookie_serializer_rejects_invalid_or_oversized_material_without_disclosure(value):
    with pytest.raises(ValueError) as exc_info:
        serialize_challenge_cookie(value)
    assert str(exc_info.value) == "invalid passcode change cookie"


@pytest.mark.parametrize(
    "raw",
    [
        "v2.a.b", "v1.a", "v1.a.b.c", "v1.not-a-uuid.QUJD",
        "v1.00000000-0000-0000-0000-000000000000.abc=",
        "v1.00000000-0000-0000-0000-000000000000.@@@",
        "v1.00000000-0000-0000-0000-000000000000.YQ", "x" * 513,
        "v1.00000000-0000-0000-0000-000000000000.QUJD".upper(),
    ],
)
def test_cookie_parser_rejects_boundary_inputs_without_disclosure(raw, caplog):
    caplog.set_level(logging.DEBUG)
    with pytest.raises(ValueError) as exc_info:
        parse_challenge_cookie(raw)
    assert str(exc_info.value) == "invalid passcode change cookie"
    assert raw not in str(exc_info.value)
    assert raw not in caplog.text
