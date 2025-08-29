from typing import Any

import httpx
import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPhoto:
    @pytest.fixture(autouse=True)
    def setup(self, client: AsyncClient):
        self.test_user = {"username": "testuser", "password": "password123"}
        self.client = client
        # JPEG magic number (FFD8FFE0 is a valid JPEG start)
        self.test_file = {
            "file": (
                "test.jpg",
                b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00",
                "image/jpeg",
            )
        }
        # Invalid file (text file for testing InvalidFileTypeError)
        self.invalid_file = {
            "file": (
                "test.txt",
                b"Plain text content",
                "text/plain",
            )
        }

    async def register_user(
        self, user_data: dict[str, str] | None = None
    ) -> Any:
        user_data = user_data or self.test_user

        response = await self.client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_200_OK, response.json()
        response = await self.client.post(
            "/auth/login",
            data={
                "username": user_data["username"],
                "password": user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        return response.json()

    def make_auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    async def test_upload_photo_success(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["access_token"])

        # Act
        response = await self.client.post(
            "photos/upload",
            files=self.test_file,
            headers=headers,
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        assert "value" in data

    async def test_upload_photo_unauthenticated(self):
        # Act
        response = await self.client.post(
            "photos/upload",
            files=self.test_file,
        )

        # Assert
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_upload_photo_invalid_file_type(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["access_token"])

        # Act
        response = await self.client.post(
            "photos/upload",
            files=self.invalid_file,
            headers=headers,
        )

        # Assert
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), response.json()
        assert "error" in response.json()["detail"], response.json()

    async def test_get_presigned_url_success(self):
        # Arrange
        test_photo_name = "test-photo.jpg"

        # Act
        response = await self.client.get(
            "photos/presigned-url",
            params={"name": test_photo_name},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        assert "value" in data
        assert test_photo_name in data["value"]

    async def test_get_presigned_url_missing_name(self):
        # Act
        response = await self.client.get("photos/presigned-url")

        # Assert
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        ), response.json()
        assert "name" in response.json()["detail"][0]["loc"]

    async def test_retrieve_photo_with_presigned_url_success(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["access_token"])

        response = await self.client.post(
            "photos/upload", files=self.test_file, headers=headers
        )
        photo_name = response.json()["value"]

        # Get presigned URL
        response = await self.client.get(
            "photos/presigned-url",
            params={"name": photo_name},
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        presigned_url = response.json()["value"]

        # Act
        async with httpx.AsyncClient() as client:
            response = await client.get(presigned_url)

        # Assert
        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.headers["content-type"] == "image/jpeg"
        assert response.content.startswith(
            b"\xff\xd8\xff\xe0"
        )  # JPEG magic number

    async def test_retrieve_photo_with_invalid_presigned_url(self):
        # Arrange
        test_photo_name = "test-photo.jpg"
        response = await self.client.get(
            "photos/presigned-url",
            params={"name": test_photo_name},
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        presigned_url = response.json()["value"]

        # Act
        async with httpx.AsyncClient() as client:
            response = await client.get(presigned_url)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
