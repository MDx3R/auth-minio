from common.infrastructure.storage.minio.storage import MinioStorage
from photos.application.interfaces.repositories.photo_repository import (
    IPhotoRepository,
)
from photos.infrastructure.storage.minio.repositories.photo_repository import (
    MinioPhotoRepository,
)


def provide_minio_photo_repository(storage: MinioStorage) -> IPhotoRepository:
    return MinioPhotoRepository(
        storage.get_client(), storage.get_bucket_name()
    )
