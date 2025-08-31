import logging
from typing import Any

from grpc import aio

from common.infrastructure.config.grcp_config import GRPCConfig


class GRPCClient:
    def __init__(self, logger: logging.Logger, config: GRPCConfig):
        self._logger = logger
        self._config = config
        self._channel: aio.Channel | None = None

    async def connect(self) -> None:
        if self._channel is None:
            self._logger.info(
                f"opening gRPC channel to {self._config.address}"
            )
            self._channel = aio.insecure_channel(self._config.address)

    def get_channel(self) -> aio.Channel:
        if self._channel is None:
            raise RuntimeError(
                "GRPCClient is not connected. Call connect() first."
            )
        return self._channel

    async def close(self) -> None:
        if self._channel is not None:
            self._logger.info(
                f"closing gRPC channel to {self._config.address}"
            )
            await self._channel.close(self._config.grace)
            self._channel = None


class LazyStub:
    def __init__(self, client: GRPCClient, stub_cls: Any):
        self._client = client
        self._stub_cls = stub_cls
        self._stub = None

    def _ensure_stub(self):
        if self._stub is None:
            channel = self._client.get_channel()
            self._stub = self._stub_cls(channel)
        return self._stub

    def __getattr__(self, item: str):
        return getattr(self._ensure_stub(), item)
