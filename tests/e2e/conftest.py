import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from cli.services.api import main
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from common.infrastructure.app.app import App
from common.infrastructure.database.redis.redis import RedisDatabase
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.database.sqlalchemy.models.base import Base


@pytest.fixture
def app() -> App:
    app = main()
    return app


@pytest_asyncio.fixture
async def fastapi(app: App):
    fastapi = app.get_server().get_app()
    async with LifespanManager(fastapi) as manager:
        yield manager.app


@pytest_asyncio.fixture(autouse=True)
async def database(app: App):
    db: Database = Database.create(app.get_config().db)
    yield db
    await db.truncate_database(Base.metadata)
    await db.shutdown()


@pytest_asyncio.fixture(autouse=True)
async def redis(app: App):
    db: RedisDatabase = RedisDatabase.create(app.get_config().redis)
    yield db
    await db.flush_db()
    await db.shutdown()


@pytest_asyncio.fixture
async def client(fastapi: FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app=fastapi), base_url="http://test"
    ) as c:
        yield c
