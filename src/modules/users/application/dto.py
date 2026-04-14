from pydantic import BaseModel

from src.conf.enums import Role
from src.modules.users.domain.aggregates.user import UserAggregate


class UserDTO(BaseModel):
    id: str
    email: str
    name: str
    role: Role

    @classmethod
    def from_aggregate(cls, user: UserAggregate) -> "UserDTO":
        return cls(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
        )
