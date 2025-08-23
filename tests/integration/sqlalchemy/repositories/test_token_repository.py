from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from auth.application.dtos.models.token import Token, TokenTypeEnum
from auth.infrastructure.database.sqlalchemy.mappers.token_mapper import (
    TokenMapper,
)
from auth.infrastructure.database.sqlalchemy.models.token_base import (
    TokenBase,
)
from auth.infrastructure.database.sqlalchemy.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor


@pytest.mark.asyncio
class TestRefreshTokenRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.token_repository = RefreshTokenRepository(query_executor)

    async def _add_token(self) -> Token:
        token = self._get_token()
        async with self.maker() as session:
            session.add(TokenMapper.to_persistence(token))
            await session.commit()
        return token

    def _get_token(self) -> Token:
        return Token(
            token_id=uuid4(),
            user_id=uuid4(),
            value=str(uuid4()),
            token_type=TokenTypeEnum.REFRESH,
            issued_at=datetime(2025, 7, 22, tzinfo=UTC),
            expires_at=datetime(2025, 7, 22, tzinfo=UTC) + timedelta(days=7),
            revoked=False,
        )

    async def _get(self, value: str) -> Token | None:
        async with self.maker() as session:
            stmt = await session.execute(
                select(TokenBase).where(TokenBase.value == value)
            )
            base = stmt.scalar_one_or_none()
            return TokenMapper.to_domain(base) if base else None

    async def test_add_success(self):
        new_token = self._get_token()
        await self.token_repository.add(new_token)

        stored = await self._get(new_token.value)
        assert stored == new_token

    async def test_get_success(self):
        token = await self._add_token()

        result = await self.token_repository.get(token.value)
        assert result == token

    async def test_get_not_found(self):
        with pytest.raises(NotFoundError):
            await self.token_repository.get("absent_token")

    async def test_revoke_success(self):
        token = await self._add_token()

        await self.token_repository.revoke(token.value)
        updated = await self._get(token.value)

        assert updated
        assert updated.revoked is True
