from identity.application.dtos.queries.get_user_be_id_query import (
    GetUserByIdQuery,
)
from identity.application.dtos.responses.user_dto import UserDTO
from identity.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from identity.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)


class GetSelfUseCase(IGetSelfUseCase):
    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def execute(self, query: GetUserByIdQuery) -> UserDTO:
        user = await self.user_repository.get_by_id(query.user_id)
        return UserDTO.from_user(user)
