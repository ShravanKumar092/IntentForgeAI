from redis.asyncio import Redis
from redis.exceptions import RedisError


class RedisConnectivityError(RuntimeError):
    pass


async def probe_redis_connection(client: Redis) -> None:
    try:
        if not await client.ping():
            raise RedisConnectivityError("redis connectivity check returned an unexpected result")
    except (OSError, RedisError) as exc:
        raise RedisConnectivityError("redis connectivity check failed") from exc
