from datetime import timedelta
from io import BytesIO
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from minio import Minio  # type: ignore

from photos.infrastructure.storage.minio.repositories.photo_repository import (
    MinioPhotoRepository,
)


@pytest.mark.asyncio
class TestMinioPhotoRepository:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, minio: Minio):
        self.bucket_name = "test-bucket"
        self.client = minio
        self.repository = MinioPhotoRepository(self.client, self.bucket_name)

        if not minio.bucket_exists(self.bucket_name):
            minio.make_bucket(self.bucket_name)
        async with httpx.AsyncClient() as http_client:
            self.http_client = http_client
            yield
        # Clean up
        objects = self.client.list_objects(self.bucket_name, recursive=True)
        for obj in objects:
            if not obj.object_name:
                continue
            self.client.remove_object(self.bucket_name, obj.object_name)

    def _get_photo_name(self) -> str:
        return f"{uuid4()}.jpg"

    def _get_image_data(self) -> BytesIO:
        return BytesIO(b"fake_image_data")

    async def _add_photo(self, photo_name: str, mime: str) -> None:
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=photo_name,
            data=self._get_image_data(),
            length=len(b"fake_image_data"),
            content_type=mime,
        )

    async def test_upload_photo_success(self):
        # Arrange
        photo_name = self._get_photo_name()
        mime = "image/jpeg"
        data = self._get_image_data()

        # Act
        await self.repository.upload_photo(photo_name, mime, data)

        # Assert
        objects = list(self.client.list_objects(self.bucket_name))
        assert len(objects) == 1
        assert objects[0].object_name == photo_name
        stat = self.client.stat_object(self.bucket_name, photo_name)
        assert stat.content_type == mime

    async def test_get_presigned_get_url_success(self):
        # Arrange
        photo_name = self._get_photo_name()
        mime = "image/jpeg"
        expires_in = timedelta(minutes=5)
        await self._add_photo(photo_name, mime)

        # Act
        url = await self.repository.get_presigned_get_url(
            photo_name, expires_in
        )

        # Assert
        assert isinstance(url, str)
        assert f"{self.bucket_name}/{photo_name}" in url

        response = await self.http_client.get(url)

        # Assert response
        assert response.status_code == 200
        assert response.headers["Content-Type"] == mime
        assert response.content == b"fake_image_data"

    async def test_get_presigned_get_urls_success(self):
        # Arrange
        photo_names = [self._get_photo_name() for _ in range(2)]
        mime = "image/jpeg"
        expires_in = timedelta(minutes=5)
        for name in photo_names:
            await self._add_photo(name, mime)

        # Act
        urls = await self.repository.get_presigned_get_urls(
            photo_names, expires_in
        )

        # Assert
        assert len(urls) == 2
        for url, name in zip(urls, photo_names, strict=True):
            assert isinstance(url, str)
            assert f"{self.bucket_name}/{name}" in url

            response = await self.http_client.get(url)

            # Assert response
            assert response.status_code == 200
            assert response.headers["Content-Type"] == mime
            assert response.content == b"fake_image_data"
