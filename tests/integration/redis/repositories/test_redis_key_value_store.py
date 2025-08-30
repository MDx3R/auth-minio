import asyncio
from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from marshmallow import Schema
from redis.asyncio import Redis

from auth.infrastructure.serializers.marshmallow.shemas import (
    UserDescriptorSchema,
)
from common.application.exceptions import NotFoundError
from common.infrastructure.database.redis.repositories.key_value_store import (
    RedisKeyValueStore,
)
from common.infrastructure.serializers.marshmallow.serializer import (
    MarshmallowSerializer,
)
from identity.application.read_models.user_read_model import UserReadModel
from identity.domain.value_objects.descriptor import UserDescriptor
from identity.infrastructure.serializers.marshmallow.shemas import (
    UserReadModelSchema,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "model_cls,schema_cls,instance",
    [
        (
            UserDescriptor,
            UserDescriptorSchema,
            lambda: UserDescriptor(user_id=uuid4(), username="testuser"),
        ),
        (
            UserReadModel,
            UserReadModelSchema,
            lambda: UserReadModel(user_id=uuid4(), username="readuser"),
        ),
    ],
    ids=["UserDescriptor", "UserReadModel"],
)
class TestRedisKeyValueStoreGeneric:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        redis_client: Redis,
        model_cls: Any,
        schema_cls: type[Schema],
        instance: Callable[..., Any],
    ):
        self.redis_client = redis_client
        self.schema = schema_cls()
        self.serializer = MarshmallowSerializer[model_cls](schema=self.schema)
        self.store = RedisKeyValueStore(
            redis_client=self.redis_client,
            serializer=self.serializer,
            namespace="test:user",
        )
        self.instance = instance()
        self.key = self.store.make_key(str(self.instance.user_id))

    async def test_set_and_get_success(self):
        # Act
        await self.store.set(
            str(self.instance.user_id), self.instance, expire=300
        )

        # Assert
        result = await self.store.get(str(self.instance.user_id))
        assert result == self.instance
        assert result.user_id == self.instance.user_id
        assert result.username == self.instance.username
        assert await self.redis_client.exists(self.key)

    async def test_get_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.store.get("non_existent_key")

    async def test_set_with_ttl(self):
        await self.store.set(
            str(self.instance.user_id), self.instance, expire=1
        )

        # Assert
        result = await self.store.get(str(self.instance.user_id))
        assert result == self.instance

        # TTL expiration
        await asyncio.sleep(2)
        with pytest.raises(NotFoundError):
            await self.store.get(str(self.instance.user_id))
