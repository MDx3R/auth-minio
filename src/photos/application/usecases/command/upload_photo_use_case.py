from identity.domain.value_objects.descriptor import UserDescriptor
from photos.application.dtos.command.upload_photo_command import (
    UploadPhotoCommand,
)
from photos.application.interfaces.repositories.photo_repository import (
    IPhotoRepository,
)
from photos.application.interfaces.repositories.user_photo_repository import (
    IUserPhotoRepository,
)
from photos.application.interfaces.services.file_type_introspector import (
    IFileTypeIntrospector,
)
from photos.application.interfaces.usecases.command.upload_photo_use_case import (
    IUploadPhotoUseCase,
)
from photos.domain.interfaces.photo_factory import IPhotoFactory


class UploadPhotoUseCase(IUploadPhotoUseCase):
    def __init__(
        self,
        photo_factory: IPhotoFactory,
        photo_repository: IPhotoRepository,
        user_photo_repository: IUserPhotoRepository,
        file_type_introspector: IFileTypeIntrospector,
    ) -> None:
        self.photo_factory = photo_factory
        self.photo_repository = photo_repository
        self.user_photo_repository = user_photo_repository
        self.file_type_introspector = file_type_introspector

    async def execute(
        self, command: UploadPhotoCommand, descriptor: UserDescriptor
    ) -> str:
        file_type = self.file_type_introspector.extract(command.content)

        photo = self.photo_factory.create(
            descriptor.user_id,
            extension=file_type.extension,
            mime=file_type.mime,
        )

        await self.user_photo_repository.add(photo)
        await self.photo_repository.upload_photo(
            name=photo.name, mime=photo.mime, data=command.content
        )

        return photo.name
