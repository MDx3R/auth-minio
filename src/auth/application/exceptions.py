from common.application.exceptions import ApplicationError


class TokenExpiredError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Token expired")


class TokenRevokedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Token revoked")


class InvalidTokenError(ApplicationError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Invalid token")
