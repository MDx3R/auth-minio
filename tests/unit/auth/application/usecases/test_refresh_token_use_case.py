from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from auth.application.dtos.commands.refresh_token_command import (
    RefreshTokenCommand,
)
from auth.application.dtos.models.auth_tokens import AuthTokens
from auth.application.interfaces.services.token_service import ITokenRefresher
from auth.application.usecases.command.refresh_token_use_case import (
    RefreshTokenUseCase,
)


@pytest.mark.asyncio
class TestRefreshTokenUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.tokens = AuthTokens(uuid4(), "access_token", "new_refresh_token")

        self.token_refresher = Mock(spec=ITokenRefresher)
        self.token_refresher.refresh_tokens = AsyncMock(
            return_value=self.tokens
        )

        self.command = RefreshTokenCommand(refresh_token="refresh_token")
        self.use_case = RefreshTokenUseCase(self.token_refresher)

    async def test_refresh_token_success(self):
        result = await self.use_case.execute(self.command)

        assert isinstance(result, AuthTokens)
        assert result.access_token == "access_token"
        assert result.refresh_token == "new_refresh_token"

        self.token_refresher.refresh_tokens.assert_awaited_once_with(
            "refresh_token"
        )
