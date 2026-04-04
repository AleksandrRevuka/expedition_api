from uuid import UUID

from src.common.schemas.responses import BaseResponseModel
from src.conf.enums import Role
from src.modules.users.domain.aggregates.user import UserAggregate


class UserResponse(BaseResponseModel):
    id: UUID
    email: str
    name: str
    role: Role

    @classmethod
    def from_domain(cls, user: UserAggregate) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
        )
