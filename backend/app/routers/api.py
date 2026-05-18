from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.brands import router as brands_router
from app.routers.categories import router as categories_router
from app.routers.customers import router as customers_router
from app.routers.health import router as health_router
from app.routers.inventory import router as inventory_router
from app.routers.products import router as products_router
from app.routers.tenants import router as tenants_router
from app.routers.users import router as users_router
from app.routers.vendors import router as vendors_router
from app.routers.warehouses import router as warehouses_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(brands_router, prefix="/brands", tags=["brands"])
api_router.include_router(vendors_router, prefix="/vendors", tags=["vendors"])
api_router.include_router(customers_router, prefix="/customers", tags=["customers"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(warehouses_router, prefix="/warehouses", tags=["warehouses"])
