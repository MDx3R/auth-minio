from uuid import UUID

from auth.application.dtos.commands.register_user_command import (
    RegisterUserCommand,
)
from auth.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from auth.application.interfaces.usecases.command.register_user_use_case import (
    IRegisterUserUseCase,
)
from identity.application.exceptions import UsernameAlreadyTakenError
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.domain.interfaces.user_factory import IUserFactory


class RegisterUserUseCase(IRegisterUserUseCase):
    def __init__(
        self,
        user_factory: IUserFactory,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self.user_factory = user_factory
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, command: RegisterUserCommand) -> UUID:
        if await self.user_repository.exists_by_username(command.username):
            raise UsernameAlreadyTakenError(command.username)

        hashed_password = self.password_hasher.hash(command.password)
        user = self.user_factory.create(command.username, hashed_password)

        await self.user_repository.add(user)
        return user.user_id
