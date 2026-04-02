from collections.abc import Generator
from types import TracebackType
from typing import Protocol, Self

from src.common.interfaces.events import AbstractEvent


class AsyncBaseUnitOfWork(Protocol):
    _events: list[AbstractEvent]

    def __init__(self) -> None: ...

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def add_event(self, event: AbstractEvent) -> None: ...

    def get_events(self) -> Generator[AbstractEvent, None, None]: ...
