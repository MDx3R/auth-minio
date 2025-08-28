from abc import ABC, abstractmethod
from typing import BinaryIO

from photos.application.dtos.dtos import FileType


class IFileTypeIntrospector(ABC):
    @abstractmethod
    def extract(self, data: BinaryIO) -> FileType: ...
