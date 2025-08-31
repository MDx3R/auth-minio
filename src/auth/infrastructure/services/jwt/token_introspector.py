from typing import Any
from uuid import UUID

from jose import ExpiredSignatureError, JWTError, jwt

from auth.application.exceptions import InvalidTokenError, TokenExpiredError
from auth.application.interfaces.repositories.descriptor_repository import (
    IUserDescriptorRepository,
)
from auth.application.interfaces.services.token_service import (
    ITokenIntrospector,
)
from auth.infrastructure.services.jwt.claims import TokenClaims
from common.application.exceptions import (
    NotFoundError,
    RepositoryError,
)
from common.domain.clock import IClock
from common.infrastructure.config.auth_config import AuthConfig
from identity.domain.value_objects.descriptor import UserDescriptor


class JWTTokenIntrospector(ITokenIntrospector):
    def __init__(
        self,
        config: AuthConfig,
        clock: IClock,
        user_descriptor_repository: IUserDescriptorRepository,
    ) -> None:
        self.config = config
        self.clock = clock
        self.user_descriptor_repository = user_descriptor_repository

    async def extract_user(self, token: str) -> UserDescriptor:
        claims = self.decode(token)
        try:
            return await self.user_descriptor_repository.get_by_id(
                claims.user_id
            )
        except NotFoundError as e:
            raise RepositoryError(
                f"decoded user_id {claims.user_id} is not found"
            ) from e

    async def is_token_valid(self, token: str) -> bool:
        try:
            await self.validate(token)
            return True
        except Exception:
            return False

    async def validate(self, token: str) -> UUID:
        return self.decode(token).user_id

    def decode(self, token: str) -> TokenClaims:
        try:
            payload = jwt.decode(
                token,
                key=self.config.secret_key,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
                options={"require": ["exp", "iat", "sub"]},
            )

            return self._parse_claims(payload)

        except ExpiredSignatureError as e:
            raise TokenExpiredError from e
        except JWTError as e:
            raise InvalidTokenError from e

    def _parse_claims(self, payload: dict[str, Any]) -> TokenClaims:
        try:
            return TokenClaims(
                sub=UUID(payload["sub"]),
                iss=payload["iss"],
                iat=self.clock.from_timestamp(payload["iat"]).value,
                exp=self.clock.from_timestamp(payload["exp"]).value,
            )
        except Exception as e:
            raise InvalidTokenError("Malformed token claims") from e
