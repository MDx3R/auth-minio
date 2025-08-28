import asyncio
from collections.abc import Sequence
from datetime import timedelta
from typing import BinaryIO

from minio import Minio, S3Error  # type: ignore

from common.application.exceptions import RepositoryError
from photos.application.interfaces.repositories.photo_repository import (
    IPhotoRepository,
)


class MinioPhotoRepository(IPhotoRepository):
    def __init__(self, client: Minio, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    async def upload_photo(self, name: str, mime: str, data: BinaryIO) -> None:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=name,
                    data=data,
                    length=-1,
                    content_type=mime,
                    part_size=8 * 1024 * 1024,
                ),
            )
        except S3Error as e:
            raise RepositoryError(f"Failed to upload photo '{name}'") from e

    async def get_presigned_get_url(
        self, name: str, expires_in: timedelta
    ) -> str:
        loop = asyncio.get_running_loop()
        try:
            url = await loop.run_in_executor(
                None,
                lambda: self.client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=name,
                    expires=expires_in,
                ),
            )
            return url
        except S3Error as e:
            # NOTE: Sice there is no exception for not found we can rely on S3 API to return 404 later on url use
            raise RepositoryError(
                f"Failed to generate presigned URL for '{name}'"
            ) from e

    async def get_presigned_get_urls(
        self, names: Sequence[str], expires_in: timedelta
    ) -> list[str]:
        tasks = [
            self.get_presigned_get_url(name, expires_in) for name in names
        ]
        urls = await asyncio.gather(*tasks)
        return urls
