from dependency_injector import containers, providers

from auth.application.usecases.command.login_use_case import LoginUseCase
from auth.application.usecases.command.logout_use_case import LogoutUseCase
from auth.application.usecases.command.refresh_token_use_case import (
    RefreshTokenUseCase,
)
from auth.application.usecases.command.register_user_use_case import (
    RegisterUserUseCase,
)
from auth.infrastructure.database.repositories.descriptor_repository import (
    UserDescriptorRepository,
)
from auth.infrastructure.database.sqlalchemy.repositories.refresh_token_repository import (
    RefreshTokenRepository,
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


class TokenContainer(containers.DeclarativeContainer):
    auth_config = providers.Dependency()
    clock = providers.Dependency()
    uuid_generator = providers.Dependency()
    token_generator = providers.Dependency()

    query_executor = providers.Dependency()
    user_repository = providers.Dependency()

    refresh_token_repository = providers.Singleton(
        RefreshTokenRepository, query_executor
    )
    user_desctiptor_repository = providers.Singleton(
        UserDescriptorRepository, user_repository
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
        user_repository=user_repository,
        clock=clock,
    )


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
