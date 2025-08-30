from uuid import UUID

from auth.application.interfaces.repositories.descriptor_repository import (
    IUserDescriptorRepository,
)
from common.application.exceptions import NotFoundError, RepositoryError
from common.application.interfaces.repositories.key_value_store import (
    IKeyValueStore,
)
from identity.domain.value_objects.descriptor import UserDescriptor


class CachingUserDescriptorRepository(IUserDescriptorRepository):
    def __init__(
        self,
        user_descriptor_repository: IUserDescriptorRepository,
        key_value_store: IKeyValueStore[UserDescriptor],
        ttl: int = 300,
    ) -> None:
        self.user_descriptor_repository = user_descriptor_repository
        self.key_value_store = key_value_store
        self.ttl = ttl

    async def get_by_id(self, user_id: UUID) -> UserDescriptor:
        key = f"{user_id}:descriptor"

        try:
            cached = await self.key_value_store.get(key)
            if cached:
                return cached
        except (RepositoryError, NotFoundError):
            pass

        descriptor = await self.user_descriptor_repository.get_by_id(user_id)

        try:
            await self.key_value_store.set(key, descriptor, self.ttl)
        except (RepositoryError, NotFoundError):
            pass

        return descriptor
