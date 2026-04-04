from datetime import datetime
from uuid import UUID

from src.common.interfaces.commands import AbstractCommand
from src.conf.enums import ExpeditionStatus


class CreateExpeditionCommand(AbstractCommand):
    title: str
    description: str
    chief_id: UUID
    start_at: datetime
    capacity: int


class UpdateExpeditionCommand(AbstractCommand):
    expedition_id: UUID
    chief_id: UUID
    title: str | None = None
    description: str | None = None


class DeleteExpeditionCommand(AbstractCommand):
    expedition_id: UUID
    chief_id: UUID


class RemoveMemberCommand(AbstractCommand):
    expedition_id: UUID
    user_id: UUID
    chief_id: UUID


class ChangeExpeditionStatusCommand(AbstractCommand):
    expedition_id: UUID
    chief_id: UUID
    new_status: ExpeditionStatus


class InviteMemberCommand(AbstractCommand):
    expedition_id: UUID
    user_id: UUID
    chief_id: UUID


class ConfirmMemberCommand(AbstractCommand):
    expedition_id: UUID
    user_id: UUID
