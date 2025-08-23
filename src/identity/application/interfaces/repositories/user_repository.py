from abc import ABC, abstractmethod
from uuid import UUID

from identity.domain.entity.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User: ...
