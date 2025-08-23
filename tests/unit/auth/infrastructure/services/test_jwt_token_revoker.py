from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from auth.infrastructure.services.jwt.token_revoker import JWTTokenRevoker
from common.infrastructure.services.clock import FixedClock


@pytest.mark.asyncio
class TestJWTTokenRevoker:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.clock = FixedClock(datetime(2025, 7, 22))

        self.token = Mock()
        self.token.is_expired.return_value = False
        self.token.is_revoked.return_value = False
        self.token.user_id = uuid4()

        self.refresh_token_repo = Mock(spec=IRefreshTokenRepository)
        self.refresh_token_repo.get.return_value = self.token

        self.revoker = JWTTokenRevoker(self.clock, self.refresh_token_repo)

    async def test_revoke_token(self):
        token = "token"
        await self.revoker.revoke_refresh_token(token)

        self.refresh_token_repo.revoke.assert_awaited_once_with(token)

    async def test_revoke_expired_token_fails(self):
        self.token.is_expired.return_value = True

        await self.revoker.revoke_refresh_token("exprired-token")

        self.refresh_token_repo.revoke.assert_not_awaited()

    async def test_revoke_revoked_token_fails(self):
        self.token.is_revoked.return_value = True

        await self.revoker.revoke_refresh_token("revoked-token")

        self.refresh_token_repo.revoke.assert_not_awaited()
