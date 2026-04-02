"""
Central router aggregation.

Routers are included here as modules are implemented:
  auth        → public_router        POST /api/auth/register, /api/auth/login
  users       → authenticated_router GET  /api/users/me, /api/users/{id}
  expeditions → public_router + chief_router
  members     → chief_router + member_router
"""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

# Uncomment when routers exist:
# from src.modules.auth.presentation.api.routers.auth import public_router as auth_router
# api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
