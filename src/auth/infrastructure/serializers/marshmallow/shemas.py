from typing import Any

from marshmallow import Schema, fields, post_load

from identity.domain.value_objects.descriptor import UserDescriptor


class UserDescriptorSchema(Schema):
    user_id = fields.UUID(required=True)
    username = fields.Str(required=True)

    @post_load
    def make_obj(self, data: dict[str, Any], **kwargs: Any):
        return UserDescriptor(**data)
