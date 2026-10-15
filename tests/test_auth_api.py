"""Tests for JWT access-token creation and verification."""

from datetime import datetime, timezone

import jwt
import pytest

from app.core.security import create_access_token, decode_access_token


def test_access_token_contains_subject_and_expiration():
    subject = "test-user-123"

    token = create_access_token(subject)
    payload = decode_access_token(token)

    assert payload["sub"] == subject
    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_invalid_token_is_rejected():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("not.a.valid.jwt")