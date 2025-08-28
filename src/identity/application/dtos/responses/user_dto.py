from dataclasses import dataclass
from typing import Self
from uuid import UUID

from identity.domain.entity.user import User


@dataclass(frozen=True)
class UserDTO:
    user_id: UUID
    username: str

    @classmethod
    def from_user(cls, user: User) -> Self:
        return cls(user_id=user.user_id, username=user.username)
