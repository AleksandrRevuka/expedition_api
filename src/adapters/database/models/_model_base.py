from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, registry
from sqlalchemy.orm.decl_api import DeclarativeMeta

from src.adapters.database.models._model_utils.datetime import DateTimeUTC, get_utc_now

dt_tz_with_none = Annotated[datetime | None, mapped_column(DateTimeUTC())]
dt_tz = Annotated[datetime, mapped_column(DateTimeUTC())]

mapper_registry = registry()


class SqlAlchemyBase(metaclass=DeclarativeMeta):
    """
    Base class for SQLAlchemy models.
    Provides a method to convert a SQLAlchemy model to a Pydantic schema.
    """

    __abstract__ = True
    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor


class BaseWithTimestamps(SqlAlchemyBase):
    """
    Base class for models with automatic created_at and updated_at timestamps.
    """

    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now
    )
