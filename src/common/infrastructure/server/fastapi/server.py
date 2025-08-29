import inspect
import logging
from abc import ABC
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, TypeVar

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


DEPENDENCY = TypeVar("DEPENDENCY", bound=ABC)


class FastAPIServer:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._startup_handlers: list[Callable[[], Awaitable[None]]] = []
        self._shutdown_handlers: list[Callable[[], Awaitable[None]]] = []
        self._app = FastAPI(lifespan=self._lifespan)

    def get_app(self) -> FastAPI:
        return self._app

    def on_start_up(self, func: Callable[..., Any], **kwargs: dict[str, Any]):
        self._startup_handlers.append(self._wrap(func, **kwargs))

    def on_tear_down(self, func: Callable[..., Any], **kwargs: dict[str, Any]):
        self._shutdown_handlers.append(self._wrap(func, **kwargs))

    def _wrap(
        self, func: Callable[..., Any], **kwargs: dict[str, Any]
    ) -> Callable[[], Awaitable[None]]:
        @wraps(func)
        async def wrapper():
            if inspect.iscoroutinefunction(func):
                await func(**kwargs)
            else:
                func(**kwargs)

        return wrapper

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        try:
            self.logger.info("Server startup begins")
            for handler in self._startup_handlers:
                await handler()
            yield
        finally:
            self.logger.info("Server shutdown begins")
            for handler in reversed(self._shutdown_handlers):
                try:
                    await handler()
                    self.logger.info(
                        f"Shutdown handler executed successfully: {handler.__name__}"
                    )
                except Exception as e:
                    self.logger.exception(
                        f"Error in shutdown handler {handler.__name__}: {e}"
                    )

    def use_middleware(
        self, middleware: type[BaseHTTPMiddleware], **options: Any
    ):
        self._app.add_middleware(middleware, **options)
        self.logger.info("Middleware %s added", middleware)

    def include_cors_middleware(self):
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # TODO: Add Config
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.logger.info("CORS middleware added with allow_origins=['*']")

    def register_router(self, router: APIRouter, prefix: str, tags: list[str]):
        self._app.include_router(
            router,
            prefix=prefix,
            tags=tags,  # pyright: ignore[reportArgumentType]
        )
        self.logger.info(f"Router registered: prefix={prefix}, tags={tags}")

    def override_dependency(
        self, interface: type[DEPENDENCY], dependency: DEPENDENCY
    ):
        self._app.dependency_overrides[interface] = lambda: dependency
        self.logger.debug(f"Dependency overridden: {interface.__name__}")
