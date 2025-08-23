from common.application.exceptions import ApplicationError, NotFoundError


class UserNotFoundError(NotFoundError):
    pass


class UsernameAlreadyTakenError(ApplicationError):
    def __init__(self, username: str):
        super().__init__(
            f"Username '{username}' is already taken by another user."
        )
        self.username = username
