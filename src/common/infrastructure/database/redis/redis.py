import logging
from typing import Self

from redis.asyncio import Redis

from common.infrastructure.config.redis_config import RedisConfig


class RedisDatabase:
    def __init__(self, redis: Redis, logger: logging.Logger):
        self._redis = redis
        self._logger = logger

    @classmethod
    def create(
        cls, config: RedisConfig, logger: logging.Logger | None = None
    ) -> Self:
        redis = cls.create_redis_client(config)
        return cls(redis=redis, logger=logger or logging.getLogger())

    @staticmethod
    def create_redis_client(config: RedisConfig) -> Redis:
        return Redis(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            decode_responses=True,
        )

    def get_client(self) -> Redis:
        return self._redis

    async def flush_db(self) -> None:
        await self._redis.flushdb()  # type: ignore

    async def shutdown(self) -> None:
        self._logger.info("closing redis connection...")
        await self._redis.aclose()
        self._logger.info("redis connection closed gracefully")
