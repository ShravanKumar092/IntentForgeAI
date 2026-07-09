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
    assert settings.redis_host == "127.0.0.1"
    assert settings.redis_port == 6379
    assert settings.redis_database == 0
    assert settings.redis_timeout_seconds == 5.0
    assert settings.token_signing_secret.get_secret_value() == "change_me"
    assert settings.token_signing_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 15
    assert settings.token_issuer == "intentforge-api"
    assert settings.token_audience == "intentforge-api"
    assert "change_me" not in repr(settings)


def test_environment_values_are_typed() -> None:
    settings = Settings(
        _env_file=None,
        app_environment="production",
        app_debug=False,
        token_signing_secret="super-secret-super-secret-super-secret",
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


@pytest.mark.parametrize("invalid_port", [0, 65536])
def test_invalid_redis_port_is_rejected(invalid_port: int) -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            redis_port=invalid_port,
        )


def test_invalid_redis_database_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            redis_database=-1,
        )


def test_invalid_redis_timeout_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            redis_timeout_seconds=0,
        )


def test_invalid_access_token_lifetime_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            access_token_expire_minutes=0,
        )


def test_production_token_secret_is_required() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_environment="production",
        )


def test_cached_settings_provider_returns_same_instance() -> None:
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()
