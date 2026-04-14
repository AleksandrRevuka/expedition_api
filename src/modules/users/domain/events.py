from src.conf.enums import Role
from uuid import UUID

from src.common.interfaces.events import AbstractEvent


class UserRegisteredEvent(AbstractEvent):
    user_id: UUID
    email: str
    name: str


class UserChangedRoleEvent(AbstractEvent):
    user_id: UUID
    role: Role