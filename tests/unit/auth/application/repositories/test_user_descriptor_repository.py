from unittest.mock import Mock
from uuid import uuid4

import pytest

from auth.application.repositories.descriptor_repository import (
    UserDescriptorRepository,
)
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.domain.entity.user import User


@pytest.mark.asyncio
class TestUserDescriptorRepository:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_repository = Mock(spec=IUserRepository)
        self.repository = UserDescriptorRepository(self.user_repository)
        self.user_id = uuid4()
        self.user = User(uuid4(), "username", "hash")
        self.user_repository.get_by_id.return_value = self.user

    async def test_get_by_id_success(self):
        # Act
        result = await self.repository.get_by_id(self.user_id)

        # Assert
        assert result == self.user.descriptor()
        self.user_repository.get_by_id.assert_awaited_once_with(self.user_id)
