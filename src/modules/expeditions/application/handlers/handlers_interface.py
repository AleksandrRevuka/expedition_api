from src.common.interfaces.commands import AbstractCommand
from src.common.interfaces.events import AbstractEvent
from src.common.interfaces.handlers import AbstractCommandHandler, AbstractEventHandler
from src.modules.expeditions.infrastructure.units_of_work import (
    ExpeditionsStorageUnitOfWork,
)


class ExpeditionsCommandHandler[TC: AbstractCommand](AbstractCommandHandler[TC]):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        self.uow = uow


class ExpeditionsEventHandler[TE: AbstractEvent](AbstractEventHandler[TE]):
    def __init__(self) -> None:
        pass
