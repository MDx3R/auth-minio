from uuid import UUID

from common.application.repositories.key_value_cache import IKeyValueCache
from identity.application.interfaces.repositories.user_read_repository import (
    IUserReadRepository,
)
from identity.application.read_models.user_read_model import UserReadModel


class CachingUserReadRepository(IUserReadRepository):
    def __init__(
        self,
        user_read_repository: IUserReadRepository,
        key_value_cache: IKeyValueCache[UserReadModel],
    ) -> None:
        self.user_read_repository = user_read_repository
        self.key_value_cache = key_value_cache

    async def get_by_id(self, user_id: UUID) -> UserReadModel:
        key = self.key_value_cache.make_key(str(user_id))

        cached = await self.key_value_cache.get(key)
        if cached:
            return cached

        user = await self.user_read_repository.get_by_id(user_id)

        await self.key_value_cache.set(key, user)
        return user
