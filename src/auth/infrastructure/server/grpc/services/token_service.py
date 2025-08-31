from uuid import UUID

import grpc

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
from auth.presentation.grpc.generated import auth_pb2, auth_pb2_grpc
from common.application.exceptions import ApplicationError
from identity.domain.value_objects.descriptor import UserDescriptor


def map_grpc_error(error: grpc.aio.AioRpcError) -> Exception:
    status_code = error.code()
    details = error.details()

    if status_code == grpc.StatusCode.UNAUTHENTICATED:
        if details == "token expired":
            return TokenExpiredError()
        elif details == "token revoked":
            return TokenRevokedError()
        elif details == "token is invalid":
            return InvalidTokenError()
        return InvalidTokenError()

    if status_code == grpc.StatusCode.INVALID_ARGUMENT:
        return ValueError(details)

    return ApplicationError(details or "Internal error")


class GRPCTokenIssuer(ITokenIssuer):
    def __init__(self, stub: auth_pb2_grpc.AuthServiceStub) -> None:
        self.stub = stub

    async def issue_tokens(self, user_id: UUID) -> AuthTokens:
        try:
            request = auth_pb2.IssueTokensRequest(user_id=str(user_id))
            response: auth_pb2.AuthResponse = await self.stub.IssueTokens(  # type: ignore
                request
            )
            return AuthTokens(
                user_id=UUID(response.user_id),  # type: ignore
                access_token=response.access_token,  # type: ignore
                refresh_token=response.refresh_token,  # type: ignore
            )
        except grpc.aio.AioRpcError as e:
            raise map_grpc_error(e) from e


class GRPCTokenRefresher(ITokenRefresher):
    def __init__(self, stub: auth_pb2_grpc.AuthServiceStub) -> None:
        self.stub = stub

    async def refresh_tokens(self, refresh_token: str) -> AuthTokens:
        try:
            request = auth_pb2.RefreshTokensRequest(
                refresh_token=refresh_token
            )
            response: auth_pb2.AuthResponse = await self.stub.RefreshTokens(  # type: ignore
                request
            )
            return AuthTokens(
                user_id=UUID(response.user_id),  # type: ignore
                access_token=response.access_token,  # type: ignore
                refresh_token=response.refresh_token,  # type: ignore
            )
        except grpc.aio.AioRpcError as e:
            raise map_grpc_error(e) from e


class GRPCTokenRevoker(ITokenRevoker):
    def __init__(self, stub: auth_pb2_grpc.AuthServiceStub) -> None:
        self.stub = stub

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        try:
            request = auth_pb2.RevokeTokenRequest(refresh_token=refresh_token)
            await self.stub.RevokeToken(request)  # type: ignore
        except grpc.aio.AioRpcError as e:
            raise map_grpc_error(e) from e


class GRPCTokenIntrospector(ITokenIntrospector):
    def __init__(self, stub: auth_pb2_grpc.AuthServiceStub) -> None:
        self.stub = stub

    async def extract_user(self, token: str) -> UserDescriptor:
        try:
            request = auth_pb2.IntrospectTokenRequest(access_token=token)
            response: auth_pb2.IntrospectionResponse = (  # type: ignore
                await self.stub.IntrospectToken(request)  # type: ignore
            )
            return UserDescriptor(
                user_id=UUID(response.user_id),  # type: ignore
                username=response.username,  # type: ignore
            )
        except grpc.aio.AioRpcError as e:
            raise map_grpc_error(e) from e

    async def is_token_valid(self, token: str) -> bool:
        raise NotImplementedError

    async def validate(self, token: str) -> UUID:
        raise NotImplementedError
