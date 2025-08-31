import logging

from grpc import aio

from common.infrastructure.config.grcp_config import GRPCConfig


class GRPCClient:
    def __init__(self, logger: logging.Logger, config: GRPCConfig):
        self._logger = logger
        self._config = config
        self._channel = aio.insecure_channel(config.address)

    def get_channel(self) -> aio.Channel:
        return self._channel

    async def close(self):
        self._logger.info(f"closing gRPC channel to {self._config.address}")
        await self._channel.close(self._config.grace)
