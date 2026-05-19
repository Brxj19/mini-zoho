import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.errors import register_exception_handlers
from app.middleware import setup_middlewares
from app.routers.api import api_router
from app.services.bootstrap_service import ensure_super_admin
from app.services.seed_service import ensure_demo_workspace

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = SessionLocal()
    try:
        ensure_super_admin(db)
        if settings.env.lower() == "development":
            ensure_demo_workspace(db)
    except SQLAlchemyError:
        logger.exception("Startup seed failed.")
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

setup_middlewares(app, settings)
register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
