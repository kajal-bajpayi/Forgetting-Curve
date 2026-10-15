""" Test for application configuration"""

from app.core.config import Settings

# func to test if we can use testing environemnt
def test_settings_env()-> None:
    settings = Settings(
        _env_file = None,
        app_env="testing",
    )

    assert settings.app_env == "testing"
    assert settings.app_name == "Forgetting Curve API"
    assert settings.api_v1_prefix == "/api/v1"

