from abc import ABC, abstractmethod
from uuid import UUID


class IUUIDGenerator(ABC):
    @abstractmethod
    def create(self) -> UUID: ...
