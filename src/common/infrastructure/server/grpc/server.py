import logging

from grpc import aio

from common.infrastructure.config.grcp_config import GRPCConfig


class GRPCServer:
    def __init__(self, logger: logging.Logger, config: GRPCConfig):
        self._logger = logger
        self._config = config
        self._server = aio.server()

    def get_server(self) -> aio.Server:
        return self._server

    async def start(self):
        self._server.add_insecure_port(self._config.address)
        self._logger.info(f"starting gRPC server at {self._config.address}")
        await self._server.start()

    async def stop(self):
        self._logger.info(f"stopping gRPC server at {self._config.address}")
        await self._server.stop(self._config.grace)
