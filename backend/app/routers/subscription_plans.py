from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import DbSession, get_pagination_params, require_roles
from app.models.enums import RoleEnum
from app.schemas.common import PaginationMeta
from app.schemas.subscription_plan import (
    SubscriptionPlanCreate,
    SubscriptionPlanListResponse,
    SubscriptionPlanResponse,
    SubscriptionPlanUpdate,
)
from app.services.subscription_plan_service import SubscriptionPlanService

router = APIRouter()


@router.get("/", response_model=SubscriptionPlanListResponse)
def list_subscription_plans(
    db: DbSession,
    pagination: tuple[int, int] = Depends(get_pagination_params),
    search: str | None = Query(default=None),
) -> SubscriptionPlanListResponse:
    page, page_size = pagination
    items, total = SubscriptionPlanService(db).list_plans(page=page, page_size=page_size, search=search)
    return SubscriptionPlanListResponse(
        items=[SubscriptionPlanResponse.model_validate(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post("/", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_subscription_plan(
    payload: SubscriptionPlanCreate,
    db: DbSession,
    _=Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> SubscriptionPlanResponse:
    plan = SubscriptionPlanService(db).create_plan(payload)
    return SubscriptionPlanResponse.model_validate(plan)


@router.get("/{plan_id}", response_model=SubscriptionPlanResponse)
def get_subscription_plan(plan_id: int, db: DbSession) -> SubscriptionPlanResponse:
    plan = SubscriptionPlanService(db).get_plan_or_404(plan_id)
    return SubscriptionPlanResponse.model_validate(plan)


@router.patch("/{plan_id}", response_model=SubscriptionPlanResponse)
def update_subscription_plan(
    plan_id: int,
    payload: SubscriptionPlanUpdate,
    db: DbSession,
    _=Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> SubscriptionPlanResponse:
    plan = SubscriptionPlanService(db).update_plan(plan_id, payload)
    return SubscriptionPlanResponse.model_validate(plan)
