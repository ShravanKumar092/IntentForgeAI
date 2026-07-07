from pydantic import ValidationError
import pytest

from intentforge_api.core.config import Environment, Settings, get_settings


def test_default_settings_have_expected_runtime_identity() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "IntentForge AI"
    assert settings.app_version == "0.1.0"
    assert settings.app_environment is Environment.DEVELOPMENT
    assert settings.app_debug is True
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8010
    assert settings.log_level == "INFO"


def test_environment_values_are_typed() -> None:
    settings = Settings(
        _env_file=None,
        app_environment="production",
        app_debug=False,
    )

    assert settings.app_environment is Environment.PRODUCTION
    assert settings.is_production is True
    assert settings.app_debug is False


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_environment="invalid-environment",
        )


@pytest.mark.parametrize("invalid_port", [0, 65536])
def test_invalid_api_port_is_rejected(invalid_port: int) -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            api_port=invalid_port,
        )


def test_cached_settings_provider_returns_same_instance() -> None:
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()