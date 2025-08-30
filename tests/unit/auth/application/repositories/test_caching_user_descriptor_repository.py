from unittest.mock import Mock
from uuid import uuid4

import pytest

from auth.application.interfaces.repositories.descriptor_repository import (
    IUserDescriptorRepository,
)
from auth.application.repositories.caching_descriptor_repository import (
    CachingUserDescriptorRepository,
)
from common.application.exceptions import NotFoundError, RepositoryError
from common.application.interfaces.repositories.key_value_store import (
    IKeyValueStore,
)
from identity.domain.value_objects.descriptor import UserDescriptor


@pytest.mark.asyncio
class TestCachingUserDescriptorRepository:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_descriptor_repository = Mock(spec=IUserDescriptorRepository)
        self.key_value_store = Mock(spec=IKeyValueStore)
        self.ttl = 300

        self.repository = CachingUserDescriptorRepository(
            self.user_descriptor_repository, self.key_value_store, self.ttl
        )

        self.user_id = uuid4()
        self.descriptor = Mock(spec=UserDescriptor)
        self.key = f"{self.user_id}:descriptor"

    async def test_get_by_id_cache_hit(self):
        # Arrange
        self.key_value_store.get.return_value = self.descriptor

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.descriptor
        self.key_value_store.get.assert_awaited_once_with(self.key)
        self.user_descriptor_repository.get_by_id.assert_not_called()

    async def test_get_by_id_cache_miss_fetches_and_caches(self):
        # Arrange
        self.key_value_store.get.side_effect = NotFoundError(self.key)
        self.user_descriptor_repository.get_by_id.return_value = (
            self.descriptor
        )

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.descriptor
        self.key_value_store.get.assert_awaited_once_with(self.key)
        self.user_descriptor_repository.get_by_id.assert_awaited_once_with(
            self.user_id
        )
        self.key_value_store.set.assert_awaited_once_with(
            self.key, self.descriptor, self.ttl
        )

    async def test_get_by_id_cache_miss_with_repository_error(self):
        # Arrange
        self.key_value_store.get.side_effect = RepositoryError(self.key)
        self.user_descriptor_repository.get_by_id.return_value = (
            self.descriptor
        )

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.descriptor
        self.key_value_store.get.assert_awaited_once_with(self.key)
        self.user_descriptor_repository.get_by_id.assert_awaited_once_with(
            self.user_id
        )
        self.key_value_store.set.assert_awaited_once_with(
            self.key, self.descriptor, self.ttl
        )

    async def test_get_by_id_cache_set_fails(self):
        # Arrange
        self.key_value_store.get.side_effect = NotFoundError(self.key)
        self.user_descriptor_repository.get_by_id.return_value = (
            self.descriptor
        )
        self.key_value_store.set.side_effect = RepositoryError(self.key)

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.descriptor
        self.key_value_store.get.assert_awaited_once_with(self.key)
        self.user_descriptor_repository.get_by_id.assert_awaited_once_with(
            self.user_id
        )
        self.key_value_store.set.assert_awaited_once_with(
            self.key, self.descriptor, self.ttl
        )
