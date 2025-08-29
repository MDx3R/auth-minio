from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi_utils.cbv import cbv

from auth.application.dtos.commands.login_command import LoginCommand
from auth.application.dtos.commands.logout_command import LogoutCommand
from auth.application.dtos.commands.refresh_token_command import (
    RefreshTokenCommand,
)
from auth.application.dtos.commands.register_user_command import (
    RegisterUserCommand,
)
from auth.application.exceptions import (
    InvalidPasswordError,
    InvalidUsernameError,
)
from auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from auth.application.interfaces.usecases.command.logout_use_case import (
    ILogoutUseCase,
)
from auth.application.interfaces.usecases.command.refresh_token_use_case import (
    IRefreshTokenUseCase,
)
from auth.application.interfaces.usecases.command.register_user_use_case import (
    IRegisterUserUseCase,
)
from auth.presentation.http.dto.request import (
    RegisterUserRequest,
)
from auth.presentation.http.dto.response import AuthTokensResponse
from auth.presentation.http.fastapi.auth import (
    get_token,
    require_authenticated,
    require_unauthenticated,
)
from common.presentation.http.dto.response import IDResponse
from identity.application.exceptions import UsernameAlreadyTakenError


auth_router = APIRouter()


@cbv(auth_router)
class AuthController:
    login_use_case: ILoginUseCase = Depends()
    logout_use_case: ILogoutUseCase = Depends()
    refresh_token_use_case: IRefreshTokenUseCase = Depends()
    register_user_use_case: IRegisterUserUseCase = Depends()

    @auth_router.post(
        "/login",
        response_model=AuthTokensResponse,
        dependencies=[Depends(require_unauthenticated)],
    )
    async def login(
        self,
        username: str = Form(...),
        password: str = Form(...),
    ):
        try:
            result = await self.login_use_case.execute(
                LoginCommand(username=username, password=password)
            )
            return AuthTokensResponse(**asdict(result))
        except InvalidUsernameError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "InvalidUsernameError",
                    "username": exc.username,
                    "detail": str(exc),
                },
            )
        except InvalidPasswordError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "InvalidPasswordError",
                    "user_id": str(exc.user_id),
                    "detail": str(exc),
                },
            )

    @auth_router.post(
        "/logout",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def logout(self, token: Annotated[str, Depends(get_token)]):
        await self.logout_use_case.execute(LogoutCommand(refresh_token=token))

    @auth_router.post(
        "/refresh",
        response_model=AuthTokensResponse,
        dependencies=[Depends(require_authenticated)],
    )
    async def refresh(self, token: Annotated[str, Depends(get_token)]):
        result = await self.refresh_token_use_case.execute(
            RefreshTokenCommand(token)
        )
        return AuthTokensResponse(**asdict(result))

    @auth_router.post(
        "/register",
        response_model=IDResponse,
        dependencies=[Depends(require_unauthenticated)],
    )
    async def register(self, request: RegisterUserRequest):
        try:
            result = await self.register_user_use_case.execute(
                RegisterUserCommand(
                    username=request.username, password=request.password
                )
            )
            return IDResponse.from_uuid(result)
        except UsernameAlreadyTakenError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "UsernameAlreadyTakenError",
                    "username": exc.username,
                    "detail": str(exc),
                },
            )
