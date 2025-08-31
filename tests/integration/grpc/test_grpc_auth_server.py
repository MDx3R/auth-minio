from unittest.mock import AsyncMock
from uuid import uuid4

import grpc
import pytest
import pytest_asyncio
from grpc.aio import server as aio_server

from auth.application.dtos.models.auth_tokens import AuthTokens
from auth.application.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
)
from auth.application.interfaces.services.token_service import (
    ITokenIntrospector,
    ITokenIssuer,
    ITokenRefresher,
    ITokenRevoker,
)
from auth.infrastructure.server.grpc.services.token_service import (
    GRPCTokenIntrospector,
    GRPCTokenIssuer,
    GRPCTokenRefresher,
    GRPCTokenRevoker,
)
from auth.presentation.grpc.auth_service import AsyncAuthServiceServicer
from auth.presentation.grpc.generated import auth_pb2_grpc
from common.application.exceptions import ApplicationError
from identity.domain.value_objects.descriptor import UserDescriptor


@pytest.mark.asyncio
class TestGRPCClientServer:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        # Mock server-side services
        self.token_issuer = AsyncMock(spec=ITokenIssuer)
        self.token_refresher = AsyncMock(spec=ITokenRefresher)
        self.token_revoker = AsyncMock(spec=ITokenRevoker)
        self.token_introspector = AsyncMock(spec=ITokenIntrospector)

        self.user_id = uuid4()
        self.descriptor = UserDescriptor(
            user_id=self.user_id, username="testuser"
        )
        self.tokens = AuthTokens(
            user_id=self.user_id,
            access_token="access_token",
            refresh_token="refresh_token",
        )

        # Set up gRPC server
        self.server = aio_server()
        self.servicer = AsyncAuthServiceServicer(
            token_issuer=self.token_issuer,
            token_refresher=self.token_refresher,
            token_revoker=self.token_revoker,
            token_introspector=self.token_introspector,
        )
        auth_pb2_grpc.add_AuthServiceServicer_to_server(  # type: ignore
            self.servicer, self.server
        )
        self.port = self.server.add_insecure_port("[::]:0")  # Random port
        await self.server.start()

        # Set up gRPC client
        self.channel = grpc.aio.insecure_channel(f"localhost:{self.port}")
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

        # Instantiate client services
        self.issuer = GRPCTokenIssuer(self.stub)
        self.refresher = GRPCTokenRefresher(self.stub)
        self.revoker = GRPCTokenRevoker(self.stub)
        self.introspector = GRPCTokenIntrospector(self.stub)

        yield

        # Cleanup
        await self.server.stop(None)
        await self.channel.close()

    async def test_issue_tokens_success(self):
        # Arrange
        self.token_issuer.issue_tokens.return_value = self.tokens

        # Act
        result = await self.issuer.issue_tokens(self.user_id)

        # Assert
        assert isinstance(result, AuthTokens)
        assert result.user_id == self.user_id
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)

    async def test_issue_tokens_invalid_uuid(self):
        # Arrange
        invalid_uuid = "invalid-uuid"

        # Act & Assert
        with pytest.raises(ValueError, match="user_id must be a valid UUID"):
            await self.issuer.issue_tokens(invalid_uuid)  # type: ignore
        self.token_issuer.issue_tokens.assert_not_awaited()

    async def test_issue_tokens_internal_error(self):
        # Arrange
        self.token_issuer.issue_tokens.side_effect = Exception(
            "Unexpected error"
        )

        # Act & Assert
        with pytest.raises(ApplicationError, match="internal error"):
            await self.issuer.issue_tokens(self.user_id)
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)

    async def test_refresh_tokens_success(self):
        # Arrange
        self.token_refresher.refresh_tokens.return_value = self.tokens

        # Act
        result = await self.refresher.refresh_tokens("refresh_token")

        # Assert
        assert isinstance(result, AuthTokens)
        assert result.user_id == self.user_id
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        self.token_refresher.refresh_tokens.assert_awaited_once_with(
            "refresh_token"
        )

    async def test_refresh_tokens_invalid_token(self):
        # Arrange
        self.token_refresher.refresh_tokens.side_effect = InvalidTokenError()

        # Act & Assert
        with pytest.raises(InvalidTokenError, match="token is invalid"):
            await self.refresher.refresh_tokens("invalid_token")
        self.token_refresher.refresh_tokens.assert_awaited_once_with(
            "invalid_token"
        )

    async def test_refresh_tokens_expired_token(self):
        # Arrange
        self.token_refresher.refresh_tokens.side_effect = TokenExpiredError()

        # Act & Assert
        with pytest.raises(TokenExpiredError, match="token expired"):
            await self.refresher.refresh_tokens("expired_token")
        self.token_refresher.refresh_tokens.assert_awaited_once_with(
            "expired_token"
        )

    async def test_refresh_tokens_revoked_token(self):
        # Arrange
        self.token_refresher.refresh_tokens.side_effect = TokenRevokedError()

        # Act & Assert
        with pytest.raises(TokenRevokedError, match="token revoked"):
            await self.refresher.refresh_tokens("revoked_token")
        self.token_refresher.refresh_tokens.assert_awaited_once_with(
            "revoked_token"
        )

    async def test_revoke_token_success(self):
        # Arrange
        self.token_revoker.revoke_refresh_token.return_value = None

        # Act
        await self.revoker.revoke_refresh_token("refresh_token")

        # Assert
        self.token_revoker.revoke_refresh_token.assert_awaited_once_with(
            "refresh_token"
        )

    async def test_revoke_token_invalid_token(self):
        # Arrange
        self.token_revoker.revoke_refresh_token.side_effect = (
            InvalidTokenError()
        )

        # Act & Assert
        with pytest.raises(InvalidTokenError, match="token is invalid"):
            await self.revoker.revoke_refresh_token("invalid_token")
        self.token_revoker.revoke_refresh_token.assert_awaited_once_with(
            "invalid_token"
        )

    async def test_revoke_token_expired_token(self):
        # Arrange
        self.token_revoker.revoke_refresh_token.side_effect = (
            TokenExpiredError()
        )

        # Act & Assert
        with pytest.raises(TokenExpiredError, match="token expired"):
            await self.revoker.revoke_refresh_token("expired_token")
        self.token_revoker.revoke_refresh_token.assert_awaited_once_with(
            "expired_token"
        )

    async def test_revoke_token_revoked_token(self):
        # Arrange
        self.token_revoker.revoke_refresh_token.side_effect = (
            TokenRevokedError()
        )

        # Act & Assert
        with pytest.raises(TokenRevokedError, match="token revoked"):
            await self.revoker.revoke_refresh_token("revoked_token")
        self.token_revoker.revoke_refresh_token.assert_awaited_once_with(
            "revoked_token"
        )

    async def test_introspect_token_success(self):
        # Arrange
        self.token_introspector.extract_user.return_value = self.descriptor

        # Act
        result = await self.introspector.extract_user("access_token")

        # Assert
        assert isinstance(result, UserDescriptor)
        assert result.user_id == self.user_id
        assert result.username == "testuser"
        self.token_introspector.extract_user.assert_awaited_once_with(
            "access_token"
        )

    async def test_introspect_token_invalid_token(self):
        # Arrange
        self.token_introspector.extract_user.side_effect = InvalidTokenError()

        # Act & Assert
        with pytest.raises(InvalidTokenError, match="token is invalid"):
            await self.introspector.extract_user("invalid_token")
        self.token_introspector.extract_user.assert_awaited_once_with(
            "invalid_token"
        )

    async def test_introspect_token_expired_token(self):
        # Arrange
        self.token_introspector.extract_user.side_effect = TokenExpiredError()

        # Act & Assert
        with pytest.raises(TokenExpiredError, match="token expired"):
            await self.introspector.extract_user("expired_token")
        self.token_introspector.extract_user.assert_awaited_once_with(
            "expired_token"
        )

    async def test_introspect_token_revoked_token(self):
        # Arrange
        self.token_introspector.extract_user.side_effect = TokenRevokedError()

        # Act & Assert
        with pytest.raises(TokenRevokedError, match="token revoked"):
            await self.introspector.extract_user("revoked_token")
        self.token_introspector.extract_user.assert_awaited_once_with(
            "revoked_token"
        )

    async def test_map_grpc_error_unexpected(self):
        # Arrange
        self.token_introspector.extract_user.side_effect = Exception(
            "Unexpected error"
        )

        # Act & Assert
        with pytest.raises(ApplicationError, match="internal error"):
            await self.introspector.extract_user("access_token")
        self.token_introspector.extract_user.assert_awaited_once_with(
            "access_token"
        )
