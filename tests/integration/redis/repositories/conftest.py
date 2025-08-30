import pytest
import pytest_asyncio
from redis.asyncio import Redis
from testcontainers.redis import RedisContainer  # type: ignore

from common.infrastructure.config.redis_config import RedisConfig


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7") as redis:
        yield redis


@pytest.fixture(scope="session")
def redis_config(redis_container: RedisContainer):
    return RedisConfig(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        db=0,
    )


@pytest_asyncio.fixture
async def redis_client(redis_config: RedisConfig):
    redis = Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        decode_responses=True,
    )
    yield redis
    await redis.flushdb()  # type: ignore
    await redis.aclose()
