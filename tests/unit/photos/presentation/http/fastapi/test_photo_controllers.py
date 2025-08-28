import unittest
import unittest.mock
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from auth.application.interfaces.services.token_service import (
    ITokenIntrospector,
)
from identity.domain.value_objects.descriptor import UserDescriptor
from photos.application.dtos.command.upload_photo_command import (
    UploadPhotoCommand,
)
from photos.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from photos.application.interfaces.usecases.command.upload_photo_use_case import (
    IUploadPhotoUseCase,
)
from photos.application.interfaces.usecases.query.get_presigned_url_use_case import (
    IGetPresignedUrlUseCase,
)
from photos.presentation.http.fastapi.controllers import (
    command_router,
    query_router,
)


@pytest.mark.asyncio
class TestPhotoControllers:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = FastAPI()
        self.app.include_router(command_router)
        self.app.include_router(query_router)
        self.client: TestClient = TestClient(self.app)

        self.upload_photo_use_case = AsyncMock(spec=IUploadPhotoUseCase)
        self.get_presigned_url_use_case = AsyncMock(
            spec=IGetPresignedUrlUseCase
        )
        self.token_introspector = AsyncMock(spec=ITokenIntrospector)
        self.user_descriptor = self._get_user_descriptor()
        self.token_introspector.extract_user.return_value = (
            self.user_descriptor
        )

        self.app.dependency_overrides[IUploadPhotoUseCase] = (
            lambda: self.upload_photo_use_case
        )
        self.app.dependency_overrides[IGetPresignedUrlUseCase] = (
            lambda: self.get_presigned_url_use_case
        )
        self.app.dependency_overrides[ITokenIntrospector] = (
            lambda: self.token_introspector
        )

    def _get_user_descriptor(self) -> UserDescriptor:
        user_id = uuid4()
        return UserDescriptor(user_id=user_id, username="testuser")

    async def test_upload_photo_success(self):
        # Arrange
        photo_name = "test-photo.jpg"
        file_content = b"fake_image_data"
        mock_response = photo_name
        self.upload_photo_use_case.execute.return_value = mock_response

        # Act
        response = self.client.post(
            "/upload",
            files={"file": (photo_name, file_content, "image/jpeg")},
            headers={"Authorization": "Bearer valid_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"value": mock_response}
        self.upload_photo_use_case.execute.assert_awaited_once_with(
            UploadPhotoCommand(content=unittest.mock.ANY),
            self.user_descriptor,
        )

    async def test_upload_photo_unauthenticated_fails(self):
        # Arrange
        photo_name = "test-photo.jpg"
        file_content = b"fake_image_data"

        # Act
        response = self.client.post(
            "/upload", files={"file": (photo_name, file_content, "image/jpeg")}
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Authentication required"}
        self.upload_photo_use_case.execute.assert_not_awaited()

    async def test_get_presigned_url_success(self):
        # Arrange
        photo_name = "test-photo.jpg"
        mock_url = f"https://example.com/presigned/{photo_name}"
        self.get_presigned_url_use_case.execute.return_value = mock_url

        # Act
        response = self.client.get(f"/presigned-url?name={photo_name}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"value": mock_url}
        self.get_presigned_url_use_case.execute.assert_awaited_once_with(
            GetPresignedUrlQuery(name=photo_name)
        )

    async def test_get_presigned_url_missing_name_fails(self):
        # Act
        response = self.client.get(
            "/presigned-url"
        )  # Missing 'name' query parameter

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
        self.get_presigned_url_use_case.execute.assert_not_awaited()
