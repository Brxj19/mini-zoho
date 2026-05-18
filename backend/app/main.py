from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import SessionLocal, engine
from app.core.errors import register_exception_handlers
from app.models import Base
from app.routers.api import api_router
from app.services.seed_service import rebuild_schema_if_needed, seed_demo_data

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if settings.env == "development":
            rebuild_schema_if_needed(db)
        seed_demo_data(db, settings.super_admin_email, settings.super_admin_password)
    finally:
        db.close()


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
