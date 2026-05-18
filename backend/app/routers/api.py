from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.tenants import router as tenants_router
from app.routers.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
