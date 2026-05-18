from fastapi import APIRouter
from sqlalchemy import text

from app.core.dependencies import DbSession

router = APIRouter()


@router.get("/", summary="Application health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/db", summary="Database connectivity health check")
def database_health_check(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

