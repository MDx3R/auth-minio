from abc import ABC, abstractmethod
from uuid import UUID

from auth.application.dtos.commands.register_user_command import (
    RegisterUserCommand,
)


class IRegisterUserUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RegisterUserCommand) -> UUID: ...
