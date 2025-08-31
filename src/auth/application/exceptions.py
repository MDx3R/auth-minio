from uuid import UUID

from common.application.exceptions import ApplicationError


class InvalidPasswordError(ApplicationError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"Invalid password for user {user_id}")
        self.user_id = user_id


class InvalidUsernameError(ApplicationError):
    def __init__(self, username: str) -> None:
        super().__init__(f"Invalid username: {username}")
        self.username = username


class TokenExpiredError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Token expired")


class TokenRevokedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Token revoked")


class InvalidTokenError(ApplicationError):
    def __init__(self, message: str = "Invalid token") -> None:
        super().__init__(message)
