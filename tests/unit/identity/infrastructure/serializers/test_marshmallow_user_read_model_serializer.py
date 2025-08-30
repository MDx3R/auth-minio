from uuid import uuid4

import pytest

from common.infrastructure.exceptions import SerializationError
from common.infrastructure.serializers.marshmallow.serializer import (
    MarshmallowSerializer,
)
from identity.application.read_models.user_read_model import UserReadModel
from identity.infrastructure.serializers.marshmallow.shemas import (
    UserReadModelSchema,
)


class TestMarshmallowSerializerUserReadModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.schema = UserReadModelSchema()
        self.serializer = MarshmallowSerializer[UserReadModel](self.schema)
        self.user_id = uuid4()
        self.username = "testuser"
        self.descriptor = UserReadModel(
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
        assert isinstance(result, UserReadModel)
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
