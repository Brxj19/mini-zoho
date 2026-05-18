from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.brand import Brand
from app.models.enums import RecordStatusEnum, RoleEnum
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.brand import BrandCreate, BrandListResponse, BrandResponse, BrandUpdate
from app.schemas.common import PaginationMeta
from app.services.master_data_service import MasterDataService

router = APIRouter()


def get_service(db: DbSession) -> MasterDataService:
    return MasterDataService(
        db,
        model=Brand,
        entity_name="Brand",
        search_columns=(Brand.name, Brand.description),
        unique_fields=("name",),
    )


@router.get("/", response_model=BrandListResponse)
def list_brands(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    status_filter: RecordStatusEnum | None = Query(default=None, alias="status"),
    tenant_id: int | None = Query(default=None),
) -> BrandListResponse:
    page, page_size = pagination
    service = get_service(db)
    items, total = service.list_entities(
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        tenant_id=tenant_id,
    )
    return BrandListResponse(
        items=[BrandResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    payload: BrandCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
    tenant_id: int | None = Query(default=None),
) -> BrandResponse:
    brand = get_service(db).create_entity(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return BrandResponse.model_validate(brand)


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: int, db: DbSession, current_user: CurrentUser) -> BrandResponse:
    brand = get_service(db).get_entity_for_user(current_user=current_user, entity_id=brand_id)
    return BrandResponse.model_validate(brand)


@router.patch("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    payload: BrandUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> BrandResponse:
    brand = get_service(db).update_entity(current_user=current_user, entity_id=brand_id, payload=payload)
    return BrandResponse.model_validate(brand)


@router.delete("/{brand_id}", response_model=MessageResponse)
def archive_brand(
    brand_id: int,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> MessageResponse:
    get_service(db).archive_entity(current_user=current_user, entity_id=brand_id)
    return MessageResponse(detail="Brand archived successfully.")
