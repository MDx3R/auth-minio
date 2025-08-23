from abc import ABC, abstractmethod

from auth.application.dtos.models.token import Token


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def get(self, value: str) -> Token: ...
    @abstractmethod
    async def revoke(self, value: str) -> None: ...
    @abstractmethod
    async def add(self, token: Token) -> None: ...
