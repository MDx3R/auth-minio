from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import ClassVar

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from auth.application.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
)
from common.application.exceptions import (
    ApplicationError,
    DuplicateEntryError,
    NotFoundError,
    OptimisticLockError,
    RepositoryError,
)
from common.domain.exceptions import DomainError


class IHTTPErrorHandler(ABC):
    @abstractmethod
    def handle(self, request: Request, exc: Exception) -> JSONResponse: ...


class DomainErrorHandler(IHTTPErrorHandler):
    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )


class ApplicationErrorHandler(IHTTPErrorHandler):
    ERROR_STATUS_MAP: ClassVar[dict[type[Exception], int]] = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        TokenExpiredError: status.HTTP_401_UNAUTHORIZED,
        TokenRevokedError: status.HTTP_401_UNAUTHORIZED,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    }

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        status_code = self.ERROR_STATUS_MAP.get(
            type(exc), status.HTTP_400_BAD_REQUEST
        )
        return JSONResponse(
            status_code=status_code,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )


class RepositoryErrorHandler(IHTTPErrorHandler):
    ERROR_STATUS_MAP: ClassVar[dict[type[Exception], int]] = {
        DuplicateEntryError: status.HTTP_409_CONFLICT,
        OptimisticLockError: status.HTTP_409_CONFLICT,
    }

    def handle(self, request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, OptimisticLockError):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "OptimisticLockError",
                    "detail": f"Retry later: {exc!s}",
                },
            )

        status_code = self.ERROR_STATUS_MAP.get(
            type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": type(exc).__name__,
                "detail": str(exc),
            },
        )


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    HANDLERS: ClassVar[dict[type[Exception], IHTTPErrorHandler]] = {
        DomainError: DomainErrorHandler(),
        ApplicationError: ApplicationErrorHandler(),
        RepositoryError: RepositoryErrorHandler(),
    }

    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            for exc_type, handler in self.HANDLERS.items():
                if isinstance(exc, exc_type):
                    return handler.handle(request, exc)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "InternalError", "detail": str(exc)},
            )
