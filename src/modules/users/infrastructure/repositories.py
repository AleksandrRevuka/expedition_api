from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.repository import AsyncRepository
from src.modules.users.domain.aggregates.user import UserAggregate


class UsersRepository(AsyncRepository[UserAggregate]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserAggregate, session)
