from unittest.mock import AsyncMock, Mock

import pytest

from auth.application.dtos.commands.logout_command import LogoutCommand
from auth.application.interfaces.services.token_service import ITokenRevoker
from auth.application.usecases.command.logout_use_case import LogoutUseCase


@pytest.mark.asyncio
class TestLogoutUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.token_revoker = Mock(spec=ITokenRevoker)
        self.token_revoker.revoke_refresh_token = AsyncMock()

        self.command = LogoutCommand(refresh_token="refresh_token")
        self.use_case = LogoutUseCase(self.token_revoker)

    async def test_logout_success(self):
        await self.use_case.execute(self.command)
        self.token_revoker.revoke_refresh_token.assert_awaited_once_with(
            "refresh_token"
        )
