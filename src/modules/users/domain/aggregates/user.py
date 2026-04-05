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

    @classmethod
    def create(cls, email: str, hashed_password: str, name: str, role: Role) -> "UserAggregate":
        return cls(email=email, hashed_password=hashed_password, name=name, role=role)

    def is_chief(self) -> bool:
        return self.role == Role.chief

    def is_member(self) -> bool:
        return self.role == Role.member
