from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class IKeyValueStore(ABC, Generic[T]):
    @abstractmethod
    async def get(self, key: str) -> T: ...
    @abstractmethod
    async def set(
        self, key: str, value: T, expire: int | None = None
    ) -> None: ...
