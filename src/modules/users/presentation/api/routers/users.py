from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status

from src.common.container.main_container import Container
from src.common.role_routers import AuthenticatedAPIRouter
from src.common.security.auth_dependencies import get_current_user
from src.modules.users.application.use_cases.get_user import GetUserUseCase
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.domain.exceptions.exceptions import UserNotFoundError
from src.modules.users.presentation.api.schemas.responses import UserResponse

authenticated_router = AuthenticatedAPIRouter()


@authenticated_router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserAggregate = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.from_domain(current_user)


@authenticated_router.get("/{user_id}", response_model=UserResponse)
@inject
async def get_user(
    user_id: UUID,
    uow=Depends(Provide[Container.uows.users_storage_uow]),
) -> UserResponse:
    async with uow:
        use_case = GetUserUseCase(uow.users)
        try:
            user = await use_case(user_id)
        except UserNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UserResponse.from_domain(user)
