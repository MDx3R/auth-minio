from abc import ABC, abstractmethod
from datetime import timedelta
from typing import BinaryIO


class IPhotoRepository(ABC):
    @abstractmethod
    async def upload_photo(
        self, name: str, mime: str, data: BinaryIO
    ) -> None: ...
    @abstractmethod
    async def get_presigned_url(
        self, name: str, expires_in: timedelta
    ) -> str: ...
