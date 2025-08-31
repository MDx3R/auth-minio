from auth.application.dtos.commands.refresh_token_command import (
    RefreshTokenCommand,
)
from auth.application.dtos.models.auth_tokens import AuthTokens
from auth.application.interfaces.services.token_service import ITokenRefresher
from auth.application.interfaces.usecases.command.refresh_token_use_case import (
    IRefreshTokenUseCase,
)


class RefreshTokenUseCase(IRefreshTokenUseCase):
    def __init__(self, token_refresher: ITokenRefresher) -> None:
        self.token_refresher = token_refresher

    async def execute(self, command: RefreshTokenCommand) -> AuthTokens:
        return await self.token_refresher.refresh_tokens(command.refresh_token)
