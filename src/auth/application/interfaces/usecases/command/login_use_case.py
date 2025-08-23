from abc import ABC, abstractmethod

from auth.application.dtos.commands.login_command import LoginCommand
from auth.application.dtos.models.auth_tokens import AuthTokens


class ILoginUseCase(ABC):
    @abstractmethod
    async def execute(self, command: LoginCommand) -> AuthTokens: ...
