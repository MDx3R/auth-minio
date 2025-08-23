from uuid import UUID

from common.application.exceptions import NotFoundError


class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: UUID):
        super().__init__(user_id)
