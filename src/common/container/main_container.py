from dependency_injector import containers, providers

from src.common.container.base_container import BaseContainer
from src.common.container.messagebus_container import MessagebusContainer
from src.common.container.services_container import ServicesContainer
from src.common.container.uow_container import UowContainer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.modules.auth.presentation.api.routers",
            "src.modules.expeditions.presentation.api.routers",
            "src.modules.users.presentation.api.routers",
            "src.modules.websocket.presentation.api.routers",
        ],
        modules=[
            "src.common.security.auth_dependencies",
            "src.modules.websocket.presentation.dependencies",
        ],
    )

    core = providers.Container(BaseContainer)

    uows = providers.Container(UowContainer, base_container=core)

    services = providers.Container(ServicesContainer, uows=uows)

    messagebus = providers.Container(
        MessagebusContainer,
        uows=uows,
        services=services,
        base_container=core,
    )
