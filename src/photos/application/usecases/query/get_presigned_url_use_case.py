from datetime import timedelta

from photos.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from photos.application.interfaces.repositories.photo_repository import (
    IPhotoRepository,
)
from photos.application.interfaces.usecases.query.get_presigned_url_use_case import (
    IGetPresignedUrlUseCase,
)


class GetPresignedUrlUseCase(IGetPresignedUrlUseCase):
    def __init__(
        self, photo_repository: IPhotoRepository, expiration_delta: timedelta
    ) -> None:
        self.photo_repository = photo_repository
        self.expiration_delta = expiration_delta

    async def execute(self, command: GetPresignedUrlQuery) -> str:
        return await self.photo_repository.get_presigned_get_url(
            command.name, self.expiration_delta
        )
