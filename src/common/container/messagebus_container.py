from dependency_injector import containers, providers

from src.adapters.handler_dispatcher.bootstrap import Bootstrap
from src.adapters.handler_dispatcher.messagebus import MessageBus
from src.modules.expeditions.application.commands.commands import (
    ChangeExpeditionStatusCommand,
    ConfirmMemberCommand,
    CreateExpeditionCommand,
    DeleteExpeditionCommand,
    InviteMemberCommand,
    UpdateExpeditionCommand,
    RemoveMemberCommand,
)
from src.modules.expeditions.application.handlers.command_handlers import (
    ChangeExpeditionStatusCommandHandler,
    ConfirmMemberCommandHandler,
    CreateExpeditionCommandHandler,
    DeleteExpeditionCommandHandler,
    InviteMemberCommandHandler,
    UpdateExpeditionCommandHandler,
    RemoveMemberCommandHandler,
)
from src.modules.expeditions.application.handlers.event_handlers import (
    ExpeditionStatusChangedEventHandler,
    MemberConfirmedEventHandler,
    MemberInvitedEventHandler,
    MemberRemovedEventHandler,
)
from src.modules.expeditions.domain.events import (
    ExpeditionStatusChangedEvent,
    MemberConfirmedEvent,
    MemberInvitedEvent,
    MemberRemovedEvent,
)
from src.modules.users.application.commands.commands import (
    CreateUserCommand,
    LoginUserCommand,
)
from src.modules.users.application.handlers.command_handlers import (
    CreateUserCommandHandler,
    LoginUserCommandHandler,
)


async def init_messagebus(bootstrap: Bootstrap) -> MessageBus:
    return await bootstrap.get_messagebus()


class MessagebusContainer(containers.DeclarativeContainer):
    uows = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    base_container = providers.DependenciesContainer()

    _expeditions_bootstrap = providers.Factory(
        Bootstrap,
        uow=uows.expeditions_storage_uow,
        commands_handlers_for_injection=providers.Dict(
            {
                CreateExpeditionCommand: CreateExpeditionCommandHandler,
                UpdateExpeditionCommand: UpdateExpeditionCommandHandler,
                DeleteExpeditionCommand: DeleteExpeditionCommandHandler,
                ChangeExpeditionStatusCommand: ChangeExpeditionStatusCommandHandler,
                InviteMemberCommand: InviteMemberCommandHandler,
                ConfirmMemberCommand: ConfirmMemberCommandHandler,
                RemoveMemberCommand: RemoveMemberCommandHandler,
            }
        ),
        events_handlers_for_injection=providers.Dict(
            {
                ExpeditionStatusChangedEvent: providers.List(
                    ExpeditionStatusChangedEventHandler
                ),
                MemberInvitedEvent: providers.List(MemberInvitedEventHandler),
                MemberConfirmedEvent: providers.List(MemberConfirmedEventHandler),
                MemberRemovedEvent: providers.List(MemberRemovedEventHandler),
            }
        ),
        dependencies=providers.Dict(
            {
                "ws_manager": base_container.ws_manager,
            }
        ),
    )
    expeditions = providers.Resource(init_messagebus, bootstrap=_expeditions_bootstrap)

    _users_bootstrap = providers.Factory(
        Bootstrap,
        uow=uows.users_storage_uow,
        commands_handlers_for_injection=providers.Dict(
            {
                CreateUserCommand: CreateUserCommandHandler,
                LoginUserCommand: LoginUserCommandHandler,
            }
        ),
        events_handlers_for_injection=providers.Dict({}),
        dependencies=providers.Dict(
            {
                "password_service": services.password_service,
                "token_service": services.token_service,
            }
        ),
    )
    users = providers.Resource(init_messagebus, bootstrap=_users_bootstrap)
