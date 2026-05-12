from uuid import UUID

from src.common.interfaces.events import AbstractEvent
from src.conf.enums import Role


class UserRegisteredEvent(AbstractEvent):
    user_id: UUID
    email: str
    name: str


class UserChangedRoleEvent(AbstractEvent):
    user_id: UUID
    role: Role