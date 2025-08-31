from dependency_injector import containers, providers

from auth.application.repositories.caching_descriptor_repository import (
    CachingUserDescriptorRepository,
)
from auth.application.repositories.descriptor_repository import (
    UserDescriptorRepository,
)
from auth.application.usecases.command.login_use_case import LoginUseCase
from auth.application.usecases.command.logout_use_case import LogoutUseCase
from auth.application.usecases.command.refresh_token_use_case import (
    RefreshTokenUseCase,
)
from auth.application.usecases.command.register_user_use_case import (
    RegisterUserUseCase,
)
from auth.infrastructure.database.sqlalchemy.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from auth.infrastructure.serializers.marshmallow.shemas import (
    UserDescriptorSchema,
)
from auth.infrastructure.server.grpc.services.token_service import (
    GRPCTokenIntrospector,
    GRPCTokenIssuer,
    GRPCTokenRefresher,
    GRPCTokenRevoker,
)
from auth.infrastructure.services.bcrypt.password_hasher import (
    BcryptPasswordHasher,
)
from auth.infrastructure.services.jwt.token_introspector import (
    JWTTokenIntrospector,
)
from auth.infrastructure.services.jwt.token_issuer import JWTTokenIssuer
from auth.infrastructure.services.jwt.token_refresher import JWTTokenRefresher
from auth.infrastructure.services.jwt.token_revoker import JWTTokenRevoker
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
from identity.domain.value_objects.descriptor import UserDescriptor


class TokenContainer(containers.DeclarativeContainer):
    ttl = providers.Dependency()
    namespace = providers.Dependency()

    auth_config = providers.Dependency()
    clock = providers.Dependency()
    uuid_generator = providers.Dependency()
    token_generator = providers.Dependency()

    query_executor = providers.Dependency()
    redis = providers.Dependency()
    user_repository = providers.Dependency()

    refresh_token_repository = providers.Singleton(
        RefreshTokenRepository, query_executor
    )
    user_descriptor_repository = providers.Singleton(
        UserDescriptorRepository, user_repository
    )

    user_descriptor_serializer = providers.Singleton(
        MarshmallowSerializer[UserDescriptor], UserDescriptorSchema()
    )

    key_value_store: providers.Singleton[IKeyValueStore[UserDescriptor]] = (
        providers.Singleton(
            redis_key_value_store_provider,
            redis=redis,
            serializer=user_descriptor_serializer,
            namespace=namespace,
        )
    )

    key_value_cache = providers.Singleton(
        TTLKeyValueCache, store=key_value_store, ttl=ttl
    )

    caching_user_read_repository = providers.Singleton(
        CachingUserDescriptorRepository,
        user_descriptor_repository=user_descriptor_repository,
        key_value_cache=key_value_cache,
    )

    token_issuer = providers.Singleton(
        JWTTokenIssuer,
        config=auth_config,
        token_generator=token_generator,
        uuid_generator=uuid_generator,
        clock=clock,
        refresh_token_repository=refresh_token_repository,
    )
    token_revoker = providers.Singleton(
        JWTTokenRevoker,
        clock=clock,
        refresh_token_repository=refresh_token_repository,
    )
    token_refresher = providers.Singleton(
        JWTTokenRefresher,
        token_issuer=token_issuer,
        token_revoker=token_revoker,
        clock=clock,
        refresh_token_repository=refresh_token_repository,
    )
    token_introspector = providers.Singleton(
        JWTTokenIntrospector,
        config=auth_config,
        user_descriptor_repository=caching_user_read_repository,
        clock=clock,
    )


class GRPCTokenContainer(TokenContainer):
    stub = providers.Dependency()

    token_issuer = providers.Singleton(GRPCTokenIssuer, stub)
    token_revoker = providers.Singleton(GRPCTokenRevoker, stub)
    token_refresher = providers.Singleton(GRPCTokenRefresher, stub)
    token_introspector = providers.Singleton(GRPCTokenIntrospector, stub)


class AuthContainer(containers.DeclarativeContainer):
    uuid_generator = providers.Dependency()
    user_factory = providers.Dependency()

    user_repository = providers.Dependency()

    token_issuer = providers.Dependency()
    token_revoker = providers.Dependency()
    token_refresher = providers.Dependency()

    password_hasher = providers.Singleton(BcryptPasswordHasher)

    register_user_use_case = providers.Singleton(
        RegisterUserUseCase,
        user_factory=user_factory,
        user_repository=user_repository,
        password_hasher=password_hasher,
    )

    login_use_case = providers.Singleton(
        LoginUseCase,
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
    )

    refresh_token_use_case = providers.Singleton(
        RefreshTokenUseCase, token_refresher
    )
    logout_use_case = providers.Singleton(LogoutUseCase, token_revoker)
