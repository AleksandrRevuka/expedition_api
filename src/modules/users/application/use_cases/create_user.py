from src.modules.users.application.commands.commands import CreateUserCommand
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.domain.exceptions.exceptions import UserAlreadyExistsError
from src.modules.users.infrastructure.password_service import PasswordService
from src.modules.users.infrastructure.repositories import UsersRepository


class CreateUserUseCase:
    def __init__(
        self, users: UsersRepository, password_service: PasswordService
    ) -> None:
        self._users = users
        self._password_service = password_service

    async def __call__(self, command: CreateUserCommand) -> UserAggregate:
        existing = await self._users.get_one(email=command.email)
        if existing is not None:
            raise UserAlreadyExistsError(
                f"User with email {command.email!r} already exists"
            )
        hashed = self._password_service.hash(command.password)
        user = UserAggregate(
            email=command.email,
            hashed_password=hashed,
            name=f"{command.first_name} {command.last_name}",
            role=command.role,
        )
        return await self._users.add_one(user)
