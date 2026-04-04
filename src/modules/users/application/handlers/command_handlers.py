from src.modules.users.application.commands.commands import (
    CreateUserCommand,
    LoginUserCommand,
)
from src.modules.users.application.handlers.handlers_interface import (
    UsersCommandHandler,
)
from src.modules.users.application.use_cases.create_user import CreateUserUseCase
from src.modules.users.application.use_cases.login_user import LoginUserUseCase
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.infrastructure.password_service import PasswordService
from src.modules.users.infrastructure.token_service import TokenService
from src.modules.users.infrastructure.units_of_work import UsersStorageUnitOfWork


class CreateUserCommandHandler(UsersCommandHandler[CreateUserCommand]):
    def __init__(
        self, uow: UsersStorageUnitOfWork, password_service: PasswordService
    ) -> None:
        super().__init__(uow)
        self.password_service = password_service

    async def __call__(self, command: CreateUserCommand) -> UserAggregate:
        async with self.uow:
            use_case = CreateUserUseCase(
                users=self.uow.users,
                password_service=self.password_service,
            )
            result = await use_case(command)
            await self.uow.commit()
        return result


class LoginUserCommandHandler(UsersCommandHandler[LoginUserCommand]):
    def __init__(
        self,
        uow: UsersStorageUnitOfWork,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        super().__init__(uow)
        self.password_service = password_service
        self.token_service = token_service

    async def __call__(self, command: LoginUserCommand) -> str:
        async with self.uow:
            use_case = LoginUserUseCase(
                users=self.uow.users,
                password_service=self.password_service,
                token_service=self.token_service,
            )
            result = await use_case(command)
        return result
