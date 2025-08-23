from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from jose import jwt

from auth.application.dtos.models.token import Token, TokenPair, TokenTypeEnum
from auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from auth.application.interfaces.services.token_service import ITokenIssuer
from auth.infrastructure.services.jwt.claims import TokenClaims
from common.domain.clock import IClock
from common.domain.token_generator import ITokenGenerator
from common.domain.uuid_generator import IUUIDGenerator
from common.infrastructure.config.auth_config import AuthConfig


class JWTTokenIssuer(ITokenIssuer):
    def __init__(
        self,
        config: AuthConfig,
        token_generator: ITokenGenerator,
        uuid_generator: IUUIDGenerator,
        clock: IClock,
        refresh_token_repository: IRefreshTokenRepository,
    ) -> None:
        self.config = config
        self.clock = clock
        self.token_generator = token_generator
        self.uuid_generator = uuid_generator
        self.refresh_token_repository = refresh_token_repository

    async def issue_tokens(self, user_id: UUID) -> TokenPair:
        access = self.issue_access_token(user_id)
        refresh = self.issue_refresh_token(user_id)

        await self.refresh_token_repository.add(refresh)

        return TokenPair.create(access, refresh)

    def issue_access_token(self, user_id: UUID) -> Token:
        issued_at = self.clock.now().value
        expires_at = self.expires_at(issued_at, self.config.ACCESS_TOKEN_TTL)

        claims = TokenClaims.create(
            user_id, self.config.ISSUER, issued_at, expires_at
        )
        token_str = self.create_jwt_token(claims)

        return Token.create(
            token_id=self.uuid_generator.create(),
            user_id=user_id,
            value=token_str,
            token_type=TokenTypeEnum.ACCESS,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def issue_refresh_token(self, user_id: UUID) -> Token:
        issued_at = self.clock.now().value
        expires_at = self.expires_at(issued_at, self.config.REFRESH_TOKEN_TTL)

        token_value = self.token_generator.secure(64)

        refresh_token = Token.create(
            token_id=self.uuid_generator.create(),
            user_id=user_id,
            value=token_value,
            token_type=TokenTypeEnum.REFRESH,
            issued_at=issued_at,
            expires_at=expires_at,
        )

        return refresh_token

    def create_jwt_token(self, claims: TokenClaims) -> str:
        payload: dict[str, Any] = {
            "sub": str(claims.sub),
            "iss": claims.iss,
            "iat": int(claims.iat.timestamp()),
            "exp": int(claims.exp.timestamp()),
        }
        return jwt.encode(
            payload,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM,
        )

    def expires_at(self, issued_at: datetime, ttl: timedelta) -> datetime:
        return issued_at + ttl
