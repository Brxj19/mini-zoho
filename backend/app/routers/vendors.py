from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.enums import RecordStatusEnum, RoleEnum
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.auth import MessageResponse
from app.schemas.common import PaginationMeta
from app.schemas.vendor import VendorCreate, VendorListResponse, VendorResponse, VendorUpdate
from app.services.master_data_service import MasterDataService

router = APIRouter()


def get_service(db: DbSession) -> MasterDataService:
    return MasterDataService(
        db,
        model=Vendor,
        entity_name="Vendor",
        search_columns=(Vendor.name, Vendor.email, Vendor.phone, Vendor.gst_number),
    )


@router.get("/", response_model=VendorListResponse)
def list_vendors(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    status_filter: RecordStatusEnum | None = Query(default=None, alias="status"),
    tenant_id: int | None = Query(default=None),
) -> VendorListResponse:
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
    return VendorListResponse(
        items=[VendorResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(
    payload: VendorCreate,
    db: DbSession,
    current_user: User = Depends(
        require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER, RoleEnum.PURCHASE_STAFF)
    ),
    tenant_id: int | None = Query(default=None),
) -> VendorResponse:
    vendor = get_service(db).create_entity(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return VendorResponse.model_validate(vendor)


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: DbSession, current_user: CurrentUser) -> VendorResponse:
    vendor = get_service(db).get_entity_for_user(current_user=current_user, entity_id=vendor_id)
    return VendorResponse.model_validate(vendor)


@router.patch("/{vendor_id}", response_model=VendorResponse)
def update_vendor(
    vendor_id: int,
    payload: VendorUpdate,
    db: DbSession,
    current_user: User = Depends(
        require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER, RoleEnum.PURCHASE_STAFF)
    ),
) -> VendorResponse:
    vendor = get_service(db).update_entity(current_user=current_user, entity_id=vendor_id, payload=payload)
    return VendorResponse.model_validate(vendor)


@router.delete("/{vendor_id}", response_model=MessageResponse)
def archive_vendor(
    vendor_id: int,
    db: DbSession,
    current_user: User = Depends(
        require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.INVENTORY_MANAGER, RoleEnum.PURCHASE_STAFF)
    ),
) -> MessageResponse:
    get_service(db).archive_entity(current_user=current_user, entity_id=vendor_id)
    return MessageResponse(detail="Vendor archived successfully.")
