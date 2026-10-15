"""Pydantic schemas for user authentication."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Validate registration data."""

    email: EmailStr = Field(..., max_length=320)
    password: str = Field(..., min_length=12, max_length=128)


class UserLogin(BaseModel):
    """Validate login credentials."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserRead(BaseModel):
    """Define the safe user data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Represent an access-token response."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"