from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from common.infrastructure.database.sqlalchemy.models.base import Base


class UserBase(Base):
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
