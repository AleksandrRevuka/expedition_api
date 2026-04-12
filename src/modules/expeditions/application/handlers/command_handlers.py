from src.modules.expeditions.application.commands.commands import (
    ChangeExpeditionStatusCommand,
    ConfirmMemberCommand,
    CreateExpeditionCommand,
    DeleteExpeditionCommand,
    InviteMemberCommand,
    RemoveMemberCommand,
    UpdateExpeditionCommand,
)
from src.modules.expeditions.application.handlers.handlers_interface import (
    ExpeditionsCommandHandler,
)
from src.modules.expeditions.application.use_cases.change_status import (
    ChangeExpeditionStatusUseCase,
)
from src.modules.expeditions.application.use_cases.confirm_member import (
    ConfirmMemberUseCase,
)
from src.modules.expeditions.application.use_cases.create_expedition import (
    CreateExpeditionUseCase,
)
from src.modules.expeditions.application.use_cases.delete_expedition import (
    DeleteExpeditionUseCase,
)
from src.modules.expeditions.application.use_cases.invite_member import (
    InviteMemberUseCase,
)
from src.modules.expeditions.application.use_cases.remove_member import (
    RemoveMemberUseCase,
)
from src.modules.expeditions.application.use_cases.update_expedition import (
    UpdateExpeditionUseCase,
)
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.infrastructure.units_of_work import (
    ExpeditionsStorageUnitOfWork,
)


class CreateExpeditionCommandHandler(
    ExpeditionsCommandHandler[CreateExpeditionCommand]
):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        super().__init__(uow)

    async def __call__(self, command: CreateExpeditionCommand) -> ExpeditionAggregate:
        async with self.uow:
            use_case = CreateExpeditionUseCase(expeditions=self.uow.expeditions)
            result = await use_case(command)
            await self.uow.commit()
        await self.uow.collect_events(result)
        return result


class UpdateExpeditionCommandHandler(
    ExpeditionsCommandHandler[UpdateExpeditionCommand]
):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        super().__init__(uow)

    async def __call__(self, command: UpdateExpeditionCommand) -> ExpeditionAggregate:
        async with self.uow:
            use_case = UpdateExpeditionUseCase(expeditions=self.uow.expeditions)
            result = await use_case(command)
            await self.uow.commit()
        await self.uow.collect_events(result)
        return result


class DeleteExpeditionCommandHandler(
    ExpeditionsCommandHandler[DeleteExpeditionCommand]
):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        super().__init__(uow)

    async def __call__(self, command: DeleteExpeditionCommand) -> None:
        async with self.uow:
            use_case = DeleteExpeditionUseCase(expeditions=self.uow.expeditions)
            await use_case(command)
            await self.uow.commit()


class ChangeExpeditionStatusCommandHandler(
    ExpeditionsCommandHandler[ChangeExpeditionStatusCommand]
):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        super().__init__(uow)

    async def __call__(
        self, command: ChangeExpeditionStatusCommand
    ) -> ExpeditionAggregate:
        async with self.uow:
            use_case = ChangeExpeditionStatusUseCase(
                expeditions=self.uow.expeditions, members=self.uow.members
            )
            result = await use_case(command)
            await self.uow.commit()
        await self.uow.collect_events(result)
        return result


class RemoveMemberCommandHandler(ExpeditionsCommandHandler[RemoveMemberCommand]):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        super().__init__(uow)

    async def __call__(self, command: RemoveMemberCommand) -> ExpeditionAggregate:
        async with self.uow:
            use_case = RemoveMemberUseCase(
                expeditions=self.uow.expeditions,
                members=self.uow.members,
            )
            result = await use_case(command)
            await self.uow.commit()
        await self.uow.collect_events(result)
        return result


class InviteMemberCommandHandler(ExpeditionsCommandHandler[InviteMemberCommand]):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        super().__init__(uow)

    async def __call__(self, command: InviteMemberCommand) -> ExpeditionAggregate:
        async with self.uow:
            use_case = InviteMemberUseCase(
                expeditions=self.uow.expeditions,
                members=self.uow.members,
            )
            result = await use_case(command)
            await self.uow.commit()
        await self.uow.collect_events(result)
        return result


class ConfirmMemberCommandHandler(ExpeditionsCommandHandler[ConfirmMemberCommand]):
    def __init__(self, uow: ExpeditionsStorageUnitOfWork) -> None:
        super().__init__(uow)

    async def __call__(self, command: ConfirmMemberCommand) -> ExpeditionAggregate:
        async with self.uow:
            use_case = ConfirmMemberUseCase(
                expeditions=self.uow.expeditions,
                members=self.uow.members,
            )
            result = await use_case(command)
            await self.uow.commit()
        await self.uow.collect_events(result)
        return result
