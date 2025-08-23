from abc import ABC, abstractmethod
from uuid import UUID

from auth.application.dtos.models.token import TokenPair
from identity.domain.value_objects.descriptor import UserDescriptor


class ITokenIssuer(ABC):
    @abstractmethod
    async def issue_tokens(self, user_id: UUID) -> TokenPair: ...


class ITokenRefresher(ABC):
    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> TokenPair: ...


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
