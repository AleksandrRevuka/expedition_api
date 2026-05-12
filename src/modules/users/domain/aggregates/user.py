import uuid
from dataclasses import dataclass, field

from src.common.domain.base_models import AggregateRoot, BaseWithTimestamps
from src.conf.enums import Role
from src.modules.users.domain.events import UserChangedRoleEvent, UserRegisteredEvent


@dataclass(kw_only=True)
class UserAggregate(BaseWithTimestamps, AggregateRoot):
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str
    hashed_password: str
    name: str
    role: Role

    @classmethod
    def create(cls, email: str, hashed_password: str, name: str, role: Role) -> "UserAggregate":
        user = cls(email=email, hashed_password=hashed_password, name=name, role=role)
        user.add_event(UserRegisteredEvent(
            user_id=user.id,
            email=user.email,
            name=user.name,
        ))
        user.add_event(UserChangedRoleEvent(user_id=user.id, role=Role.chief))
        return user

    def is_chief(self) -> bool:
        return self.role == Role.chief

    def is_member(self) -> bool:
        return self.role == Role.member

    def change_role(self, role: Role) -> None:
        self.role = role

