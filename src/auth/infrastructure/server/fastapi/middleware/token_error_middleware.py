from typing import ClassVar

from fastapi import status

from auth.application.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
)
from common.infrastructure.server.fastapi.middleware.error_middleware import (
    ApplicationErrorHandler,
)


class TokenErrorHandler(ApplicationErrorHandler):
    ERROR_STATUS_MAP: ClassVar[dict[type[Exception], int]] = {
        TokenExpiredError: status.HTTP_401_UNAUTHORIZED,
        TokenRevokedError: status.HTTP_401_UNAUTHORIZED,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    }

    def can_handle(self, exc: Exception) -> bool:
        return type(exc) in self.ERROR_STATUS_MAP
