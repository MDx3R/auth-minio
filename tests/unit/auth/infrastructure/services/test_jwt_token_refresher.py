from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from auth.application.dtos.models.auth_tokens import AuthTokens
from auth.application.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
)
from auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from auth.infrastructure.services.jwt.token_issuer import JWTTokenIssuer
from auth.infrastructure.services.jwt.token_refresher import JWTTokenRefresher
from auth.infrastructure.services.jwt.token_revoker import JWTTokenRevoker
from common.application.exceptions import NotFoundError
from common.infrastructure.services.clock import FixedClock


@pytest.mark.asyncio
class TestJWTTokenRefresher:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()

        self.token_issuer = Mock(spec=JWTTokenIssuer)
        self.token_revoker = Mock(spec=JWTTokenRevoker)
        self.clock = FixedClock(datetime(2025, 7, 22))

        self.tokens = AuthTokens(self.user_id, "access_token", "refresh_token")
        self.token_issuer.issue_tokens.return_value = self.tokens

        self.token = Mock()
        self.token.is_expired.return_value = False
        self.token.is_revoked.return_value = False
        self.token.user_id = self.user_id

        self.refresh_token_repo = Mock(spec=IRefreshTokenRepository)
        self.refresh_token_repo.get.return_value = self.token

        self.refresher = JWTTokenRefresher(
            self.token_issuer,
            self.token_revoker,
            self.clock,
            self.refresh_token_repo,
        )

    async def test_refresh_valid_token(self):
        result = await self.refresher.refresh_tokens("refresh-token")

        assert isinstance(result, AuthTokens)
        assert result == self.tokens

        self.token_revoker.revoke_refresh_token.assert_awaited_once()
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)

    async def test_refresh_expired_token_fails(self):
        self.token.is_expired.return_value = True

        with pytest.raises(TokenExpiredError):
            await self.refresher.refresh_tokens("refresh-token")

        self.token_revoker.revoke_refresh_token.assert_not_awaited()
        self.token_issuer.issue_tokens.assert_not_awaited()

    async def test_refresh_revoked_token_fails(self):
        self.token.is_revoked.return_value = True

        with pytest.raises(TokenRevokedError):
            await self.refresher.refresh_tokens("refresh-token")

        self.token_revoker.revoke_refresh_token.assert_not_awaited()
        self.token_issuer.issue_tokens.assert_not_awaited()

    async def test_refresh_no_token_fails_with_invalid_token(self):
        self.refresh_token_repo.get.side_effect = NotFoundError("random-token")

        with pytest.raises(InvalidTokenError):
            await self.refresher.refresh_tokens("random-token")

        self.token_revoker.revoke_refresh_token.assert_not_awaited()
        self.token_issuer.issue_tokens.assert_not_awaited()
