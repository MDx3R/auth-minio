from abc import ABC, abstractmethod


class IExtensionPolicy(ABC):
    @abstractmethod
    def is_allowed(self, extension: str) -> bool: ...
