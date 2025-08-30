from identity.application.read_models.user_read_model import UserReadModel
from identity.domain.entity.user import User
from identity.infrastructure.database.sqlalchemy.models.user_base import (
    UserBase,
)


class UserMapper:
    @classmethod
    def to_domain(cls, base: UserBase) -> User:
        return User(
            user_id=base.user_id,
            username=base.username,
            password=base.password,
        )

    @classmethod
    def to_persistence(cls, user: User) -> UserBase:
        return UserBase(
            user_id=user.user_id,
            username=user.username,
            password=user.password,
        )


class UserReadMapper:
    @classmethod
    def to_read(cls, base: UserBase) -> UserReadModel:
        return UserReadModel(user_id=base.user_id, username=base.username)
