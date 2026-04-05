from src.conf.app_config import get_app_config
from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.modules.auth.presentation.api.schemas.schemas import TokenResponse
from src.modules.users.application.commands.commands import (
    CreateUserCommand,
    LoginUserCommand,
)
from src.modules.users.presentation.api.schemas.responses import UserResponse
from src.modules.users.presentation.dependencies import MessagebusUsersDep

public_router = APIRouter()


@public_router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def register(
    body: CreateUserCommand,
    bus: MessagebusUsersDep,
) -> UserResponse:

    user = await bus.handle(body)

    return UserResponse.from_domain(user)


@public_router.post("/login", response_model=TokenResponse)
@inject
async def login(
    bus: MessagebusUsersDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    command = LoginUserCommand(email=form_data.username, password=form_data.password)
    token = await bus.handle(command)

    conf = get_app_config()
    if conf.ENVIRONMENT == "dev":
        print(token)  #TODO remove

    return TokenResponse(access_token=token)
