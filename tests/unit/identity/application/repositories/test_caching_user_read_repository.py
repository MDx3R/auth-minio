from unittest.mock import Mock
from uuid import uuid4

import pytest

from common.application.repositories.key_value_cache import KeyValueCache
from identity.application.interfaces.repositories.user_read_repository import (
    IUserReadRepository,
)
from identity.application.read_models.user_read_model import UserReadModel
from identity.application.repositories.caching_user_read_repository import (
    CachingUserReadRepository,
)


@pytest.mark.asyncio
class TestCachingUserReadModelRepository:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_read_repository = Mock(spec=IUserReadRepository)
        self.key_value_cache = Mock(spec=KeyValueCache)

        self.repository = CachingUserReadRepository(
            self.user_read_repository, self.key_value_cache
        )

        self.user_id = uuid4()
        self.user = Mock(spec=UserReadModel)

        self.key = f"{self.user_id}"
        self.key_value_cache.make_key.return_value = self.key

    async def test_get_by_id_cache_hit(self):
        # Arrange
        self.key_value_cache.get.return_value = self.user

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.user
        self.key_value_cache.get.assert_awaited_once_with(self.key)
        self.user_read_repository.get_by_id.assert_not_called()

    async def test_get_by_id_cache_miss_fetches_and_caches(self):
        # Arrange
        self.key_value_cache.get.return_value = None
        self.user_read_repository.get_by_id.return_value = self.user

        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.user
        self.key_value_cache.get.assert_awaited_once_with(self.key)
        self.user_read_repository.get_by_id.assert_awaited_once_with(
            self.user_id
        )
        self.key_value_cache.set.assert_awaited_once_with(self.key, self.user)
