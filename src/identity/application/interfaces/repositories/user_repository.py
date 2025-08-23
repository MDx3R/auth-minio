from abc import ABC, abstractmethod
from uuid import UUID

from identity.domain.entity.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User: ...
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool: ...
    @abstractmethod
    async def get_by_username(self, username: str) -> User: ...
    @abstractmethod
    async def add(self, entity: User) -> None: ...
