from uuid import UUID

from src.common.interfaces.events import AbstractEvent
from src.conf.enums import ExpeditionStatus


class MemberInvitedEvent(AbstractEvent):
    expedition_id: UUID
    user_id: UUID


class MemberConfirmedEvent(AbstractEvent):
    expedition_id: UUID
    user_id: UUID


class ExpeditionStatusChangedEvent(AbstractEvent):
    expedition_id: UUID
    new_status: ExpeditionStatus
    chief_id: UUID


class MemberRemovedEvent(AbstractEvent):
    expedition_id: UUID
    user_id: UUID
