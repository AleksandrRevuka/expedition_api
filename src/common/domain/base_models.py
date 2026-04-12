from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from src.adapters.database.models._model_utils.datetime import get_utc_now
from src.common.interfaces.events import AbstractEvent


class BaseAggregateRoot:
    def __init__(self) -> None:
        self._events: list[AbstractEvent] = []

    @property
    def events(self) -> list[AbstractEvent]:
        if not hasattr(self, "_events"):
            self._events = []
        return self._events

    def add_event(self, event: AbstractEvent) -> None:
        if not hasattr(self, "_events"):
            self._events = []
        self._events.append(event)

    def pull_events(self) -> list[AbstractEvent]:
        if not hasattr(self, "_events"):
            self._events = []
        events = self._events[:]
        self._events.clear()
        return events


@dataclass
class AggregateRoot(BaseAggregateRoot):
    def to_dict(
        self, exclude: set[str] | None = None, include: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        data: dict[str, Any] = asdict(self)  # type: ignore[arg-type]
        if exclude:
            for key in exclude:
                try:
                    del data[key]
                except KeyError:
                    pass

        if include:
            data.update(include)

        return data


@dataclass
class BaseWithTimestamps:
    created_at: datetime = field(default_factory=get_utc_now)
    updated_at: datetime = field(default_factory=get_utc_now)
