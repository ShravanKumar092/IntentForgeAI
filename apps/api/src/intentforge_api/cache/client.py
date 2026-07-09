from redis.asyncio import Redis

from intentforge_api.core.config import Settings


def create_redis_client(settings: Settings) -> Redis:
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_database,
        socket_connect_timeout=settings.redis_timeout_seconds,
        socket_timeout=settings.redis_timeout_seconds,
        decode_responses=True,
        health_check_interval=30,
        max_connections=10,
    )
