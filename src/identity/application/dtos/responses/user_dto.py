from dataclasses import dataclass
from typing import Self
from uuid import UUID

from identity.application.read_models.user_read_model import UserReadModel


@dataclass(frozen=True)
class UserDTO:
    user_id: UUID
    username: str

    @classmethod
    def from_user(cls, user: UserReadModel) -> Self:
        return cls(user_id=user.user_id, username=user.username)
