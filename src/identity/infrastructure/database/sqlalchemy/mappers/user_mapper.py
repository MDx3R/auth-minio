from identity.domain.entity.user import User
from identity.infrastructure.database.sqlalchemy.models.user_base import (
    UserBase,
)


class UserMapper:
    @classmethod
    def to_domain(cls, base: UserBase) -> User:
        return User(user_id=base.user_id, username=base.username)

    @classmethod
    def to_persistence(cls, user: User) -> UserBase:
        return UserBase(user_id=user.user_id, username=user.username)
