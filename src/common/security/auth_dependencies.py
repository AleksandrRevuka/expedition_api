from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.common.container.main_container import Container
from src.conf.logging_config import LOGGER
from src.conf.security_conf import get_jwt_config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@inject
async def get_current_user(
    uow=Depends(Provide[Container.uows.users_storage_uow]),  # type: ignore[assignment]
    token: str = Depends(oauth2_scheme),
):  # type: ignore[return]
    """
    Decode JWT, look up the user in DB, return UserAggregate.
    NOTE: `uow` type is annotated loosely here until the users module lands and
    UsersStorageUnitOfWork + UserAggregate are importable.
    Replace the annotations once src/modules/users/ exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            get_jwt_config().JWT_TOKEN_SECRET_KEY,
            algorithms=[get_jwt_config().JWT_TOKEN_ALGORITHM],
        )
        if payload.get("scope") != "access_token":
            LOGGER.error("Invalid token scope")
            raise credentials_exception
        email: str | None = payload.get("sub")
        if email is None:
            LOGGER.error("No subject in token")
            raise credentials_exception
    except JWTError as e:
        LOGGER.error("JWT decode error", error=str(e))
        raise credentials_exception from e

    async with uow:
        user = await uow.users.get_one(email=email)

    if user is None:
        raise credentials_exception

    return user
