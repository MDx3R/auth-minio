from typing import Any

from marshmallow import Schema, fields, post_load

from identity.application.read_models.user_read_model import UserReadModel


class UserReadModelSchema(Schema):
    user_id = fields.UUID(required=True)
    username = fields.Str(required=True)

    @post_load
    def make_obj(self, data: dict[str, Any], **kwargs: Any):
        return UserReadModel(**data)
