from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import timedelta
from typing import BinaryIO


class IPhotoRepository(ABC):
    @abstractmethod
    async def upload_photo(
        self, name: str, mime: str, data: BinaryIO
    ) -> None: ...
    @abstractmethod
    async def get_presigned_get_url(
        self, name: str, expires_in: timedelta
    ) -> str: ...
    @abstractmethod
    async def get_presigned_get_urls(
        self, names: Sequence[str], expires_in: timedelta
    ) -> list[str]: ...
