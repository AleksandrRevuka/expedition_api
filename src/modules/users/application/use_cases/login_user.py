from src.modules.users.application.commands.commands import LoginUserCommand
from src.modules.users.domain.exceptions.exceptions import InvalidCredentialsError
from src.modules.users.infrastructure.password_service import PasswordService
from src.modules.users.infrastructure.repositories import UsersRepository
from src.modules.users.infrastructure.token_service import TokenService


class LoginUserUseCase:
    def __init__(
        self,
        users: UsersRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._users = users
        self._password_service = password_service
        self._token_service = token_service

    async def __call__(self, command: LoginUserCommand) -> str:
        user = await self._users.get_one(email=command.email)
        if user is None or not self._password_service.verify(
            command.password, user.hashed_password
        ):
            raise InvalidCredentialsError("Invalid credentials")
        return self._token_service.create_access_token(user.email)
