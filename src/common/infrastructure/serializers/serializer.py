from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class ISerializer(ABC, Generic[T]):
    @abstractmethod
    def serialize(self, obj: T) -> str: ...
    @abstractmethod
    def deserialize(self, data: str) -> T: ...
