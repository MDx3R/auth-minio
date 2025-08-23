from unittest.mock import Mock
from uuid import uuid4

import pytest

from auth.application.dtos.commands.register_user_command import (
    RegisterUserCommand,
)
from auth.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from auth.application.usecases.command.register_user_use_case import (
    RegisterUserUseCase,
)
from identity.application.exceptions import UsernameAlreadyTakenError
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.domain.entity.user import User
from identity.domain.interfaces.user_factory import IUserFactory


@pytest.mark.asyncio
class TestRegisterUserUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.user = User(self.user_id, "test user", "hashed_password")

        self.password_hasher = Mock(spec=IPasswordHasher)
        self.password_hasher.hash.return_value = "hashed_password"

        self.user_factory = Mock(spec=IUserFactory)
        self.user_factory.create.return_value = self.user

        self.user_repository = Mock(spec=IUserRepository)
        self.user_repository.exists_by_username.return_value = False

        self.command = RegisterUserCommand(
            username="test user", password="password"
        )
        self.use_case = RegisterUserUseCase(
            user_factory=self.user_factory,
            user_repository=self.user_repository,
            password_hasher=self.password_hasher,
        )

    async def test_register_success(self):
        result = await self.use_case.execute(self.command)

        assert result == self.user_id

        self.user_repository.exists_by_username.assert_awaited_once_with(
            self.command.username
        )
        self.password_hasher.hash.assert_called_once_with(
            self.command.password
        )
        self.user_repository.add.assert_awaited_once()

    async def test_register_email_already_taken(self):
        self.user_repository.exists_by_username.return_value = True

        with pytest.raises(UsernameAlreadyTakenError):
            await self.use_case.execute(self.command)

        self.user_repository.exists_by_username.assert_awaited_once_with(
            self.command.username
        )
        self.user_repository.add.assert_not_awaited()
