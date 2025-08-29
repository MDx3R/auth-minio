import logging
from abc import ABC, abstractmethod

from common.infrastructure.config.config import AppConfig
from common.infrastructure.server.fastapi.middleware.error_middleware import (
    ApplicationErrorHandler,
    DomainErrorHandler,
    ErrorHandlingMiddleware,
    RepositoryErrorHandler,
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
        self, config: AppConfig, logger: logging.Logger, server: FastAPIServer
    ) -> None:
        self.config = config
        self.logger = logger
        self.server = server

    def configure(self) -> None:
        """Must be called after configuration of sub apps"""
        self.server.use_middleware(
            ErrorHandlingMiddleware,
            handlers=[
                RepositoryErrorHandler(),
                ApplicationErrorHandler(),
                DomainErrorHandler(),
            ],
        )
        self.server.use_middleware(LoggingMiddleware, logger=self.logger)
        self.server.include_cors_middleware()

    def add_app(self, *apps: IApp) -> None:
        for app in apps:
            app.configure()
            self.logger.info(
                f"Sub-application '{app.__class__.__name__}' registered successfully"
            )

    def run(self) -> None:
        import uvicorn  # noqa: PLC0415

        self.logger.info(
            "Service is starting with uvicorn on 0.0.0.0:8000",
            extra={"port": 8000, "host": "0.0.0.0"},
        )
        uvicorn.run(
            self.server.get_app(), host="0.0.0.0", port=8000
        )  # TODO: Add config
        self.logger.info("uvicorn stopped")

    def get_server(self) -> FastAPIServer:
        return self.server

    def get_logger(self) -> logging.Logger:
        return self.logger

    def get_config(self) -> AppConfig:
        return self.config
