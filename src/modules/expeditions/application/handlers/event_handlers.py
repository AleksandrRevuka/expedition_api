from src.modules.expeditions.application.handlers.handlers_interface import (
    ExpeditionsEventHandler,
)
from src.modules.expeditions.domain.events import (
    ExpeditionStatusChangedEvent,
    MemberConfirmedEvent,
    MemberInvitedEvent,
    MemberRemovedEvent,
)
from src.modules.websocket.manager import ExpeditionConnectionManager


class ExpeditionStatusChangedEventHandler(
    ExpeditionsEventHandler[ExpeditionStatusChangedEvent]
):
    def __init__(self, ws_manager: ExpeditionConnectionManager) -> None:
        super().__init__()
        self.ws_manager = ws_manager

    async def __call__(self, event: ExpeditionStatusChangedEvent) -> None:
        await self.ws_manager.broadcast_to_expedition(
            event.expedition_id,
            {
                "event": "expedition_status",
                "exebition_id": str(event.expedition_id),
                "status": event.new_status,
            },
        )


class MemberInvitedEventHandler(ExpeditionsEventHandler[MemberInvitedEvent]):
    def __init__(self, ws_manager: ExpeditionConnectionManager) -> None:
        super().__init__()
        self.ws_manager = ws_manager

    async def __call__(self, event: MemberInvitedEvent) -> None:
        await self.ws_manager.broadcast_to_expedition(
            event.expedition_id,
            {
                "event": "member_invited",
                "exebition_id": str(event.expedition_id),
                "user_id": str(event.user_id),
            },
        )


class MemberConfirmedEventHandler(ExpeditionsEventHandler[MemberConfirmedEvent]):
    def __init__(self, ws_manager: ExpeditionConnectionManager) -> None:
        super().__init__()
        self.ws_manager = ws_manager

    async def __call__(self, event: MemberConfirmedEvent) -> None:
        await self.ws_manager.broadcast_to_expedition(
            event.expedition_id,
            {
                "event": "member_confirmed",
                "exebition_id": str(event.expedition_id),
                "user_id": str(event.user_id),
            },
        )


class MemberRemovedEventHandler(ExpeditionsEventHandler[MemberRemovedEvent]):
    def __init__(self, ws_manager: ExpeditionConnectionManager) -> None:
        super().__init__()
        self.ws_manager = ws_manager

    async def __call__(self, event: MemberRemovedEvent) -> None:
        await self.ws_manager.broadcast_to_expedition(
            event.expedition_id,
            {
                "event": "member_removed",
                "expedition_id": str(event.expedition_id),
                "user_id": str(event.user_id),
            },
        )
