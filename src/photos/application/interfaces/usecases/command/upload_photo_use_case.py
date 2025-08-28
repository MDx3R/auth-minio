from abc import ABC, abstractmethod

from identity.domain.value_objects.descriptor import UserDescriptor
from photos.application.dtos.command.upload_photo_command import (
    UploadPhotoCommand,
)


class IUploadPhotoUseCase(ABC):
    @abstractmethod
    async def execute(
        self, command: UploadPhotoCommand, descriptor: UserDescriptor
    ) -> str: ...
