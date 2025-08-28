from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from identity.domain.entity.user import User
from identity.infrastructure.database.sqlalchemy.mappers.user_mapper import (
    UserMapper,
)
from photos.domain.entity.photo import Photo
from photos.infrastructure.database.sqlalchemy.mappers.photo_mapper import (
    PhotoMapper,
)
from photos.infrastructure.database.sqlalchemy.models.photo_base import (
    PhotoBase,
)
from photos.infrastructure.database.sqlalchemy.repositories.user_photo_repository import (
    UserPhotoRepository,
)


@pytest.mark.asyncio
class TestUserPhotoRepository:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.repository = UserPhotoRepository(query_executor)

        self.user = await self._add_user()

    def _get_user(self) -> User:
        return User(uuid4(), "test user", "hash")

    async def _add_user(self) -> User:
        user = self._get_user()
        async with self.maker() as session:
            session.add(UserMapper.to_persistence(user))
            await session.commit()
        return user

    async def _add_photo(self) -> Photo:
        photo = self._get_photo()
        async with self.maker() as session:
            session.add(PhotoMapper.to_persistence(photo))
            await session.commit()
        return photo

    def _get_photo(self) -> Photo:
        return Photo(
            photo_id=uuid4(),
            user_id=self.user.user_id,
            name=f"{uuid4()}.jpg",
            mime="image/jpeg",
        )

    async def _get(self, photo_id: UUID) -> Photo | None:
        async with self.maker() as session:
            stmt = select(PhotoBase).where(PhotoBase.photo_id == photo_id)
            base = await session.execute(stmt)
            base = base.scalar_one_or_none()
            return PhotoMapper.to_domain(base) if base else None

    async def test_add_success(self):
        # Arrange
        photo = self._get_photo()

        # Act
        await self.repository.add(photo)

        # Assert
        result = await self._get(photo.photo_id)
        assert result
        assert result == photo

    async def test_list_by_user_id_success(self):
        # Arrange
        photo1 = await self._add_photo()
        photo2 = self._get_photo()
        photo2.user_id = photo1.user_id  # Same user for both photos
        await self.repository.add(photo2)

        # Act
        result = await self.repository.list_by_user_id(photo1.user_id)

        # Assert
        assert len(result) == 2
        assert photo1 in result
        assert photo2 in result

    async def test_list_by_user_id_no_photos(self):
        # Arrange
        user_id = uuid4()  # New user with no photos

        # Act
        result = await self.repository.list_by_user_id(user_id)

        # Assert
        assert len(result) == 0
        assert result == []
