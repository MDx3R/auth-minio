import asyncio
from uuid import uuid4

import pytest
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
from identity.domain.value_objects.descriptor import UserDescriptor


@pytest.mark.asyncio
class TestUserDescriptorRedisKeyValueStore:
    @pytest.fixture(autouse=True)
    def setup(self, redis_client: Redis):
        self.redis_client = redis_client
        self.schema = UserDescriptorSchema()
        self.serializer = MarshmallowSerializer[UserDescriptor](self.schema)

        self.store = RedisKeyValueStore[UserDescriptor](
            redis_client=self.redis_client,
            serializer=self.serializer,
            namespace="test:user",
        )
        self.user_id = uuid4()
        self.descriptor = UserDescriptor(
            user_id=self.user_id, username="testuser"
        )
        self.key = self.store.make_key(str(self.user_id))

    async def test_set_and_get_success(self):
        # Act
        await self.store.set(str(self.user_id), self.descriptor, expire=300)

        # Assert
        result = await self.store.get(str(self.user_id))
        assert result == self.descriptor
        assert result.user_id == self.descriptor.user_id
        assert result.username == self.descriptor.username

        assert await self.redis_client.exists(self.key)

    async def test_get_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.store.get("non_existent_key")

    async def test_set_with_ttl(self):
        # Act
        await self.store.set(str(self.user_id), self.descriptor, expire=1)

        # Assert
        result = await self.store.get(str(self.user_id))
        assert result == self.descriptor

        # Assert
        with pytest.raises(NotFoundError):
            await asyncio.sleep(2)  # Wait for TTL to expire
            await self.store.get(str(self.user_id))
