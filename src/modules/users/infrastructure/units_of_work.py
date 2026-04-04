from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.adapters.repositories.async_unit_of_work import AsyncSqlAlchemyUnitOfWork
from src.modules.users.infrastructure.repositories import UsersRepository


class UsersStorageUnitOfWork(AsyncSqlAlchemyUnitOfWork):
    users: UsersRepository

    def __init__(self, session_factory: async_scoped_session[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self.users = UsersRepository(self.session)
        return self
