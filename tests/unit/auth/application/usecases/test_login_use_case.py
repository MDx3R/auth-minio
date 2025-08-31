from unittest.mock import Mock
from uuid import uuid4

import pytest

from auth.application.dtos.commands.login_command import LoginCommand
from auth.application.dtos.models.auth_tokens import AuthTokens
from auth.application.exceptions import (
    InvalidPasswordError,
    InvalidUsernameError,
)
from auth.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from auth.application.interfaces.services.token_service import ITokenIssuer
from auth.application.usecases.command.login_use_case import LoginUseCase
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.domain.entity.user import User


@pytest.mark.asyncio
class TestLoginUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.user = User(self.user_id, "test user", "hash")

        self.user_repository = Mock(spec=IUserRepository)
        self.user_repository.get_by_username.return_value = self.user
        self.user_repository.exists_by_username.return_value = True

        self.password_hasher = Mock(spec=IPasswordHasher)
        self.password_hasher.verify = Mock(return_value=True)

        self.token_issuer = Mock(spec=ITokenIssuer)

        self.tokens = AuthTokens(self.user_id, "access_token", "refresh_token")
        self.token_issuer.issue_tokens.return_value = self.tokens

        self.command = LoginCommand(
            username=self.user.username, password="correct_password"
        )
        self.use_case = LoginUseCase(
            self.user_repository, self.password_hasher, self.token_issuer
        )

    async def test_login_success(self):
        result = await self.use_case.execute(self.command)

        assert isinstance(result, AuthTokens)
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"

        self.user_repository.exists_by_username.assert_awaited_once_with(
            self.user.username
        )
        self.user_repository.get_by_username.assert_awaited_once_with(
            self.user.username
        )
        self.password_hasher.verify.assert_called_once_with(
            "correct_password", self.user.password
        )
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)

    async def test_login_invalid_username(self):
        self.user_repository.exists_by_username.return_value = False
        with pytest.raises(InvalidUsernameError):
            await self.use_case.execute(self.command)

    async def test_login_invalid_password(self):
        self.password_hasher.verify.return_value = False
        with pytest.raises(InvalidPasswordError):
            await self.use_case.execute(self.command)
