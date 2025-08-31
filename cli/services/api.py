from datetime import timedelta

from auth.infrastructure.app.app import AuthApp, TokenApp
from auth.infrastructure.di.container.container import (
    AuthContainer,
    GRPCTokenContainer,
)
from auth.presentation.grpc.generated import auth_pb2_grpc
from common.infrastructure.app.app import App
from common.infrastructure.config.config import AppConfig
from common.infrastructure.database.redis.redis import RedisDatabase
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.di.container.container import CommonContainer
from common.infrastructure.logger.logging.logger_factory import LoggerFactory
from common.infrastructure.logger.logging.utils import log_config
from common.infrastructure.server.fastapi.server import FastAPIServer
from common.infrastructure.server.grpc.client import GRPCClient
from common.infrastructure.storage.minio.storage import MinioStorage
from identity.infrastructure.di.container.container import IdentityContainer
from photos.infrastructure.app.app import PhotosApp
from photos.infrastructure.di.container.container import PhotoContainer


def main():
    config = AppConfig.load()

    logger = LoggerFactory.create(None, config)
    logger.info("logger initialized")

    log_config(logger, config)

    # Database
    logger.info("initializing database...")
    database = Database.create(config.db, logger)
    logger.info("database initialized")

    # MinIO
    logger.info("initializing MinIO storage...")
    storage = MinioStorage.create(config.s3)
    logger.info("MinIO storage initialized")

    # Database
    logger.info("initializing Redis...")
    redis = RedisDatabase.create(config.redis, logger)
    logger.info("redis initialized")

    # gRPC Client
    logger.info("initializing gRPC client...")
    client = GRPCClient(logger, config.grpc)
    logger.info("gRPC client initialized")

    # Server
    logger.info("setting up FastAPI server...")
    server = FastAPIServer(logger)
    server.on_start_up(storage.ensure_bucket)
    server.on_tear_down(database.shutdown)
    server.on_tear_down(storage.shutdown)
    server.on_tear_down(redis.shutdown)
    server.on_tear_down(client.close)
    logger.info("FastAPI server setup complete")

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

    stub = auth_pb2_grpc.AuthServiceStub(client.get_channel())
    token_container = GRPCTokenContainer(
        stub=stub,
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

    auth_container = AuthContainer(
        uuid_generator=uuid_generator,
        user_factory=identity_container.user_factory,
        user_repository=user_repository,
        token_issuer=token_container.token_issuer,
        token_revoker=token_container.token_revoker,
        token_refresher=token_container.token_refresher,
    )

    photo_container = PhotoContainer(
        presigned_url_expiration_delta=timedelta(minutes=15),
        allowed_extensions=["jpg", "jpeg", "png", "gif"],
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        minio_storage=storage,
    )

    logger.info("building application...")

    app = App(config, logger, server)
    app.add_app(
        TokenApp(token_container, server),
        AuthApp(auth_container, identity_container, server),
        PhotosApp(photo_container, server),
    )
    app.configure()

    logger.info("application initialized")

    return app


if __name__ == "__main__":
    service = main()
    logger = service.get_logger()
    logger.info("service is starting")
    service.run()
    logger.info("service stopped")
else:
    service = main()
    logger = service.get_logger()
    logger.info("service is starting with ASGI web server")

    app = service.get_server().get_app()
