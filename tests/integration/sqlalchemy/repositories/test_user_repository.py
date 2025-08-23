from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from identity.application.exceptions import UserNotFoundError
from identity.domain.entity.user import User
from identity.infrastructure.database.sqlalchemy.mappers.user_mapper import (
    UserMapper,
)
from identity.infrastructure.database.sqlalchemy.models.user_base import (
    UserBase,
)
from identity.infrastructure.database.sqlalchemy.repositories.user_repository import (
    UserRepository,
)


@pytest.mark.asyncio
class TestUserRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.user_repository = UserRepository(query_executor)

    async def _exists(self, user: User) -> bool:
        return await self._get(user) is not None

    async def _get(self, user: User) -> User | None:
        async with self.maker() as session:
            result = await session.get(UserBase, user.user_id)
            if not result:
                return None
            return UserMapper.to_domain(result)

    async def _add_user(self) -> User:
        user = self._get_user()
        async with self.maker() as session:
            session.add(UserMapper.to_persistence(user))
            await session.commit()
        return user

    def _get_user(self) -> User:
        return User(uuid4(), "test user")

    async def test_get_by_id_success(self):
        user = await self._add_user()

        result = await self.user_repository.get_by_id(user.user_id)
        assert result == user

    async def test_get_by_id_not_found(self):
        with pytest.raises(UserNotFoundError):
            await self.user_repository.get_by_id(uuid4())
