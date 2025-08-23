from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserDescriptor:
    user_id: UUID
    username: str
