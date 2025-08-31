import asyncio
import logging

from grpc import aio

from common.infrastructure.config.grcp_config import GRPCConfig


class GRPCServer:
    """Async gRPC server with graceful shutdown support. Should be created and started/stopped within one coroutine."""

    def __init__(self, logger: logging.Logger, config: GRPCConfig):
        self._logger = logger
        self._config = config
        self._server = aio.server()

    def get_server(self) -> aio.Server:
        return self._server

    async def start(self) -> None:
        self._logger.info("preparing gRPC server...")
        self._server.add_insecure_port(self._config.address)
        await self._server.start()
        self._logger.info(f"gRPC server started at {self._config.address}")

        try:
            await self._server.wait_for_termination()
        except asyncio.CancelledError:
            self._logger.debug("server wait cancelled")
        finally:
            pass

    async def stop(self) -> None:
        self._logger.info(f"stopping gRPC server at {self._config.address}")
        await self._server.stop(self._config.grace)
        self._logger.info("gRPC server stopped gracefully")
