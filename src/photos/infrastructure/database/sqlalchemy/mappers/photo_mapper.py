from photos.domain.entity.photo import Photo
from photos.infrastructure.database.sqlalchemy.models.photo_base import (
    PhotoBase,
)


class PhotoMapper:
    @classmethod
    def to_domain(cls, base: PhotoBase) -> Photo:
        return Photo(
            photo_id=base.photo_id,
            user_id=base.user_id,
            name=base.name,
            mime=base.mime,
        )

    @classmethod
    def to_persistence(cls, photo: Photo) -> PhotoBase:
        return PhotoBase(
            photo_id=photo.photo_id,
            user_id=photo.user_id,
            name=photo.name,
            mime=photo.mime,
        )
