"""Pydantic schemas for learning concepts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConceptCreate(BaseModel):
    """Validate a new concept."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    question: str = Field(min_length=1, max_length=5000)
    answer: str = Field(min_length=1, max_length=10000)
    subject: str | None = Field(default=None, max_length=120)
    tags: list[str] = Field(default_factory=list, max_length=20)


class ConceptUpdate(BaseModel):
    """Validate partial concept updates."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    question: str | None = Field(default=None, min_length=1, max_length=5000)
    answer: str | None = Field(default=None, min_length=1, max_length=10000)
    subject: str | None = Field(default=None, max_length=120)
    tags: list[str] | None = Field(default=None, max_length=20)
    is_archived: bool | None = None

    @model_validator(mode="after")
    def validate_update(self):
        """Reject null values for fields that cannot be null."""

        for field_name in (
            "title",
            "question",
            "answer",
            "tags",
            "is_archived",
        ):
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"{field_name} cannot be null")

        if not self.model_fields_set:
            raise ValueError("At least one field must be supplied")

        return self


class ConceptRead(BaseModel):
    """Define the concept representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    question: str
    answer: str
    subject: str | None
    tags: list[str]
    is_archived: bool
    created_at: datetime
    updated_at: datetime