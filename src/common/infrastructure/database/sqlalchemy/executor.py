from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy import Delete, Insert, Row, Select, Update
from sqlalchemy.sql.dml import (
    ReturningInsert,
    ReturningUpdate,
)

from common.infrastructure.database.sqlalchemy.models.base import Base
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork


RESULT = TypeVar("RESULT")


class QueryExecutor:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute_scalar(
        self,
        statement: (
            Select[tuple[RESULT]]
            | Insert[RESULT]
            | Update[RESULT]
            | Delete[RESULT]
            | ReturningInsert[tuple[RESULT]]
            | ReturningUpdate[tuple[RESULT]]
        ),
    ) -> RESULT:
        return (await self.execute(statement)).unique().scalar_one()

    async def execute_scalar_one(
        self,
        statement: (
            Select[tuple[RESULT]]
            | Insert[RESULT]
            | Update[RESULT]
            | Delete[RESULT]
            | ReturningInsert[tuple[RESULT]]
            | ReturningUpdate[tuple[RESULT]]
        ),
    ) -> RESULT | None:
        return (await self.execute(statement)).unique().scalar_one_or_none()

    async def execute_scalar_many(
        self,
        statement: (
            Select[tuple[RESULT]]
            | Insert[RESULT]
            | Update[RESULT]
            | Delete[RESULT]
            | ReturningInsert[tuple[RESULT]]
            | ReturningUpdate[tuple[RESULT]]
        ),
    ) -> Sequence[RESULT]:
        return (await self.execute(statement)).unique().scalars().all()

    async def execute_one(
        self,
        statement: Select[tuple[RESULT, ...]],
    ) -> Row[tuple[RESULT, ...]] | None:
        return (await self.execute(statement)).unique().one_or_none()

    async def execute_many(
        self,
        statement: Select[tuple[RESULT, ...]],
    ) -> Sequence[Row[tuple[RESULT, ...]]]:
        return (await self.execute(statement)).unique().all()

    async def execute(
        self,
        statement: (
            Select[tuple[RESULT, ...]]
            | Insert[RESULT]
            | Update[RESULT]
            | Delete[RESULT]
            | ReturningInsert[tuple[RESULT]]
            | ReturningUpdate[tuple[RESULT]]
        ),
    ):
        async with self.uow.get_session() as session:
            result = await session.execute(statement)
            return result

    async def add(
        self,
        model: Base,
    ) -> None:
        async with self.uow.get_session() as session:
            session.add(model)
            await session.flush()

    async def add_all(
        self,
        models: Sequence[Base],
    ) -> None:
        async with self.uow.get_session() as session:
            session.add_all(models)
            await session.flush()

    async def save(
        self,
        model: Base,
    ) -> None:
        async with self.uow.get_session() as session:
            model = await session.merge(model)
            await session.flush()
