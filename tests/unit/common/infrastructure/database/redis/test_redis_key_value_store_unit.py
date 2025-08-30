from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from redis import RedisError

from common.application.exceptions import RepositoryError
from common.infrastructure.database.redis.repositories.key_value_store import (
    RedisKeyValueStore,
)
from common.infrastructure.exceptions import SerializationError
from common.infrastructure.serializers.serializer import ISerializer


@pytest.mark.asyncio
class TestRedisKeyValueStoreUnit:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.redis_client = AsyncMock()
        self.serializer = Mock(spec=ISerializer)

        self.store = RedisKeyValueStore[UUID](
            redis_client=self.redis_client,
            serializer=self.serializer,
            namespace="test",
        )
        self.id = uuid4()

        self.key = self.store.make_key(str(self.id))
        self.serialized_data = f"'{self.id!s}'"

    async def test_get_success(self):
        # Arrange
        self.redis_client.get.return_value = self.serialized_data
        self.serializer.deserialize.return_value = self.id

        # Act
        result = await self.store.get(str(self.id))

        # Assert
        assert result == self.id

        self.redis_client.get.assert_awaited_once_with(self.key)
        self.serializer.deserialize.assert_called_once_with(
            self.serialized_data
        )

    async def test_set_success(self):
        # Arrange
        self.serializer.serialize.return_value = self.serialized_data
        self.redis_client.set.return_value = True

        # Act
        await self.store.set(str(self.id), self.id, expire=300)

        # Assert
        self.serializer.serialize.assert_called_once_with(self.id)
        self.redis_client.set.assert_awaited_once_with(
            self.key, self.serialized_data, ex=300
        )

    async def test_set_success_without_ttl(self):
        # Arrange
        self.serializer.serialize.return_value = self.serialized_data
        self.redis_client.set.return_value = True

        # Act
        await self.store.set(str(self.id), self.id)

        # Assert
        self.serializer.serialize.assert_called_once_with(self.id)
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
            await self.store.get(str(self.id))

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
            await self.store.set(str(self.id), self.id, expire=300)
        self.serializer.serialize.assert_called_once_with(self.id)
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
            await self.store.get(str(self.id))
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
            await self.store.set(str(self.id), self.id, expire=300)
        self.serializer.serialize.assert_called_once_with(self.id)
        self.redis_client.set.assert_awaited_once_with(
            self.key, self.serialized_data, ex=300
        )
