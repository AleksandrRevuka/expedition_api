from collections.abc import Generator
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.common.domain.base_models import AggregateRoot
from src.common.interfaces.events import AbstractEvent
from src.common.protocols.unitofwork import AsyncBaseUnitOfWork
from src.conf.logging_config import LOGGER


class AsyncSqlAlchemyUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, session_factory: async_scoped_session[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._events: list[AbstractEvent] = []

    @property
    def session(self) -> AsyncSession:
        assert self._session is not None
        return self._session

    async def __aenter__(self) -> Self:
        """
        Entering the SqlAlchemyUnitOfWork.
        """
        self._session = self._session_factory()
        LOGGER.debug(f"Open session UOW: {id(self._session)}", "started")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exiting the SqlAlchemyUnitOfWork.
        """
        if exc_type:
            LOGGER.debug(f"Exception: {True}", "error")
            await self.rollback()
        LOGGER.debug(f"Close session UOW: {id(self._session)}", "stopped")

        await self.session.close()

    async def commit(self) -> None:
        """
        Commit the current transaction.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Rollback the current transaction.
        Uses self.session.expunge_all() to avoid sqlalchemy.orm.exc.DetachedInstanceError after session rollback.
        """
        self.session.expunge_all()
        await self.session.rollback()

    async def add_event(self, event: AbstractEvent) -> None:
        self._events.append(event)

    async def collect_events(self, domain: AggregateRoot) -> None:
        self._events.extend(domain.pull_events())

    def get_events(self) -> Generator[AbstractEvent, None, None]:
        """
        Using generator to get elements only when they needed.
        Also can not use self._events directly, not to run events endlessly.
        """

        while self._events:
            yield self._events.pop(0)
