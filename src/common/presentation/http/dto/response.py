from typing import Self
from uuid import UUID

from pydantic import BaseModel


class EmptyResponse(BaseModel): ...


class IDResponse(BaseModel):
    id: UUID

    @classmethod
    def from_uuid(cls, id: UUID) -> Self:
        return cls(id=id)
