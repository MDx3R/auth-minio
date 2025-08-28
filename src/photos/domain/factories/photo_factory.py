from uuid import UUID

from common.domain.uuid_generator import IUUIDGenerator
from photos.domain.entity.photo import Photo
from photos.domain.exceptions import InvalidExtensionTypeError
from photos.domain.interfaces.extenstion_policy import IExtensionPolicy
from photos.domain.interfaces.photo_factory import IPhotoFactory


class PhotoFactory(IPhotoFactory):
    def __init__(
        self, uuid_generator: IUUIDGenerator, ext_policy: IExtensionPolicy
    ) -> None:
        self.uuid_generator = uuid_generator
        self.ext_policy = ext_policy

    def create(self, user_id: UUID, extension: str, mime: str) -> Photo:
        if not self.ext_policy.is_allowed(extension):
            raise InvalidExtensionTypeError(extension)

        return Photo.create(
            self.uuid_generator.create(), user_id, extension, mime
        )
