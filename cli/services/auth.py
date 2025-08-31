import asyncio

from auth.infrastructure.app.app import TokenGRPCApp
from auth.infrastructure.di.container.container import TokenContainer
from common.infrastructure.config.config import AppConfig
from common.infrastructure.database.redis.redis import RedisDatabase
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.di.container.container import CommonContainer
from common.infrastructure.logger.logging.logger_factory import LoggerFactory
from common.infrastructure.logger.logging.utils import log_config
from common.infrastructure.server.grpc.server import GRPCServer
from identity.infrastructure.di.container.container import IdentityContainer


async def main():
    config = AppConfig.load()

    logger = LoggerFactory.create(None, config)
    logger.info("logger initialized")
    log_config(logger, config)

    # Database
    logger.info("initializing database...")
    database = Database.create(config.db, logger)
    logger.info("database initialized")

    # Redis
    logger.info("initializing Redis...")
    redis = RedisDatabase.create(config.redis, logger)
    logger.info("redis initialized")

    # Containers
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

    # Server
    server = GRPCServer(logger, config.grpc)
    app = TokenGRPCApp(token_container, server, logger)
    app.configure()

    try:
        await server.start()
    except Exception as e:
        logger.exception(f"fatal error: {e}")
        raise
    finally:
        # shutdown resources before loop closes
        logger.info("stopping all resources...")
        await database.shutdown()
        await redis.shutdown()
        await server.stop()
        logger.info("all resources stopped gracefully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
