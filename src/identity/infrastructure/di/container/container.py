from dependency_injector import containers, providers

from identity.application.usecases.query.get_self_use_case import (
    GetSelfUseCase,
)
from identity.domain.factories.user_factory import UserFactory
from identity.infrastructure.database.sqlalchemy.repositories.user_read_repository import (
    UserReadRepository,
)
from identity.infrastructure.database.sqlalchemy.repositories.user_repository import (
    UserRepository,
)


class IdentityContainer(containers.DeclarativeContainer):
    uuid_generator = providers.Dependency()
    query_executor = providers.Dependency()

    user_factory = providers.Singleton(UserFactory, uuid_generator)
    user_repository = providers.Singleton(UserRepository, query_executor)
    user_read_repository = providers.Singleton(
        UserReadRepository, query_executor
    )

    get_self_use_case = providers.Singleton(
        GetSelfUseCase, user_read_repository
    )
