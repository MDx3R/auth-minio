from unittest.mock import Mock
from uuid import uuid4

import pytest

from auth.application.interfaces.repositories.descriptor_repository import (
    IUserDescriptorRepository,
)
from auth.application.repositories.caching_descriptor_repository import (
    CachingUserDescriptorRepository,
)
from common.application.repositories.key_value_cache import IKeyValueCache
from identity.domain.value_objects.descriptor import UserDescriptor


@pytest.mark.asyncio
class TestCachingUserDescriptorRepository:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_descriptor_repository = Mock(spec=IUserDescriptorRepository)
        self.key_value_cache = Mock(spec=IKeyValueCache)

        self.repository = CachingUserDescriptorRepository(
            self.user_descriptor_repository, self.key_value_cache
        )

        self.user_id = uuid4()
        self.descriptor = Mock(spec=UserDescriptor)

        self.key = f"{self.user_id}:descriptor"
        self.key_value_cache.make_key.return_value = self.key

    async def test_get_by_id_cache_hit(self):
        # Arrange
        self.key_value_cache.get.return_value = self.descriptor

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.descriptor
        self.key_value_cache.get.assert_awaited_once_with(self.key)
        self.user_descriptor_repository.get_by_id.assert_not_called()

    async def test_get_by_id_cache_miss_fetches_and_caches(self):
        # Arrange
        self.key_value_cache.get.return_value = None
        self.user_descriptor_repository.get_by_id.return_value = (
            self.descriptor
        )

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.descriptor
        self.key_value_cache.get.assert_awaited_once_with(self.key)
        self.user_descriptor_repository.get_by_id.assert_awaited_once_with(
            self.user_id
        )
        self.key_value_cache.set.assert_awaited_once_with(
            self.key, self.descriptor
        )
