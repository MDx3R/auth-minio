import logging
from abc import ABC, abstractmethod

from common.infrastructure.server.fastapi.server import FastAPIServer


class IApp(ABC):
    @abstractmethod
    def configure(self) -> None: ...


class App(IApp):
    def __init__(self, logger: logging.Logger, server: FastAPIServer) -> None:
        self.logger = logger
        self.server = server

    def configure(self) -> None:
        pass

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
