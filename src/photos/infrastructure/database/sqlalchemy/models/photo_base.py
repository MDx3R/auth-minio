from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from common.infrastructure.database.sqlalchemy.models.base import Base


class PhotoBase(Base):
    __tablename__ = "photos"

    photo_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    mime: Mapped[str] = mapped_column(String, nullable=False)
