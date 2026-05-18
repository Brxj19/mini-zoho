from fastapi import APIRouter

from app.routers.app_data import router as app_data_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(app_data_router)
