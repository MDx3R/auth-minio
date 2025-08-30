from dependency_injector import containers, providers

from common.application.interfaces.repositories.key_value_store import (
    IKeyValueStore,
)
from common.infrastructure.database.repositories.key_value_cache import (
    TTLKeyValueCache,
)
from common.infrastructure.di.container.providers import (
    redis_key_value_store_provider,
)
from common.infrastructure.serializers.marshmallow.serializer import (
    MarshmallowSerializer,
)
from identity.application.read_models.user_read_model import UserReadModel
from identity.application.repositories.caching_user_read_repository import (
    CachingUserReadRepository,
)
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
from identity.infrastructure.serializers.marshmallow.shemas import (
    UserReadModelSchema,
)


class IdentityContainer(containers.DeclarativeContainer):
    ttl = providers.Dependency()
    namespace = providers.Dependency()

    uuid_generator = providers.Dependency()
    query_executor = providers.Dependency()
    redis = providers.Dependency()

    user_factory = providers.Singleton(UserFactory, uuid_generator)
    user_repository = providers.Singleton(UserRepository, query_executor)
    user_read_repository = providers.Singleton(
        UserReadRepository, query_executor
    )

    user_read_model_serializer = providers.Singleton(
        MarshmallowSerializer[UserReadModel], UserReadModelSchema()
    )

    key_value_store: providers.Singleton[IKeyValueStore[UserReadModel]] = (
        providers.Singleton(
            redis_key_value_store_provider,
            redis=redis,
            serializer=user_read_model_serializer,
            namespace=namespace,
        )
    )

    key_value_cache = providers.Singleton(
        TTLKeyValueCache, store=key_value_store, ttl=ttl
    )

    caching_user_read_repository = providers.Singleton(
        CachingUserReadRepository,
        user_read_repository=user_read_repository,
        key_value_cache=key_value_cache,
    )

    get_self_use_case = providers.Singleton(
        GetSelfUseCase, caching_user_read_repository
    )
