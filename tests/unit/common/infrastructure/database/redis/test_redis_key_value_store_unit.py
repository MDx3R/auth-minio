from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from redis import RedisError

from common.application.exceptions import RepositoryError
from common.infrastructure.database.redis.repositories.key_value_store import (
    RedisKeyValueStore,
)
from common.infrastructure.exceptions import SerializationError
from common.infrastructure.serializers.marshmallow.serializer import (
    MarshmallowSerializer,
)
from identity.domain.value_objects.descriptor import UserDescriptor


@pytest.mark.asyncio
class TestRedisKeyValueStoreUnit:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.redis_client = AsyncMock()
        self.serializer = Mock(spec=MarshmallowSerializer)

        self.store = RedisKeyValueStore[UserDescriptor](
            redis_client=self.redis_client,
            serializer=self.serializer,
            namespace="test",
        )
        self.user_id = uuid4()
        self.descriptor = UserDescriptor(
            user_id=self.user_id, username="testuser"
        )

        self.key = self.store.make_key(str(self.user_id))
        self.serialized_data = (
            '{"user_id": "' + str(self.user_id) + '", "username": "testuser"}'
        )

    async def test_get_success(self):
        # Arrange
        self.redis_client.get.return_value = self.serialized_data
        self.serializer.deserialize.return_value = self.descriptor

        # Act
        result = await self.store.get(str(self.user_id))

        # Assert
        assert result == self.descriptor
        assert result.user_id == self.descriptor.user_id
        assert result.username == self.descriptor.username
        self.redis_client.get.assert_awaited_once_with(self.key)
        self.serializer.deserialize.assert_called_once_with(
            self.serialized_data
        )

    async def test_set_success(self):
        # Arrange
        self.serializer.serialize.return_value = self.serialized_data
        self.redis_client.set.return_value = True

        # Act
        await self.store.set(str(self.user_id), self.descriptor, expire=300)

        # Assert
        self.serializer.serialize.assert_called_once_with(self.descriptor)
        self.redis_client.set.assert_awaited_once_with(
            self.key, self.serialized_data, ex=300
        )

    async def test_set_success_without_ttl(self):
        # Arrange
        self.serializer.serialize.return_value = self.serialized_data
        self.redis_client.set.return_value = True

        # Act
        await self.store.set(str(self.user_id), self.descriptor)

        # Assert
        self.serializer.serialize.assert_called_once_with(self.descriptor)
        self.redis_client.set.assert_awaited_once_with(
            self.key, self.serialized_data, ex=None
        )

    async def test_get_with_serialization_error(self):
        # Arrange
        self.redis_client.get.return_value = self.serialized_data
        self.serializer.deserialize.side_effect = SerializationError(
            "Deserialization failed"
        )

        # Act & Assert
        with pytest.raises(
            RepositoryError, match="Unnable to retrive value cache"
        ):
            await self.store.get(str(self.user_id))

        self.redis_client.get.assert_awaited_once_with(self.key)
        self.serializer.deserialize.assert_called_once_with(
            self.serialized_data
        )

    async def test_set_with_serialization_error(self):
        # Arrange
        self.serializer.serialize.side_effect = SerializationError(
            "Serialization failed"
        )

        # Act & Assert
        with pytest.raises(
            RepositoryError, match="Unnable to save value in cache"
        ):
            await self.store.set(
                str(self.user_id), self.descriptor, expire=300
            )
        self.serializer.serialize.assert_called_once_with(self.descriptor)
        self.redis_client.set.assert_not_awaited()

    async def test_get_with_redis_error(self):
        # Arrange
        self.redis_client.get.side_effect = RedisError(
            "Redis connection error"
        )

        # Act & Assert
        with pytest.raises(
            RepositoryError, match="Unnable to retrive value cache"
        ):
            await self.store.get(str(self.user_id))
        self.redis_client.get.assert_awaited_once_with(self.key)
        self.serializer.deserialize.assert_not_called()

    async def test_set_with_redis_error(self):
        # Arrange
        self.serializer.serialize.return_value = self.serialized_data
        self.redis_client.set.side_effect = RedisError(
            "Redis connection error"
        )

        # Act & Assert
        with pytest.raises(
            RepositoryError, match="Unnable to save value in cache"
        ):
            await self.store.set(
                str(self.user_id), self.descriptor, expire=300
            )
        self.serializer.serialize.assert_called_once_with(self.descriptor)
        self.redis_client.set.assert_awaited_once_with(
            self.key, self.serialized_data, ex=300
        )
