import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from auth.application.interfaces.services.token_service import (
    ITokenIntrospector,
)
from auth.infrastructure.di.container.container import TokenContainer
from common.infrastructure.config.config import AppConfig
from common.infrastructure.di.container.container import CommonContainer
from common.infrastructure.server.fastapi.middleware.error_middleware import (
    ErrorHandlingMiddleware,
)
from common.infrastructure.server.fastapi.middleware.logging_middleware import (
    LoggingMiddleware,
)
from common.infrastructure.server.fastapi.server import FastAPIServer


class IApp(ABC):
    @abstractmethod
    def configure(self) -> None: ...


class App(IApp):
    def __init__(
        self,
        config: AppConfig,
        logger: logging.Logger,
        container: CommonContainer,
        server: FastAPIServer,
    ) -> None:
        self.config = config
        self.logger = logger
        self.container = container
        self.server = server

    def configure(self):
        self.server.use_middleware(ErrorHandlingMiddleware)
        self.server.use_middleware(LoggingMiddleware, logger=self.logger)

    def configure_auth_dependencies(
        self, token_container: TokenContainer
    ) -> None:
        self.server.override_dependency(
            ITokenIntrospector, token_container.token_introspector()
        )
        self.logger.debug("Auth dependencies configured")

    def add_app(self, *apps: IApp) -> None:
        for app in apps:
            app.configure()
            self.logger.info(
                f"Sub-application '{app.__class__.__name__}' registered successfully"
            )

    def add_shutdown_rule(self, *rules: Callable[..., Any]) -> None:
        for rule in rules:
            self.server.on_tear_down(rule)

    def run(self):
        import uvicorn  # noqa: PLC0415

        self.logger.info(
            "Service is starting with uvicorn on 0.0.0.0:8000",
            extra={"port": 8000, "host": "0.0.0.0"},
        )
        uvicorn.run(
            self.server.get_app(), host="0.0.0.0", port=8000
        )  # TODO: Add config
        self.logger.info("Uvicorn stopped")

    def get_server(self) -> FastAPIServer:
        return self.server

    def get_logger(self) -> logging.Logger:
        return self.logger
