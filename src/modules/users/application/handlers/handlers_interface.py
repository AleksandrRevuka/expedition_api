from src.common.interfaces.commands import AbstractCommand
from src.common.interfaces.events import AbstractEvent
from src.common.interfaces.handlers import AbstractCommandHandler, AbstractEventHandler
from src.modules.users.infrastructure.units_of_work import UsersStorageUnitOfWork


class UsersCommandHandler[TC: AbstractCommand](AbstractCommandHandler[TC]):
    def __init__(self, uow: UsersStorageUnitOfWork) -> None:
        self.uow = uow


class UsersEventHandler[TE: AbstractEvent](AbstractEventHandler[TE]):
    def __init__(self) -> None:
        pass
