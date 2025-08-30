from uuid import uuid4

import pytest

from auth.infrastructure.serializers.marshmallow.shemas import (
    UserDescriptorSchema,
)
from common.infrastructure.exceptions import SerializationError
from common.infrastructure.serializers.marshmallow.serializer import (
    MarshmallowSerializer,
)
from identity.domain.value_objects.descriptor import UserDescriptor


class TestMarshmallowSerializerUserDescriptor:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.schema = UserDescriptorSchema()
        self.serializer = MarshmallowSerializer[UserDescriptor](self.schema)
        self.user_id = uuid4()
        self.username = "testuser"
        self.descriptor = UserDescriptor(
            user_id=self.user_id, username=self.username
        )
        self.serialized_data = (
            f'{{"user_id": "{self.user_id}", "username": "{self.username}"}}'
        )

    def test_serialize_success(self):
        # Act
        result = self.serializer.serialize(self.descriptor)

        # Assert
        assert result == self.serialized_data
        assert isinstance(result, str)

    def test_deserialize_success(self):
        # Act
        result = self.serializer.deserialize(self.serialized_data)

        # Assert
        assert isinstance(result, UserDescriptor)
        assert result.user_id == self.user_id
        assert result.username == self.username

    def test_deserialize_missing_user_id(self):
        # Arrange
        invalid_data = f'{{"username": "{self.username}"}}'

        # Act & Assert
        with pytest.raises(SerializationError, match="user_id.*required"):
            self.serializer.deserialize(invalid_data)

    def test_deserialize_missing_username(self):
        # Arrange
        invalid_data = f'{{"user_id": "{self.user_id}"}}'

        # Act & Assert
        with pytest.raises(SerializationError, match="username.*required"):
            self.serializer.deserialize(invalid_data)

    def test_deserialize_invalid_uuid(self):
        # Arrange
        invalid_data = (
            f'{{"user_id": "not-a-uuid", "username": "{self.username}"}}'
        )

        # Act & Assert
        with pytest.raises(
            SerializationError, match="user_id.*Not a valid UUID"
        ):
            self.serializer.deserialize(invalid_data)

    def test_deserialize_invalid_username_type(self):
        # Arrange
        invalid_data = f'{{"user_id": "{self.user_id}", "username": 123}}'

        # Act & Assert
        with pytest.raises(
            SerializationError, match="username.*Not a valid string"
        ):
            self.serializer.deserialize(invalid_data)
