from datetime import datetime
from uuid import UUID

from src.common.interfaces.body import AbstractBody
from src.conf.enums import ExpeditionStatus


class CreateExpeditionBody(AbstractBody):
    title: str
    description: str = ""
    start_at: datetime
    capacity: int


class UpdateExpeditionBody(AbstractBody):
    title: str | None = None
    description: str | None = None


class ChangeStatusBody(AbstractBody):
    status: ExpeditionStatus


class InviteMemberBody(AbstractBody):
    user_id: UUID


class ConfirmMemberBody(AbstractBody):
    pass
