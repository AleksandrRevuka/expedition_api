from datetime import UTC, datetime

from sqlalchemy import DateTime, Dialect, TypeDecorator


def get_utc_now() -> datetime:
    """
    Returns the current time in UTC.
    """
    return datetime.now(UTC)


class DateTimeUTC(TypeDecorator[datetime]):
    """
    Custom type for storing UTC datetime in SQLite,
    to avoid losing timezone.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            return value.astimezone(UTC)
        return None

    def process_result_value(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is not None:
            return value.replace(tzinfo=UTC)
        return None
