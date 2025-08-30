from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class IKeyValueCache(ABC, Generic[T]):
    @abstractmethod
    async def get(self, key: str) -> T | None: ...
    @abstractmethod
    async def get_or_raise(self, key: str) -> T: ...
    @abstractmethod
    async def set(self, key: str, value: T) -> None: ...
    @abstractmethod
    async def set_or_raise(self, key: str, value: T) -> None: ...

    def make_key(self, *parts: str) -> str:
        return ":".join(parts)
