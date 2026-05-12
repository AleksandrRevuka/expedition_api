from src.conf.enums import Role
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.infrastructure.repositories import UsersRepository


class GetMembersUseCase:
    def __init__(self, users: UsersRepository):
        self._users = users

    async def __call__(self) -> list[UserAggregate]:
        users = await self._users.get_all(role=Role.member)
        return users