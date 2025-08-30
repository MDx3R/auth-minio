from abc import ABC, abstractmethod
from uuid import UUID

from identity.application.read_models.user_read_model import UserReadModel


class IUserReadRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserReadModel: ...
