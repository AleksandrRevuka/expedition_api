from uuid import UUID

from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.domain.exceptions.exceptions import UserNotFoundError
from src.modules.users.infrastructure.repositories import UsersRepository


class GetUserUseCase:
    def __init__(self, users: UsersRepository) -> None:
        self._users = users

    async def __call__(self, user_id: UUID) -> UserAggregate:
        user = await self._users.get_one(id=user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
