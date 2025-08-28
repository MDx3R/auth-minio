from abc import ABC, abstractmethod
from uuid import UUID

from photos.domain.entity.photo import Photo


class IPhotoFactory(ABC):
    @abstractmethod
    def create(self, user_id: UUID, extension: str, mime: str) -> Photo: ...
