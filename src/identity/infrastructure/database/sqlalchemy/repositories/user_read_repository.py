from uuid import UUID

from sqlalchemy import select

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from identity.application.exceptions import UserNotFoundError
from identity.application.interfaces.repositories.user_read_repository import (
    IUserReadRepository,
)
from identity.application.read_models.user_read_model import UserReadModel
from identity.infrastructure.database.sqlalchemy.mappers.user_mapper import (
    UserReadMapper,
)
from identity.infrastructure.database.sqlalchemy.models.user_base import (
    UserBase,
)


class UserReadRepository(IUserReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, user_id: UUID) -> UserReadModel:
        stmt = select(UserBase).where(UserBase.user_id == user_id)
        user = await self.executor.execute_scalar_one(stmt)
        if not user:
            raise UserNotFoundError(user_id)
        return UserReadMapper.to_read(user)
