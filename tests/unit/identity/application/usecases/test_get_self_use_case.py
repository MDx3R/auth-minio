from unittest.mock import Mock
from uuid import uuid4

import pytest

from identity.application.dtos.queries.get_user_be_id_query import (
    GetUserByIdQuery,
)
from identity.application.dtos.responses.user_dto import UserDTO
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.application.usecases.query.get_self_use_case import (
    GetSelfUseCase,
)
from identity.domain.entity.user import User


@pytest.mark.asyncio
class TestGetSelfUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.user = User(self.user_id, "test user", "hash")

        self.user_repository = Mock(spec=IUserRepository)
        self.user_repository.get_by_id.return_value = self.user

        self.command = GetUserByIdQuery(self.user_id)
        self.use_case = GetSelfUseCase(self.user_repository)

    async def test_execute_success(self):
        result = await self.use_case.execute(self.command)

        assert isinstance(result, UserDTO)
        assert result.user_id == self.user_id
        assert result.username == self.user.username

        self.user_repository.get_by_id.assert_awaited_once_with(
            self.user.user_id
        )
