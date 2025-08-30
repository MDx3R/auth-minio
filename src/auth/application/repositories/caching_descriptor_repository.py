from uuid import UUID

from auth.application.interfaces.repositories.descriptor_repository import (
    IUserDescriptorRepository,
)
from common.application.repositories.key_value_cache import KeyValueCache
from identity.domain.value_objects.descriptor import UserDescriptor


class CachingUserDescriptorRepository(IUserDescriptorRepository):
    def __init__(
        self,
        user_descriptor_repository: IUserDescriptorRepository,
        key_value_cache: KeyValueCache[UserDescriptor],
    ) -> None:
        self.user_descriptor_repository = user_descriptor_repository
        self.key_value_cache = key_value_cache

    async def get_by_id(self, user_id: UUID) -> UserDescriptor:
        key = self.key_value_cache.make_key(str(user_id), "descriptor")

        cached = await self.key_value_cache.get(key)
        if cached:
            return cached

        descriptor = await self.user_descriptor_repository.get_by_id(user_id)

        await self.key_value_cache.set(key, descriptor)
        return descriptor
