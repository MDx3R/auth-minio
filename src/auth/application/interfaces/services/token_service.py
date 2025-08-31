from abc import ABC, abstractmethod
from uuid import UUID

from auth.application.dtos.models.auth_tokens import AuthTokens
from identity.domain.value_objects.descriptor import UserDescriptor


class ITokenIssuer(ABC):
    @abstractmethod
    async def issue_tokens(self, user_id: UUID) -> AuthTokens: ...


class ITokenRefresher(ABC):
    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> AuthTokens: ...


class ITokenIntrospector(ABC):
    @abstractmethod
    async def extract_user(self, token: str) -> UserDescriptor: ...
    @abstractmethod
    async def is_token_valid(self, token: str) -> bool: ...
    @abstractmethod
    async def validate(self, token: str) -> UUID: ...


class ITokenRevoker(ABC):
    @abstractmethod
    async def revoke_refresh_token(self, refresh_token: str) -> None: ...
