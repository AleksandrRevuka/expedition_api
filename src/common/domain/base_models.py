from dataclasses import dataclass

from src.common.interfaces.events import AbstractEvent


class AggregateRoot:
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
class BaseDomainModel(AggregateRoot):
    """Base class for all domain aggregates and entities."""

    def __post_init__(self) -> None:
        super().__init__()
        # Lazily init SA state for imperatively-mapped Pydantic dataclasses
        try:
            from sqlalchemy.orm.instrumentation import manager_of_class

            mgr = manager_of_class(type(self))
            if mgr is not None:
                mgr._new_state_if_none(self)
        except Exception:
            pass
