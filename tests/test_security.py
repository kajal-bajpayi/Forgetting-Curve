"""Tests for password hashing and verification."""

from app.core.security import hash_password, verify_password


def test_password_is_hashed():
    password = "correct-horse-battery"

    hashed = hash_password(password)

    # The hash must not be the original password
    assert hashed != password

    # The hash must be a string
    assert isinstance(hashed, str)


def test_correct_password_is_verified():
    password = "correct-horse-battery"

    hashed = hash_password(password)

    # The original password should match its hash
    assert verify_password(password, hashed) is True


def test_incorrect_password_is_rejected():
    password = "correct-horse-battery"

    hashed = hash_password(password)

    # A different password should not match the hash
    assert verify_password("wrong-password-value", hashed) is False