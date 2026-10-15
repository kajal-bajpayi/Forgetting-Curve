"""Tests for user registration and response schemas."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.user import User
from app.schemas.user import UserCreate, UserRead


def test_valid_registration_data_is_accepted():
    user_data = UserCreate(
        email="learner@example.com",
        password="correct-horse-battery",
    )

    assert user_data.email == "learner@example.com"
    assert user_data.password == "correct-horse-battery"


def test_invalid_email_is_rejected():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="correct-horse-battery",
        )


def test_short_password_is_rejected():
    with pytest.raises(ValidationError):
        UserCreate(
            email="learner@example.com",
            password="short",
        )


def test_user_read_excludes_sensitive_fields():
    now = datetime.now(timezone.utc)

    user = User(
        id=uuid4(),
        email="learner@example.com",
        password_hash="example-hash-not-a-real-password",
        created_at=now,
        updated_at=now,
    )

    response = UserRead.model_validate(user)

    assert response.id == user.id
    assert response.email == user.email
    assert response.created_at == now
    assert response.updated_at == now

    response_data = response.model_dump()

    assert "password" not in response_data
    assert "password_hash" not in response_data