from sqlalchemy import select, update

from auth.application.dtos.models.token import Token
from auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from auth.infrastructure.database.sqlalchemy.mappers.token_mapper import (
    TokenMapper,
)
from auth.infrastructure.database.sqlalchemy.models.token_base import (
    TokenBase,
)
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, executor: QueryExecutor):
        self.executor = executor

    async def get(self, value: str) -> Token:
        stmt = select(TokenBase).where(TokenBase.value == value)
        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(value)
        return TokenMapper.to_domain(result)

    async def revoke(self, value: str) -> None:
        stmt = (
            update(TokenBase)
            .where(TokenBase.value == value)
            .values(revoked=True)
        )
        await self.executor.execute(stmt)

    async def add(self, token: Token) -> None:
        base = TokenMapper.to_persistence(token)
        await self.executor.add(base)
