"""Centralized application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    app_name: str = "Forgetting Curve API"

    app_env: Literal[
        "development",
        "testing",
        "production",
    ] = "development"

    api_v1_prefix: str = "/api/v1"

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
    ] = "INFO"

    # Database configuration
    database_url: str = "sqlite:///./forgetting_curve.db"

    # JWT authentication settings
    jwt_secret_key: SecretStr = SecretStr(
        "development-only-secret-change-before-production"
    )

    jwt_algorithm: Literal["HS256"] = "HS256"

    access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        le=1440,
    )

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        """Reject known development secrets in production."""

        secret = self.jwt_secret_key.get_secret_value()

        if self.app_env == "production":
            if (
                secret
                in {
                    "development-only-secret-change-before-production",
                    "replace-with-a-random-secret-before-production",
                }
                or len(secret) < 32
            ):
                raise ValueError(
                    "Production requires a JWT secret with at least "
                    "32 characters. Configure JWT_SECRET_KEY securely."
                )

        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()