from src.common.schemas.responses import BaseResponseModel
from src.conf.enums import Role
from src.modules.users.domain.aggregates.user import UserAggregate


class UserResponse(BaseResponseModel):
    id: str
    email: str
    name: str
    role: Role

    @classmethod
    def from_domain(cls, user: UserAggregate) -> "UserResponse":
        return cls(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
        )


class UserMembersResponse(BaseResponseModel):
    users: list[UserResponse]

    @classmethod
    def from_domain(cls, users: list[UserAggregate]) -> "UserMembersResponse":
        return cls(users=[UserResponse.from_domain(user) for user in users])