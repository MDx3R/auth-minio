from marshmallow import Schema

from common.infrastructure.exceptions import SerializationError
from common.infrastructure.serializers.serializer import ISerializer, T


class MarshmallowSerializer(ISerializer[T]):
    def __init__(self, schema: Schema):
        self._schema = schema

    def serialize(self, obj: T) -> str:
        try:
            return self._schema.dumps(obj)  # type: ignore
        except Exception as e:
            raise SerializationError from e

    def deserialize(self, data: str) -> T:
        try:
            return self._schema.loads(data)  # type: ignore
        except Exception as e:
            raise SerializationError from e
