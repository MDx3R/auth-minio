import pytest
import pytest_asyncio
from cli.app.monolith import main
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from common.infrastructure.app.app import App
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.database.sqlalchemy.models.base import Base


@pytest.fixture
def app() -> App:
    app = main()
    return app


@pytest.fixture
def fastapi(app: App) -> FastAPI:
    return app.get_server().get_app()


@pytest_asyncio.fixture(autouse=True)
async def database(app: App):
    db: Database = Database.create(app.get_config().db)
    yield db
    await db.truncate_database(Base.metadata)
    await db.shutdown()


@pytest_asyncio.fixture
async def client(fastapi: FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app=fastapi), base_url="http://test"
    ) as c:
        yield c
