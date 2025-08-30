from typing import Self

from redis.asyncio import Redis

from common.infrastructure.config.redis_config import RedisConfig


class RedisDatabase:
    def __init__(self, redis: Redis):
        self._redis = redis

    @classmethod
    async def create(cls, config: RedisConfig) -> Self:
        redis = await cls.create_redis_client(config)
        return cls(redis=redis)

    @staticmethod
    async def create_redis_client(config: RedisConfig) -> Redis:
        return Redis(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            decode_responses=True,
        )

    def get_client(self) -> Redis:
        return self._redis

    async def shutdown(self) -> None:
        await self._redis.aclose()
