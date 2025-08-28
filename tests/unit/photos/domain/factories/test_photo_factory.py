from unittest.mock import Mock
from uuid import uuid4

import pytest

from common.domain.uuid_generator import IUUIDGenerator
from photos.domain.entity.photo import Photo
from photos.domain.exceptions import InvalidExtensionTypeError
from photos.domain.factories.photo_factory import PhotoFactory
from photos.domain.interfaces.extenstion_policy import IExtensionPolicy


class TestPhotoFactory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.photo_id = uuid4()
        self.user_id = uuid4()
        self.extension = "jpg"
        self.mime = "image/jpeg"

        self.uuid_generator = Mock(spec=IUUIDGenerator)
        self.uuid_generator.create.return_value = self.photo_id

        self.ext_policy = Mock(spec=IExtensionPolicy)
        self.ext_policy.is_allowed.return_value = True

        self.factory = PhotoFactory(self.uuid_generator, self.ext_policy)

    def test_photo_factory_create_success(self):
        # Arrange
        expected_name = f"{self.photo_id}.{self.extension}"

        # Act
        result = self.factory.create(self.user_id, self.extension, self.mime)

        # Assert
        assert result == Photo(
            photo_id=self.photo_id,
            user_id=self.user_id,
            name=expected_name,
            mime=self.mime,
        )
        self.uuid_generator.create.assert_called_once()
        self.ext_policy.is_allowed.assert_called_once_with(self.extension)

    def test_photo_factory_create_invalid_extension_fails(self):
        # Arrange
        self.ext_policy.is_allowed.return_value = False

        # Act
        with pytest.raises(InvalidExtensionTypeError):
            self.factory.create(self.user_id, self.extension, self.mime)

        # Assert
        self.ext_policy.is_allowed.assert_called_once_with(self.extension)
