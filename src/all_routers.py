from fastapi import APIRouter

from src.modules.auth.presentation.api.routers import auth
from src.modules.expeditions.presentation.api.routers.expeditions import (
    auth_router as expeditions_auth_router,
)
from src.modules.expeditions.presentation.api.routers.expeditions import (
    chief_router as expeditions_chief_router,
)
from src.modules.expeditions.presentation.api.routers.members import (
    chief_router,
    members_router,
)
from src.modules.users.presentation.api.routers.users import authenticated_router
from src.modules.websocket.presentation.api.routers.ws import ws_router

api_router = APIRouter(prefix="/api")

api_router.include_router(ws_router, prefix="/ws", tags=["Websocket"])
api_router.include_router(auth.public_router, prefix="/auth", tags=["Auth"])
api_router.include_router(authenticated_router, prefix="/users", tags=["Users"])
api_router.include_router(
    expeditions_auth_router, prefix="/expeditions", tags=["Expeditions"]
)
api_router.include_router(
    expeditions_chief_router, prefix="/expeditions", tags=["Expeditions"]
)
api_router.include_router(members_router, prefix="/expeditions", tags=["Members"])
api_router.include_router(chief_router, prefix="/expeditions", tags=["Members"])
