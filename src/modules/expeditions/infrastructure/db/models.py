from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.database.models._model_base import (
    BaseWithTimestamps,
    SqlAlchemyBase,
    dt_tz,
    dt_tz_with_none,
)
from src.conf.enums import ExpeditionStatus, MemberState

if TYPE_CHECKING:
    from src.modules.users.infrastructure.db.models import User


class Expedition(BaseWithTimestamps):
    __tablename__ = "expeditions"
    __table__: Table

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True
    )
    chief_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ExpeditionStatus] = mapped_column(
        Enum(ExpeditionStatus), default=ExpeditionStatus.draft
    )
    start_at: Mapped[dt_tz]
    end_at: Mapped[dt_tz_with_none]
    capacity: Mapped[int] = mapped_column(Integer)

    members: Mapped[list[ExpeditionMember]] = relationship(
        back_populates="expedition", cascade="all, delete-orphan"
    )
    chief: Mapped[User] = relationship(back_populates="expeditions_as_chief")


class ExpeditionMember(SqlAlchemyBase):
    __tablename__ = "expedition_members"
    __table__: Table
    __table_args__ = (
        UniqueConstraint("expedition_id", "user_id", name="uq_expedition_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True
    )
    expedition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("expeditions.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    state: Mapped[MemberState] = mapped_column(
        Enum(MemberState), default=MemberState.invited
    )
    invited_at: Mapped[dt_tz]
    confirmed_at: Mapped[dt_tz_with_none]

    expedition: Mapped[Expedition] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="expedition_memberships")
