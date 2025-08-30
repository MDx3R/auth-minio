from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from common.application.exceptions import NotFoundError, RepositoryError
from common.application.interfaces.repositories.key_value_store import (
    IKeyValueStore,
)
from common.infrastructure.database.repositories.key_value_cache import (
    TTLKeyValueCache,
)
from identity.domain.value_objects.descriptor import UserDescriptor


@pytest.mark.asyncio
class TestTTLKeyValueCache:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.store = AsyncMock(spec=IKeyValueStore)
        self.ttl = 300
        self.cache = TTLKeyValueCache[UserDescriptor](self.store, self.ttl)
        self.user_id = uuid4()
        self.descriptor = UserDescriptor(
            user_id=self.user_id, username="testuser"
        )
        self.key = "test:key"

    async def test_get_success(self):
        # Arrange
        self.store.get.return_value = self.descriptor

        # Act
        result = await self.cache.get(self.key)

        # Assert
        assert result == self.descriptor
        self.store.get.assert_awaited_once_with(self.key)

    async def test_get_not_found_returns_none(self):
        # Arrange
        self.store.get.side_effect = NotFoundError(self.key)

        # Act
        result = await self.cache.get(self.key)

        # Assert
        assert result is None
        self.store.get.assert_awaited_once_with(self.key)

    async def test_get_repository_error_returns_none(self):
        # Arrange
        self.store.get.side_effect = RepositoryError("Storage error")

        # Act
        result = await self.cache.get(self.key)

        # Assert
        assert result is None
        self.store.get.assert_awaited_once_with(self.key)

    async def test_get_or_raise_success(self):
        # Arrange
        self.store.get.return_value = self.descriptor

        # Act
        result = await self.cache.get_or_raise(self.key)

        # Assert
        assert result == self.descriptor
        self.store.get.assert_awaited_once_with(self.key)

    async def test_get_or_raise_not_found(self):
        # Arrange
        self.store.get.side_effect = NotFoundError(self.key)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.cache.get_or_raise(self.key)
        self.store.get.assert_awaited_once_with(self.key)

    async def test_get_or_raise_repository_error(self):
        # Arrange
        self.store.get.side_effect = RepositoryError("Storage error")

        # Act & Assert
        with pytest.raises(RepositoryError, match="Storage error"):
            await self.cache.get_or_raise(self.key)
        self.store.get.assert_awaited_once_with(self.key)

    async def test_set_success(self):
        # Act
        await self.cache.set(self.key, self.descriptor)

        # Assert
        self.store.set.assert_awaited_once_with(
            self.key, self.descriptor, self.ttl
        )

    async def test_set_repository_error_swallowed(self):
        # Arrange
        self.store.set.side_effect = RepositoryError("Storage error")

        # Act
        await self.cache.set(self.key, self.descriptor)

        # Assert
        self.store.set.assert_awaited_once_with(
            self.key, self.descriptor, self.ttl
        )

    async def test_set_or_raise_success(self):
        # Act
        await self.cache.set_or_raise(self.key, self.descriptor)

        # Assert
        self.store.set.assert_awaited_once_with(
            self.key, self.descriptor, self.ttl
        )

    async def test_set_or_raise_repository_error(self):
        # Arrange
        self.store.set.side_effect = RepositoryError("Storage error")

        # Act & Assert
        with pytest.raises(RepositoryError, match="Storage error"):
            await self.cache.set_or_raise(self.key, self.descriptor)
        self.store.set.assert_awaited_once_with(
            self.key, self.descriptor, self.ttl
        )

    async def test_make_key_single_part(self):
        # Act
        result = self.cache.make_key("part1")

        # Assert
        assert result == "part1"

    async def test_make_key_multiple_parts(self):
        # Act
        result = self.cache.make_key("part1", "part2", "part3")

        # Assert
        assert result == "part1:part2:part3"
