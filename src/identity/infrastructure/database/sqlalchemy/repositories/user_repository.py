from uuid import UUID

from sqlalchemy import exists, select

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from identity.application.exceptions import UserNotFoundError
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.domain.entity.user import User
from identity.infrastructure.database.sqlalchemy.mappers.user_mapper import (
    UserMapper,
)
from identity.infrastructure.database.sqlalchemy.models.user_base import (
    UserBase,
)


class UserRepository(IUserRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, user_id: UUID) -> User:
        stmt = select(UserBase).where(UserBase.user_id == user_id)
        user = await self.executor.execute_scalar_one(stmt)
        if not user:
            raise UserNotFoundError(user_id)
        return UserMapper.to_domain(user)

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(exists().where(UserBase.username == username))
        return await self.executor.execute_scalar(stmt)

    async def get_by_username(self, username: str) -> User:
        stmt = select(UserBase).where(UserBase.username == username)
        user = await self.executor.execute_scalar_one(stmt)
        if not user:
            raise UserNotFoundError(username)
        return UserMapper.to_domain(user)

    async def add(self, entity: User) -> None:
        model = UserMapper.to_persistence(entity)
        await self.executor.add(model)
