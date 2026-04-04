from __future__ import annotations
from src.conf.enums import Role
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Table, Enum, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.database.models._model_base import BaseWithTimestamps

if TYPE_CHECKING:
    from src.modules.expeditions.infrastructure.db.models import (
        Expedition,
        ExpeditionMember,
    )


class User(BaseWithTimestamps):
    __tablename__ = "users"
    __table__: Table

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[Role] = mapped_column(Enum(Role))

    expeditions_as_chief: Mapped[list[Expedition]] = relationship(
        back_populates="chief"
    )
    expedition_memberships: Mapped[list[ExpeditionMember]] = relationship(
        back_populates="user"
    )
