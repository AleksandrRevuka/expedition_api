from typing import Any

from fastapi import APIRouter, Depends

from src.common.roles import access_any, access_chief, access_member


class ChiefAPIRouter(APIRouter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, dependencies=[Depends(access_chief)], **kwargs)


class MemberAPIRouter(APIRouter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, dependencies=[Depends(access_member)], **kwargs)


class AuthenticatedAPIRouter(APIRouter):
    """Accessible by both chiefs and members (any authenticated user)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, dependencies=[Depends(access_any)], **kwargs)
