from auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from auth.application.interfaces.services.token_service import ITokenRevoker
from common.domain.clock import IClock


class JWTTokenRevoker(ITokenRevoker):
    def __init__(
        self, clock: IClock, refresh_token_repository: IRefreshTokenRepository
    ) -> None:
        self.clock = clock
        self.refresh_token_repository = refresh_token_repository

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        token = await self.refresh_token_repository.get(refresh_token)
        if token.is_expired(self.clock.now().value):
            return
        if token.is_revoked():
            return

        await self.refresh_token_repository.revoke(refresh_token)
