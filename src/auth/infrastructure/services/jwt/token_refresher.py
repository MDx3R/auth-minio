from auth.application.dtos.models.token import TokenPair
from auth.application.exceptions import TokenExpiredError, TokenRevokedError
from auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from auth.application.interfaces.services.token_service import ITokenRefresher
from auth.infrastructure.services.jwt.token_issuer import JWTTokenIssuer
from auth.infrastructure.services.jwt.token_revoker import JWTTokenRevoker
from common.domain.clock import IClock


class JWTTokenRefresher(ITokenRefresher):
    def __init__(
        self,
        token_issuer: JWTTokenIssuer,
        token_revoker: JWTTokenRevoker,
        clock: IClock,
        refresh_token_repository: IRefreshTokenRepository,
    ) -> None:
        self.token_issuer = token_issuer
        self.token_revoker = token_revoker
        self.clock = clock
        self.refresh_token_repository = refresh_token_repository

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        token = await self.refresh_token_repository.get(refresh_token)
        if token.is_expired(self.clock.now().value):
            raise TokenExpiredError()
        if token.is_revoked():
            raise TokenRevokedError()

        await self.token_revoker.revoke_refresh_token(refresh_token)
        return await self.token_issuer.issue_tokens(token.user_id)
