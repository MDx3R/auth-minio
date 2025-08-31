import asyncio
import logging
import signal

from auth.infrastructure.app.app import TokenGRPCApp
from auth.infrastructure.di.container.container import (
    TokenContainer,
)
from common.infrastructure.config.config import AppConfig
from common.infrastructure.database.redis.redis import RedisDatabase
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.di.container.container import CommonContainer
from common.infrastructure.logger.logging.logger_factory import LoggerFactory
from common.infrastructure.logger.logging.utils import log_config
from common.infrastructure.server.grpc.server import GRPCServer
from identity.infrastructure.di.container.container import IdentityContainer


def create_grpc_app():
    config = AppConfig.load()

    logger = LoggerFactory.create(None, config)
    logger.info("logger initialized")

    log_config(logger, config)

    # Database
    logger.info("initializing database...")
    database = Database.create(config.db)
    logger.info("database initialized")

    # Database
    logger.info("initializing Redis...")
    redis = RedisDatabase.create(config.redis)
    logger.info("redis initialized")

    # Server
    logger.info("setting up gRPC server...")
    server = GRPCServer(logger, config.grpc)
    logger.info("gRPC server setup complete")

    common_container = CommonContainer(config=config, database=database)
    uuid_generator = common_container.uuid_generator
    query_executor = common_container.query_executor
    clock = common_container.clock

    identity_container = IdentityContainer(
        ttl=300,
        namespace="user",
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        redis=redis,
    )
    user_repository = identity_container.user_repository

    token_container = TokenContainer(
        ttl=300,
        namespace="user",
        auth_config=config.auth,
        clock=clock,
        uuid_generator=uuid_generator,
        token_generator=common_container.token_generator,
        query_executor=query_executor,
        redis=redis,
        user_repository=user_repository,
    )

    logger.info("building application...")
    app = TokenGRPCApp(token_container, server, logger)
    app.configure()
    logger.info("application initialized")

    return app


async def serve(server: GRPCServer, logger: logging.Logger):
    logger.info("auth gRPC service is starting")
    await server.get_server().start()
    logger.info("auth gRPC service is running")

    stop_event = asyncio.Event()

    def shutdown():
        logger.info("received stop signal, shutting down...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, shutdown)
    loop.add_signal_handler(signal.SIGINT, shutdown)

    await stop_event.wait()

    await server.stop()
    logger.info("gRPC server stopped gracefully.")


if __name__ == "__main__":
    app = create_grpc_app()
    asyncio.run(serve(app.get_server(), app.get_logger()))
