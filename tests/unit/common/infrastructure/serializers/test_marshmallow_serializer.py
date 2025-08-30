from unittest.mock import Mock

import pytest
from marshmallow import Schema

from common.infrastructure.exceptions import SerializationError
from common.infrastructure.serializers.marshmallow.serializer import (
    MarshmallowSerializer,
)


class TestMarshmallowSerializer:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Mock the Marshmallow schema
        self.schema = Mock(spec=Schema)
        self.serializer = MarshmallowSerializer[dict[str, str]](self.schema)
        self.test_obj = {"key": "value"}
        self.serialized_data = '{"key": "value"}'

    def test_serialize_success(self):
        # Arrange
        self.schema.dumps.return_value = self.serialized_data

        # Act
        result = self.serializer.serialize(self.test_obj)

        # Assert
        assert result == self.serialized_data
        self.schema.dumps.assert_called_once_with(self.test_obj)

    def test_serialize_raises_serialization_error(self):
        # Arrange
        self.schema.dumps.side_effect = Exception("Serialization failed")

        # Act & Assert
        with pytest.raises(SerializationError):
            self.serializer.serialize(self.test_obj)
        self.schema.dumps.assert_called_once_with(self.test_obj)

    def test_deserialize_success(self):
        # Arrange
        self.schema.loads.return_value = self.test_obj

        # Act
        result = self.serializer.deserialize(self.serialized_data)

        # Assert
        assert result == self.test_obj
        self.schema.loads.assert_called_once_with(self.serialized_data)

    def test_deserialize_raises_serialization_error(self):
        # Arrange
        self.schema.loads.side_effect = Exception("Deserialization failed")

        # Act & Assert
        with pytest.raises(SerializationError):
            self.serializer.deserialize(self.serialized_data)
        self.schema.loads.assert_called_once_with(self.serialized_data)
