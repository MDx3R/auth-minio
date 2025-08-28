from uuid import UUID

from sqlalchemy import select

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from photos.application.interfaces.repositories.user_photo_repository import (
    IUserPhotoRepository,
)
from photos.domain.entity.photo import Photo
from photos.infrastructure.database.sqlalchemy.mappers.photo_mapper import (
    PhotoMapper,
)
from photos.infrastructure.database.sqlalchemy.models.photo_base import (
    PhotoBase,
)


class UserPhotoRepository(IUserPhotoRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def add(self, entity: Photo) -> None:
        model = PhotoMapper.to_persistence(entity)
        await self.executor.add(model)

    async def list_by_user_id(self, user_id: UUID) -> list[Photo]:
        stmt = select(PhotoBase).where(PhotoBase.user_id == user_id)
        result = await self.executor.execute_scalar_many(stmt)
        return [PhotoMapper.to_domain(model) for model in result]
