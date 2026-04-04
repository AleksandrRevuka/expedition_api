from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.adapters.repositories.async_unit_of_work import AsyncSqlAlchemyUnitOfWork
from src.modules.expeditions.infrastructure.repositories import (
    ExpeditionsRepository,
    MembersRepository,
)


class ExpeditionsStorageUnitOfWork(AsyncSqlAlchemyUnitOfWork):
    expeditions: ExpeditionsRepository
    members: MembersRepository

    def __init__(self, session_factory: async_scoped_session[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self.expeditions = ExpeditionsRepository(self.session)
        self.members = MembersRepository(self.session)
        return self
