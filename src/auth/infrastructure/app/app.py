from typing import ClassVar

from auth.application.interfaces.services.token_service import (
    ITokenIntrospector,
)
from auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from auth.application.interfaces.usecases.command.logout_use_case import (
    ILogoutUseCase,
)
from auth.application.interfaces.usecases.command.refresh_token_use_case import (
    IRefreshTokenUseCase,
)
from auth.application.interfaces.usecases.command.register_user_use_case import (
    IRegisterUserUseCase,
)
from auth.infrastructure.di.container.container import (
    AuthContainer,
    TokenContainer,
)
from auth.presentation.http.fastapi.controllers import auth_router
from common.infrastructure.app.http_app import IHTTPApp
from common.infrastructure.server.fastapi.server import FastAPIServer
from identity.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)
from identity.infrastructure.di.container.container import IdentityContainer
from identity.presentation.http.fastapi.controllers import query_router


class AuthApp(IHTTPApp):
    prefix = "/auth"
    tags: ClassVar = ["Auth"]

    def __init__(
        self,
        auth_container: AuthContainer,
        identity_container: IdentityContainer,
        server: FastAPIServer,
    ) -> None:
        self.auth_container = auth_container
        self.identity_container = identity_container
        self.server = server

    def configure_dependencies(self) -> None:
        self.server.override_dependency(
            ILoginUseCase, self.auth_container.login_use_case()
        )
        self.server.override_dependency(
            ILogoutUseCase, self.auth_container.logout_use_case()
        )
        self.server.override_dependency(
            IRegisterUserUseCase, self.auth_container.register_user_use_case()
        )
        self.server.override_dependency(
            IRefreshTokenUseCase, self.auth_container.refresh_token_use_case()
        )
        self.server.override_dependency(
            IGetSelfUseCase, self.identity_container.get_self_use_case()
        )

    def register_routers(self) -> None:
        self.server.register_router(auth_router, self.prefix, self.tags)
        self.server.register_router(query_router, self.prefix, self.tags)


class TokenApp(IHTTPApp):
    def __init__(
        self,
        container: TokenContainer,
        server: FastAPIServer,
    ) -> None:
        self.container = container
        self.server = server

    def configure_dependencies(self) -> None:
        self.server.override_dependency(
            ITokenIntrospector, self.container.token_introspector()
        )

    def register_routers(self) -> None:
        pass
