from unittest.mock import AsyncMock
from uuid import uuid4

import grpc
import pytest
from google.protobuf import empty_pb2
from grpc import StatusCode

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
from auth.presentation.grpc.auth_service import AsyncAuthServiceServicer
from auth.presentation.grpc.generated import auth_pb2
from identity.domain.value_objects.descriptor import UserDescriptor


@pytest.mark.asyncio
class TestAsyncAuthServiceServicer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.token_issuer = AsyncMock(spec=ITokenIssuer)
        self.token_refresher = AsyncMock(spec=ITokenRefresher)
        self.token_revoker = AsyncMock(spec=ITokenRevoker)
        self.token_introspector = AsyncMock(spec=ITokenIntrospector)
        self.context = AsyncMock()
        self.context.abort.side_effect = grpc.aio.AioRpcError(
            grpc.StatusCode.UNKNOWN, grpc.aio.Metadata(), grpc.aio.Metadata()
        )
        self.servicer = AsyncAuthServiceServicer(
            token_issuer=self.token_issuer,
            token_refresher=self.token_refresher,
            token_revoker=self.token_revoker,
            token_introspector=self.token_introspector,
        )
        self.user_id = uuid4()
        self.descriptor = UserDescriptor(
            user_id=self.user_id, username="testuser"
        )
        self.tokens = AuthTokens(
            user_id=self.user_id,
            access_token="access_token",
            refresh_token="refresh_token",
        )

    async def test_issue_tokens_success(self):
        # Arrange
        request = auth_pb2.IssueTokensRequest(user_id=str(self.user_id))
        self.token_issuer.issue_tokens.return_value = self.tokens

        # Act
        response = await self.servicer.IssueTokens(request, self.context)

        # Assert
        assert response.user_id == str(self.user_id)  # type: ignore
        assert response.access_token == "access_token"  # type: ignore
        assert response.refresh_token == "refresh_token"  # type: ignore
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)
        self.context.abort.assert_not_called()

    async def test_issue_tokens_invalid_uuid(self):
        # Arrange
        request = auth_pb2.IssueTokensRequest(user_id="invalid-uuid")

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.IssueTokens(request, self.context)

        self.context.abort.assert_awaited_once_with(
            StatusCode.INVALID_ARGUMENT, "user_id must be a valid UUID"
        )
        self.token_issuer.issue_tokens.assert_not_awaited()

    async def test_issue_tokens_internal_error(self):
        # Arrange
        request = auth_pb2.IssueTokensRequest(user_id=str(self.user_id))
        self.token_issuer.issue_tokens.side_effect = Exception(
            "Unexpected error"
        )

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.IssueTokens(request, self.context)
        self.context.abort.assert_awaited_once_with(
            StatusCode.INTERNAL, "internal error"
        )
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)

    async def test_refresh_tokens_success(self):
        # Arrange
        request = auth_pb2.RefreshTokensRequest(refresh_token="refresh_token")
        self.token_refresher.refresh_tokens.return_value = self.tokens

        # Act
        response = await self.servicer.RefreshTokens(request, self.context)

        # Assert
        assert response.user_id == str(self.user_id)  # type: ignore
        assert response.access_token == "access_token"  # type: ignore
        assert response.refresh_token == "refresh_token"  # type: ignore
        self.token_refresher.refresh_tokens.assert_awaited_once_with(
            "refresh_token"
        )
        self.context.abort.assert_not_called()

    async def test_refresh_tokens_invalid_token(self):
        # Arrange
        request = auth_pb2.RefreshTokensRequest(refresh_token="invalid_token")
        self.token_refresher.refresh_tokens.side_effect = InvalidTokenError()

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.RefreshTokens(request, self.context)
        self.context.abort.assert_awaited_once_with(
            StatusCode.UNAUTHENTICATED, "token is invalid"
        )
        self.token_refresher.refresh_tokens.assert_awaited_once_with(
            "invalid_token"
        )

    async def test_revoke_token_success(self):
        # Arrange
        request = auth_pb2.RevokeTokenRequest(refresh_token="refresh_token")
        self.token_revoker.revoke_refresh_token.return_value = None

        # Act
        response = await self.servicer.RevokeToken(request, self.context)

        # Assert
        assert isinstance(response, empty_pb2.Empty)
        self.token_revoker.revoke_refresh_token.assert_awaited_once_with(
            "refresh_token"
        )
        self.context.abort.assert_not_called()

    async def test_revoke_token_expired(self):
        # Arrange
        request = auth_pb2.RevokeTokenRequest(refresh_token="expired_token")
        self.token_revoker.revoke_refresh_token.side_effect = (
            TokenExpiredError()
        )

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.RevokeToken(request, self.context)
        self.context.abort.assert_awaited_once_with(
            StatusCode.UNAUTHENTICATED, "token expired"
        )
        self.token_revoker.revoke_refresh_token.assert_awaited_once_with(
            "expired_token"
        )

    async def test_introspect_token_success(self):
        # Arrange
        request = auth_pb2.IntrospectTokenRequest(access_token="access_token")
        self.token_introspector.extract_user.return_value = self.descriptor

        # Act
        response = await self.servicer.IntrospectToken(request, self.context)

        # Assert
        assert response.user_id == str(self.user_id)  # type: ignore
        assert response.username == "testuser"  # type: ignore
        self.token_introspector.extract_user.assert_awaited_once_with(
            "access_token"
        )
        self.context.abort.assert_not_called()

    async def test_introspect_token_revoked(self):
        # Arrange
        request = auth_pb2.IntrospectTokenRequest(access_token="revoked_token")
        self.token_introspector.extract_user.side_effect = TokenRevokedError()

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.IntrospectToken(request, self.context)
        self.context.abort.assert_awaited_once_with(
            StatusCode.UNAUTHENTICATED, "token revoked"
        )
        self.token_introspector.extract_user.assert_awaited_once_with(
            "revoked_token"
        )

    async def test_handle_grpc_error_invalid_token(self):
        # Arrange
        exc = InvalidTokenError()

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.handle_grpc_error(self.context, exc)
        self.context.abort.assert_awaited_once_with(
            StatusCode.UNAUTHENTICATED, "token is invalid"
        )

    async def test_handle_grpc_error_token_expired(self):
        # Arrange
        exc = TokenExpiredError()

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.handle_grpc_error(self.context, exc)
        self.context.abort.assert_awaited_once_with(
            StatusCode.UNAUTHENTICATED, "token expired"
        )

    async def test_handle_grpc_error_token_revoked(self):
        # Arrange
        exc = TokenRevokedError()

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.handle_grpc_error(self.context, exc)
        self.context.abort.assert_awaited_once_with(
            StatusCode.UNAUTHENTICATED, "token revoked"
        )

    async def test_handle_grpc_error_unexpected(self):
        # Arrange
        exc = Exception("Unexpected error")

        # Act & Assert
        with pytest.raises(grpc.aio.AioRpcError):
            await self.servicer.handle_grpc_error(self.context, exc)
        self.context.abort.assert_awaited_once_with(
            StatusCode.INTERNAL, "internal error"
        )
