from datetime import datetime
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy.pool import StaticPool


class MockBase(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MockModel(MockBase):
    __tablename__ = "model"

    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)


@pytest_asyncio.fixture(scope="session")
async def async_engine(request: pytest.FixtureRequest):
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(MockBase.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
def async_session_maker(async_engine: AsyncEngine):
    return async_sessionmaker(async_engine, expire_on_commit=False)
