from queue import Queue
from typing import Any

from src.common.exceptions.other_errors import MessageBusMessageError
from src.common.interfaces.commands import AbstractCommand
from src.common.interfaces.events import AbstractEvent
from src.common.interfaces.handlers import AbstractCommandHandler, AbstractEventHandler
from src.common.protocols.unitofwork import AsyncBaseUnitOfWork
from src.conf.logging_config import LOGGER

Message = AbstractEvent | AbstractCommand


class MessageBus:
    def __init__(
        self,
        uow: AsyncBaseUnitOfWork,
        event_handlers: dict[
            type[AbstractEvent], list[AbstractEventHandler[AbstractEvent]]
        ],
        command_handlers: dict[
            type[AbstractCommand], AbstractCommandHandler[AbstractCommand]
        ],
    ) -> None:
        self._uow: AsyncBaseUnitOfWork = uow
        self._event_handlers: dict[
            type[AbstractEvent], list[AbstractEventHandler[AbstractEvent]]
        ] = event_handlers
        self._command_handlers: dict[
            type[AbstractCommand], AbstractCommandHandler[AbstractCommand]
        ] = command_handlers
        self._queue: Queue[Message] = Queue()

    async def handle(self, message: Message) -> Any:
        self._queue.put(message)
        command_result = None

        while not self._queue.empty():
            message = self._queue.get()

            if isinstance(message, AbstractEvent):
                await self._handle_event(event=message)
            elif isinstance(message, AbstractCommand):
                command_result = await self._handle_command(command=message)
            else:
                raise MessageBusMessageError

        return command_result

    async def _handle_event(self, event: AbstractEvent) -> None:
        for handler in self._event_handlers.get(type(event), []):
            LOGGER.debug(f"Handler: {handler}")

            await handler(event)

            for event in self._uow.get_events():
                self._queue.put_nowait(event)

    async def _handle_command(self, command: AbstractCommand) -> Any:
        handler = self._command_handlers[type(command)]
        LOGGER.debug(f"Hendler: {handler}")
        command_result = await handler(command)

        for event in self._uow.get_events():
            self._queue.put_nowait(event)

        return command_result
