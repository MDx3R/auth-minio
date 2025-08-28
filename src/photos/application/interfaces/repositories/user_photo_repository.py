from abc import ABC, abstractmethod
from uuid import UUID

from photos.domain.entity.photo import Photo


class IUserPhotoRepository(ABC):
    @abstractmethod
    async def add(self, entity: Photo) -> None: ...
    @abstractmethod
    async def list_by_user_id(self, user_id: UUID) -> list[Photo]: ...
