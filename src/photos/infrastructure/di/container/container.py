from dependency_injector import containers, providers

from photos.application.usecases.command.upload_photo_use_case import (
    UploadPhotoUseCase,
)
from photos.application.usecases.query.get_presigned_url_use_case import (
    GetPresignedUrlUseCase,
)
from photos.domain.factories.photo_factory import PhotoFactory
from photos.domain.policies.extenstion_policy import ExtensionWhitelistPolicy
from photos.infrastructure.database.sqlalchemy.repositories.user_photo_repository import (
    UserPhotoRepository,
)
from photos.infrastructure.di.container.providers import (
    provide_minio_photo_repository,
)
from photos.infrastructure.services.file_type_introspector import (
    FileTypeIntrospector,
)


class PhotoContainer(containers.DeclarativeContainer):
    presigned_url_expiration_delta = providers.Dependency()
    allowed_extensions = providers.Dependency()

    uuid_generator = providers.Dependency()
    query_executor = providers.Dependency()
    minio_storage = providers.Dependency()

    file_type_introspector = providers.Singleton(FileTypeIntrospector)

    photo_repository = providers.Singleton(
        provide_minio_photo_repository, minio_storage
    )
    user_photo_repository = providers.Singleton(
        UserPhotoRepository, query_executor
    )

    extension_policy = providers.Singleton(
        ExtensionWhitelistPolicy, allowed_extensions
    )
    photo_factory = providers.Singleton(
        PhotoFactory,
        uuid_generator=uuid_generator,
        ext_policy=extension_policy,
    )

    upload_photo_use_case = providers.Singleton(
        UploadPhotoUseCase,
        photo_factory=photo_factory,
        photo_repository=photo_repository,
        user_photo_repository=user_photo_repository,
        file_type_introspector=file_type_introspector,
    )

    get_presigned_url_use_case = providers.Singleton(
        GetPresignedUrlUseCase,
        photo_repository=photo_repository,
        expiration_delta=presigned_url_expiration_delta,
    )
