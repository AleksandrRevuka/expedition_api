from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends

from src.adapters.handler_dispatcher.messagebus import MessageBus
from src.common.container.main_container import Container

MessagebusExpeditionsDep = Annotated[
    MessageBus, Depends(Provide[Container.messagebus.expeditions])
]
