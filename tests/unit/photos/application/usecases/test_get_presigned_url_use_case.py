from datetime import timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from photos.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from photos.application.interfaces.repositories.photo_repository import (
    IPhotoRepository,
)
from photos.application.usecases.query.get_presigned_url_use_case import (
    GetPresignedUrlUseCase,
)


@pytest.mark.asyncio
class TestGetPresignedUrlUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.photo_name = f"{uuid4()}.jpg"
        self.url = f"my-cloud/photos/{self.photo_name}"

        self.photo_repository = AsyncMock(spec=IPhotoRepository)

        self.photo_repository.get_presigned_get_url.return_value = self.url

        self.use_case = GetPresignedUrlUseCase(
            self.photo_repository, timedelta(minutes=15)
        )

        self.query = GetPresignedUrlQuery(self.photo_name)

    async def test_execute_success(self):
        # Act
        result = await self.use_case.execute(self.query)

        # Assert
        assert result == self.url
