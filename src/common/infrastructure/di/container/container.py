from dependency_injector import containers, providers

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from common.infrastructure.di.container.providers import (
    provide_maker_session_factory,
)
from common.infrastructure.services.clock import SystemClock
from common.infrastructure.services.id_generator import UUID4Generator
from common.infrastructure.services.secrets_token_generator import (
    SecretsTokenGenerator,
)


class CommonContainer(containers.DeclarativeContainer):
    config = providers.Dependency()
    database = providers.Dependency()

    # ---------------------- General ----------------------
    clock = providers.Singleton(SystemClock)
    uuid_generator = providers.Singleton(UUID4Generator)
    token_generator = providers.Singleton(SecretsTokenGenerator)

    # ---------------------- Database ----------------------
    session_factory = providers.Singleton(
        provide_maker_session_factory, database
    )
    unit_of_work = providers.Singleton(UnitOfWork, session_factory)
    query_executor = providers.Singleton(QueryExecutor, unit_of_work)
