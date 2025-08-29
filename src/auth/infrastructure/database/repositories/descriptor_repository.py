from uuid import UUID

from auth.application.interfaces.repositories.descriptor_repository import (
    IUserDescriptorRepository,
)
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.domain.value_objects.descriptor import UserDescriptor


class UserDescriptorRepository(IUserDescriptorRepository):
    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def get_by_id(self, user_id: UUID) -> UserDescriptor:
        user = await self.user_repository.get_by_id(user_id)
        return user.descriptor()
