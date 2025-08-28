from io import BytesIO
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

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
from photos.application.usecases.command.upload_photo_use_case import (
    UploadPhotoUseCase,
)
from photos.domain.entity.photo import Photo
from photos.domain.interfaces.photo_factory import IPhotoFactory


@pytest.mark.asyncio
class TestUploadPhotoUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.photo_id = uuid4()
        self.user_id = uuid4()
        self.descriptor = UserDescriptor(
            user_id=self.user_id, username="testuser"
        )
        self.extension = "jpg"
        self.mime = "image/jpeg"
        self.content = BytesIO(b"fake_image_data")
        self.photo_name = f"{self.photo_id}.{self.extension}"
        self.photo = Photo(
            photo_id=self.photo_id,
            user_id=self.user_id,
            name=self.photo_name,
            mime=self.mime,
        )

        self.photo_factory = Mock(spec=IPhotoFactory)
        self.photo_factory.create.return_value = self.photo

        self.photo_repository = AsyncMock(spec=IPhotoRepository)
        self.user_photo_repository = AsyncMock(spec=IUserPhotoRepository)
        self.file_type_introspector = Mock(spec=IFileTypeIntrospector)
        self.file_type_introspector.extract.return_value = Mock(
            extension=self.extension, mime=self.mime
        )

        self.use_case = UploadPhotoUseCase(
            photo_factory=self.photo_factory,
            photo_repository=self.photo_repository,
            user_photo_repository=self.user_photo_repository,
            file_type_introspector=self.file_type_introspector,
        )

        self.command = UploadPhotoCommand(content=self.content)

    async def test_execute_success(self):
        # Act
        result = await self.use_case.execute(self.command, self.descriptor)

        # Assert
        self.file_type_introspector.extract.assert_called_once_with(
            self.content
        )
        self.photo_factory.create.assert_called_once_with(
            self.descriptor.user_id, extension=self.extension, mime=self.mime
        )
        self.user_photo_repository.add.assert_awaited_once_with(self.photo)
        self.photo_repository.upload_photo.assert_awaited_once_with(
            name=self.photo_name, mime=self.mime, data=self.content
        )
        assert result == self.photo_name
