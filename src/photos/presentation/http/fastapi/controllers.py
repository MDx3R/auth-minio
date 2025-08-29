from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi_utils.cbv import cbv

from auth.presentation.http.fastapi.auth import (
    get_descriptor,
    require_authenticated,
)
from common.presentation.http.dto.response import StringResponse
from identity.domain.value_objects.descriptor import UserDescriptor
from photos.application.dtos.command.upload_photo_command import (
    UploadPhotoCommand,
)
from photos.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from photos.application.exceptions import InvalidFileTypeError
from photos.application.interfaces.usecases.command.upload_photo_use_case import (
    IUploadPhotoUseCase,
)
from photos.application.interfaces.usecases.query.get_presigned_url_use_case import (
    IGetPresignedUrlUseCase,
)


command_router = APIRouter()


@cbv(command_router)
class PhotoCommandController:
    upload_photo_use_case: IUploadPhotoUseCase = Depends()

    @command_router.post(
        "/upload",
        response_model=StringResponse,
        dependencies=[Depends(require_authenticated)],
    )
    async def upload(
        self,
        file: UploadFile,
        user: Annotated[UserDescriptor, Depends(get_descriptor)],
    ):
        try:
            result = await self.upload_photo_use_case.execute(
                UploadPhotoCommand(file.file), user
            )
            return StringResponse.from_str(result)
        except InvalidFileTypeError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": type(exc).__name__, "detail": str(exc)},
            )


query_router = APIRouter()


@cbv(query_router)
class PhotoQueryController:
    get_presigned_url_use_case: IGetPresignedUrlUseCase = Depends()

    @query_router.get("/presigned-url", response_model=StringResponse)
    async def get_presigned_url(
        self, name: str = Query(..., description="Photo name / object key")
    ):
        url = await self.get_presigned_url_use_case.execute(
            GetPresignedUrlQuery(name=name)
        )
        return StringResponse.from_str(url)
