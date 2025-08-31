from typing import Any
from uuid import UUID

import grpc

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


class AsyncAuthServiceServicer(auth_pb2_grpc.AuthServiceServicer):
    def __init__(
        self,
        token_issuer: ITokenIssuer,
        token_refresher: ITokenRefresher,
        token_revoker: ITokenRevoker,
        token_introspector: ITokenIntrospector,
    ) -> None:
        super().__init__()
        self.token_issuer = token_issuer
        self.token_refresher = token_refresher
        self.token_revoker = token_revoker
        self.token_introspector = token_introspector

    async def IssueTokens(
        self, request: auth_pb2.IssueTokensRequest, context: Any
    ):
        try:
            user_id = UUID(request.user_id)
            tokens = await self.token_issuer.issue_tokens(user_id)
            return auth_pb2.AuthResponse(
                user_id=str(tokens.user_id),
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
            )
        except ValueError:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "user_id must be a valid UUID",
            )
        except Exception as e:
            await self.handle_grpc_error(context, e)

    async def RefreshTokens(
        self, request: auth_pb2.RefreshTokensRequest, context: Any
    ):
        try:
            tokens = await self.token_refresher.refresh_tokens(
                request.refresh_token
            )
            return auth_pb2.AuthResponse(
                user_id=str(tokens.user_id),
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
            )
        except Exception as e:
            await self.handle_grpc_error(context, e)

    async def RevokeToken(
        self, request: auth_pb2.RevokeTokenRequest, context: Any
    ):
        try:
            await self.token_revoker.revoke_refresh_token(
                request.refresh_token
            )
            return auth_pb2.Empty()
        except Exception as e:
            await self.handle_grpc_error(context, e)

    async def IntrospectToken(
        self, request: auth_pb2.IntrospectTokenRequest, context: Any
    ):
        try:
            user = await self.token_introspector.extract_user(
                request.access_token
            )
            return auth_pb2.IntrospectionResponse(
                user_id=str(user.user_id), username=user.username
            )
        except Exception as e:
            await self.handle_grpc_error(context, e)

    async def handle_grpc_error(self, context: Any, exc: Exception) -> None:
        match exc:
            case InvalidTokenError():
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "token is invalid"
                )
            case TokenExpiredError():
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "token expired"
                )
            case TokenRevokedError():
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "token revoked"
                )
            case _:  # fallback
                await context.abort(grpc.StatusCode.INTERNAL, "internal error")
