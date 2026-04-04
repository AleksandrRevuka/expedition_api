import inspect
from types import MappingProxyType
from typing import Any

from src.adapters.handler_dispatcher.messagebus import MessageBus
from src.common.interfaces.commands import AbstractCommand
from src.common.interfaces.events import AbstractEvent
from src.common.interfaces.handlers import AbstractCommandHandler, AbstractEventHandler
from src.common.protocols.unitofwork import AsyncBaseUnitOfWork


class Bootstrap:
    """
    Bootstrap class for Dependencies Injection purposes.
    """

    def __init__(
        self,
        uow: AsyncBaseUnitOfWork,
        events_handlers_for_injection: dict[
            type[AbstractEvent], list[type[AbstractEventHandler[AbstractEvent]]]
        ],
        commands_handlers_for_injection: dict[
            type[AbstractCommand], type[AbstractCommandHandler[AbstractCommand]]
        ],
        dependencies: dict[str, Any] | None = None,
    ) -> None:
        self._uow: AsyncBaseUnitOfWork = uow
        self._dependencies: dict[str, Any] = {"uow": self._uow}
        self._events_handlers_for_injection: dict[
            type[AbstractEvent], list[type[AbstractEventHandler[AbstractEvent]]]
        ] = events_handlers_for_injection
        self._commands_handlers_for_injection: dict[
            type[AbstractCommand], type[AbstractCommandHandler[AbstractCommand]]
        ] = commands_handlers_for_injection

        if dependencies:
            self._dependencies.update(dependencies)

    async def get_messagebus(self) -> MessageBus:
        """
        Makes necessary injections to commands handlers and events handlers for creating appropriate messagebus,
        after which returns messagebus instance.
        """

        injected_event_handlers: dict[type[AbstractEvent], Any] = {
            event_type: [
                await self._inject_dependencies(handler=handler)
                for handler in event_handlers
            ]
            for event_type, event_handlers in self._events_handlers_for_injection.items()
        }

        injected_command_handlers: dict[type[AbstractCommand], Any] = {
            command_type: await self._inject_dependencies(handler=handler)
            for command_type, handler in self._commands_handlers_for_injection.items()
        }

        return MessageBus(
            uow=self._uow,
            event_handlers=injected_event_handlers,
            command_handlers=injected_command_handlers,
        )

    async def _inject_dependencies(
        self,
        handler: type[AbstractEventHandler[AbstractEvent]]
        | type[AbstractCommandHandler[AbstractCommand]],
    ) -> AbstractEventHandler[AbstractEvent] | AbstractCommandHandler[AbstractCommand]:
        """
        Inspecting handler to know its signature and init params, after which only necessary dependencies will be
        injected to the handler.
        """

        params: MappingProxyType[str, inspect.Parameter] = inspect.signature(
            handler
        ).parameters
        handler_dependencies: dict[str, Any] = {
            name: dependency
            for name, dependency in self._dependencies.items()
            if name in params
        }

        return handler(**handler_dependencies)
