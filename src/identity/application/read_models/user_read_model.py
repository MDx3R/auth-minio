from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserReadModel:
    user_id: UUID
    username: str
