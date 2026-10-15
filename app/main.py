"""Application factory and API entry point for Forgetting Curve."""

from fastapi import FastAPI

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.concept import router as concepts_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "A personal knowledge-retention API built "
            "with spaced repetition."
        ),
        version="0.1.0",
    )

    # Register authentication endpoints.
    app.include_router(
        auth_router,
        prefix=settings.api_v1_prefix,
    )

    # Register concept management endpoints.
    app.include_router(
        concepts_router,
        prefix=settings.api_v1_prefix,
    )

    @app.get(
        "/health",
        tags=["health"],
        summary="Check whether the API is running",
    )
    def health_check() -> dict[str, str]:
        """Return the API health status."""

        return {"status": "ok"}

    return app


app = create_app()