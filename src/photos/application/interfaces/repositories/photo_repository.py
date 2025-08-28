from abc import ABC, abstractmethod
from typing import BinaryIO


class IPhotoRepository(ABC):
    @abstractmethod
    async def upload_photo(self, name: str, data: BinaryIO) -> None: ...
    @abstractmethod
    async def download_photo(self, name: str) -> BinaryIO: ...
