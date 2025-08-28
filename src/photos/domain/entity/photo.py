from dataclasses import dataclass
from typing import Self
from uuid import UUID


@dataclass
class Photo:
    photo_id: UUID
    user_id: UUID
    name: str
    mime: str

    @classmethod
    def create(
        cls, photo_id: UUID, user_id: UUID, extension: str, mime: str
    ) -> Self:
        return cls(
            photo_id=photo_id,
            user_id=user_id,
            name=f"{photo_id}.{extension}",
            mime=mime,
        )
