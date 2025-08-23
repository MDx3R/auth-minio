from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from identity.domain.value_objects.descriptor import UserDescriptor


@dataclass
class User:
    user_id: UUID
    username: str

    def descriptor(self) -> UserDescriptor:
        return UserDescriptor(self.user_id, self.username)

    def __post_init__(self):
        if not self.username.strip():
            raise InvariantViolationError("Username cannot be empty")

    @classmethod
    def create(cls, user_id: UUID, username: str) -> Self:
        return cls(user_id=user_id, username=username)
