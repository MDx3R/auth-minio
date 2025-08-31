from auth.application.dtos.commands.login_command import LoginCommand
from auth.application.dtos.models.auth_tokens import AuthTokens
from auth.application.exceptions import (
    InvalidPasswordError,
    InvalidUsernameError,
)
from auth.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from auth.application.interfaces.services.token_service import ITokenIssuer
from auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)


class LoginUseCase(ILoginUseCase):
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        token_issuer: ITokenIssuer,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_issuer = token_issuer

    async def execute(self, command: LoginCommand) -> AuthTokens:
        if not await self.user_repository.exists_by_username(command.username):
            raise InvalidUsernameError(command.username)

        user = await self.user_repository.get_by_username(command.username)
        if not self.password_hasher.verify(command.password, user.password):
            raise InvalidPasswordError(user.user_id)

        return await self.token_issuer.issue_tokens(user.user_id)
