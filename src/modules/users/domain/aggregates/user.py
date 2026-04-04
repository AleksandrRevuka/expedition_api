import uuid
from dataclasses import dataclass, field

from src.common.domain.base_models import AggregateRoot, BaseWithTimestamps
from src.conf.enums import Role


@dataclass(kw_only=True)
class UserAggregate(BaseWithTimestamps, AggregateRoot):
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str
    hashed_password: str
    name: str
    role: Role

    def is_chief(self) -> bool:
        return self.role == Role.chief

    def is_member(self) -> bool:
        return self.role == Role.member
