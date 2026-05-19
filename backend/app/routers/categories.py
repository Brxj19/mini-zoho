from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.category import Category
from app.models.enums import RecordStatusEnum, RoleEnum
from app.models.product import Product
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse, CategoryUpdate
from app.schemas.common import PaginationMeta
from app.services.master_data_service import MasterDataService

router = APIRouter()


def get_service(db: DbSession) -> MasterDataService:
    return MasterDataService(
        db,
        model=Category,
        entity_name="Category",
        search_columns=(Category.name, Category.description),
        unique_fields=("name",),
        archive_dependencies=((Product, "category_id", "products"),),
    )


@router.get("/", response_model=CategoryListResponse)
def list_categories(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    status_filter: RecordStatusEnum | None = Query(default=None, alias="status"),
    tenant_id: int | None = Query(default=None),
) -> CategoryListResponse:
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
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
    tenant_id: int | None = Query(default=None),
) -> CategoryResponse:
    category = get_service(db).create_entity(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return CategoryResponse.model_validate(category)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: DbSession, current_user: CurrentUser) -> CategoryResponse:
    category = get_service(db).get_entity_for_user(current_user=current_user, entity_id=category_id)
    return CategoryResponse.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> CategoryResponse:
    category = get_service(db).update_entity(current_user=current_user, entity_id=category_id, payload=payload)
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", response_model=MessageResponse)
def archive_category(
    category_id: int,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER)),
) -> MessageResponse:
    get_service(db).archive_entity(current_user=current_user, entity_id=category_id)
    return MessageResponse(detail="Category archived successfully.")
