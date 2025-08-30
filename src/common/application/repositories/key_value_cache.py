from typing import Generic, TypeVar

from common.application.exceptions import NotFoundError, RepositoryError
from common.application.interfaces.repositories.key_value_store import (
    IKeyValueStore,
)


T = TypeVar("T")


class KeyValueCache(Generic[T]):
    def __init__(self, store: IKeyValueStore[T], ttl: int = 300):
        self.store = store
        self.ttl = ttl

    async def get(self, key: str) -> T | None:
        try:
            return await self.get_or_raise(key)
        except (RepositoryError, NotFoundError):
            return None

    async def get_or_raise(self, key: str) -> T:
        return await self.store.get(key)

    async def set(self, key: str, value: T) -> None:
        try:
            await self.set_or_raise(key, value)
        except RepositoryError:
            pass

    async def set_or_raise(self, key: str, value: T) -> None:
        await self.store.set(key, value, self.ttl)

    def make_key(self, *parts: str) -> str:
        return ":".join(parts)
