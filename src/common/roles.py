from fastapi import Depends, HTTPException, Request

from src.common.security.auth_dependencies import get_current_user
from src.conf.enums import Role
from src.conf.logging_config import LOGGER


class RolesAccess:
    def __init__(self, allowed_roles: list[Role]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        current_user=Depends(get_current_user),
    ) -> None:
        if current_user.role not in self.allowed_roles:
            LOGGER.error("Access denied")
            raise HTTPException(status_code=403, detail="Permission denied")


access_chief = RolesAccess([Role.chief])
access_member = RolesAccess([Role.member])
access_any = RolesAccess([Role.chief, Role.member])
