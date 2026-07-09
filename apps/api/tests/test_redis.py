import pytest
from pydantic import ValidationError
from redis.asyncio import Redis

from intentforge_api.cache.connection import RedisConnectivityError, probe_redis_connection
from intentforge_api.cache.client import create_redis_client
from intentforge_api.cache.namespace import build_redis_key
from intentforge_api.core.config import Settings


def test_redis_configuration_defaults_and_url_derivation() -> None:
    settings = Settings(_env_file=None)

    assert settings.redis_host == "127.0.0.1"
    assert settings.redis_port == 6379
    assert settings.redis_database == 0
    assert settings.redis_timeout_seconds == 5.0
    assert settings.redis_url.drivername == "redis"
    assert settings.redis_url.host == "127.0.0.1"
    assert settings.redis_url.port == 6379
    assert settings.redis_url.database == "0"


def test_redis_configuration_validation_is_enforced() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, redis_port=0)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, redis_database=-1)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, redis_timeout_seconds=0)


def test_redis_client_is_derived_from_settings() -> None:
    settings = Settings(
        _env_file=None,
        redis_host="cache.internal",
        redis_port=6380,
        redis_database=3,
        redis_timeout_seconds=2.5,
    )

    client = create_redis_client(settings)

    assert isinstance(client, Redis)
    assert client.connection_pool.connection_kwargs["host"] == "cache.internal"
    assert client.connection_pool.connection_kwargs["port"] == 6380
    assert client.connection_pool.connection_kwargs["db"] == 3
    assert client.connection_pool.connection_kwargs["socket_connect_timeout"] == 2.5
    assert client.connection_pool.connection_kwargs["socket_timeout"] == 2.5
    assert client.connection_pool.connection_kwargs["decode_responses"] is True


def test_redis_key_namespace_is_deterministic() -> None:
    settings = Settings(_env_file=None, app_environment="testing")

    assert build_redis_key(settings, "queue", "job-123") == "intentforge:testing:queue:job-123"


def test_redis_key_namespace_rejects_invalid_segments() -> None:
    settings = Settings(_env_file=None)

    with pytest.raises(ValueError):
        build_redis_key(settings, "", "job-123")

    with pytest.raises(ValueError):
        build_redis_key(settings, "queue", "bad:key")


class _SuccessfulRedisClient:
    async def ping(self) -> bool:
        return True


class _FailingRedisClient:
    async def ping(self) -> bool:
        raise ConnectionError("boom")


@pytest.mark.asyncio
async def test_redis_probe_succeeds_with_ping() -> None:
    await probe_redis_connection(_SuccessfulRedisClient())


@pytest.mark.asyncio
async def test_redis_probe_failure_is_explicit() -> None:
    with pytest.raises(RedisConnectivityError):
        await probe_redis_connection(_FailingRedisClient())
