from abc import ABC, abstractmethod

from photos.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)


class IGetPresignedUrlUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetPresignedUrlQuery) -> str: ...
