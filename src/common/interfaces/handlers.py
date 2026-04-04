from abc import ABC, abstractmethod
from typing import Any

from src.common.interfaces.commands import AbstractCommand
from src.common.interfaces.events import AbstractEvent
from src.common.protocols.unitofwork import AsyncBaseUnitOfWork


class AbstractHandler(ABC):
    @abstractmethod
    def __init__(self, uow: AsyncBaseUnitOfWork) -> None: ...

    def __repr__(self) -> str:
        if hasattr(self.__class__, "__orig_bases__"):
            for base in tuple(self.__class__.__orig_bases__):  # type: ignore
                if hasattr(base, "__args__"):
                    args = base.__args__
                    return f"{self.__class__.__name__}[{', '.join(arg.__name__ for arg in args)}]"

        return self.__class__.__name__


class AbstractEventHandler[TE: AbstractEvent](AbstractHandler, ABC):
    """
    Abstract event handler class, from which every event handler should be inherited from.
    """

    @abstractmethod
    async def __call__(self, event: TE) -> Any: ...


class AbstractCommandHandler[TC: AbstractCommand](AbstractHandler, ABC):
    """
    Abstract command handler class, from which every command handler should be inherited from.
    """

    @abstractmethod
    async def __call__(self, command: TC) -> Any: ...
