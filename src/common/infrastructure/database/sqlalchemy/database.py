from typing import Self

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from common.infrastructure.config.database_config import DatabaseConfig
from common.infrastructure.database.sqlalchemy.session_factory import MAKER


class Database:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine
        self._create_session_maker()

    @classmethod
    def create(cls, config: DatabaseConfig) -> Self:
        return cls(engine=cls.create_engine(config))

    @staticmethod
    def create_engine(config: DatabaseConfig) -> AsyncEngine:
        return create_async_engine(
            config.database_url, echo=False
        )  # echo=True for detailed logs

    def _create_session_maker(self) -> None:
        self._session_maker = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    def get_engine(self) -> AsyncEngine:
        return self._engine

    def get_session_maker(self) -> MAKER:
        return self._session_maker

    async def shutdown(self) -> None:
        await self._engine.dispose()
