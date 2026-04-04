from src.common.interfaces.commands import AbstractCommand
from src.common.interfaces.handlers import AbstractCommandHandler
from src.modules.users.infrastructure.units_of_work import UsersStorageUnitOfWork


class UsersCommandHandler[TC: AbstractCommand](AbstractCommandHandler[TC]):
    def __init__(self, uow: UsersStorageUnitOfWork) -> None:
        self.uow = uow
