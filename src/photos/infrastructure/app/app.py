from typing import ClassVar

from common.infrastructure.app.http_app import IHTTPApp
from common.infrastructure.server.fastapi.server import FastAPIServer
from photos.application.interfaces.usecases.command.upload_photo_use_case import (
    IUploadPhotoUseCase,
)
from photos.application.interfaces.usecases.query.get_presigned_url_use_case import (
    IGetPresignedUrlUseCase,
)
from photos.infrastructure.di.container.container import PhotoContainer
from photos.presentation.http.fastapi.controllers import (
    command_router,
    query_router,
)


class PhotosApp(IHTTPApp):
    prefix = "/photos"
    tags: ClassVar = ["Photos"]

    def __init__(
        self,
        container: PhotoContainer,
        server: FastAPIServer,
    ) -> None:
        self.container = container
        self.server = server

    def configure_dependencies(self) -> None:
        self.server.override_dependency(
            IUploadPhotoUseCase, self.container.upload_photo_use_case()
        )
        self.server.override_dependency(
            IGetPresignedUrlUseCase,
            self.container.get_presigned_url_use_case(),
        )

    def register_routers(self) -> None:
        self.server.register_router(query_router, self.prefix, self.tags)
        self.server.register_router(command_router, self.prefix, self.tags)
