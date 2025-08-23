from abc import ABC, abstractmethod
from uuid import UUID

from identity.domain.value_objects.descriptor import UserDescriptor


class IUserDescriptorRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserDescriptor: ...
