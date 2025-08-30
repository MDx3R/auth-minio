from redis import RedisError
from redis.asyncio import Redis

from common.application.exceptions import NotFoundError, RepositoryError
from common.application.interfaces.repositories.key_value_store import (
    IKeyValueStore,
    T,
)
from common.infrastructure.exceptions import SerializationError
from common.infrastructure.serializers.serializer import ISerializer


class RedisKeyValueStore(IKeyValueStore[T]):
    def __init__(
        self,
        redis_client: Redis,
        serializer: ISerializer[T],
        namespace: str = "",
    ):
        self.redis = redis_client
        self.serializer = serializer
        self.namespace = namespace.rstrip(":")

    def make_key(self, key: str) -> str:
        if self.namespace:
            return f"{self.namespace}:{key}"
        return key

    async def get(self, key: str) -> T:
        key = self.make_key(key)
        try:
            data = await self.redis.get(key)
            if not data:
                raise NotFoundError(key)
            return self.serializer.deserialize(data)
        except (RedisError, SerializationError) as e:
            raise RepositoryError("Unnable to retrive value cache") from e

    async def set(self, key: str, value: T, expire: int | None = None) -> None:
        key = self.make_key(key)
        try:
            payload = self.serializer.serialize(value)
            await self.redis.set(key, payload, ex=expire)
        except (RedisError, SerializationError) as e:
            raise RepositoryError("Unnable to save value in cache") from e
