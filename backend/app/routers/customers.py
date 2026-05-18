from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_pagination_params, require_roles
from app.models.customer import Customer
from app.models.enums import RecordStatusEnum, RoleEnum
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.common import PaginationMeta
from app.schemas.customer import CustomerCreate, CustomerListResponse, CustomerResponse, CustomerUpdate
from app.services.master_data_service import MasterDataService

router = APIRouter()


def get_service(db: DbSession) -> MasterDataService:
    return MasterDataService(
        db,
        model=Customer,
        entity_name="Customer",
        search_columns=(Customer.name, Customer.email, Customer.phone, Customer.gst_number),
    )


@router.get("/", response_model=CustomerListResponse)
def list_customers(
    db: DbSession,
    current_user: CurrentUser,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
    status_filter: RecordStatusEnum | None = Query(default=None, alias="status"),
    tenant_id: int | None = Query(default=None),
) -> CustomerListResponse:
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
    return CustomerListResponse(
        items=[CustomerResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
    tenant_id: int | None = Query(default=None),
) -> CustomerResponse:
    customer = get_service(db).create_entity(current_user=current_user, payload=payload, tenant_id=tenant_id)
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: DbSession, current_user: CurrentUser) -> CustomerResponse:
    customer = get_service(db).get_entity_for_user(current_user=current_user, entity_id=customer_id)
    return CustomerResponse.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> CustomerResponse:
    customer = get_service(db).update_entity(current_user=current_user, entity_id=customer_id, payload=payload)
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", response_model=MessageResponse)
def archive_customer(
    customer_id: int,
    db: DbSession,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.TENANT_ADMIN, RoleEnum.SALES_STAFF)),
) -> MessageResponse:
    get_service(db).archive_entity(current_user=current_user, entity_id=customer_id)
    return MessageResponse(detail="Customer archived successfully.")
