from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends

from src.adapters.handler_dispatcher.messagebus import MessageBus
from src.common.container.main_container import Container

MessagebusUsersDep = Annotated[MessageBus, Depends(Provide[Container.messagebus.users])]
