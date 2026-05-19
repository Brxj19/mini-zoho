from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.subscription_plan import SubscriptionPlan


class SubscriptionPlanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        self.db.add(plan)
        self.db.flush()
        self.db.refresh(plan)
        return plan

    def get_by_id(self, plan_id: int) -> SubscriptionPlan | None:
        return self.db.get(SubscriptionPlan, plan_id)

    def get_by_code(self, code: str) -> SubscriptionPlan | None:
        return self.db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == code))

    def list(self, *, page: int, page_size: int, search: str | None = None) -> tuple[list[SubscriptionPlan], int]:
        query: Select[tuple[SubscriptionPlan]] = select(SubscriptionPlan)
        count_query = select(func.count(SubscriptionPlan.id))

        if search:
            search_filter = or_(
                SubscriptionPlan.name.ilike(f"%{search}%"),
                SubscriptionPlan.code.ilike(f"%{search}%"),
                SubscriptionPlan.description.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        query = query.order_by(SubscriptionPlan.monthly_price.asc(), SubscriptionPlan.id.asc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.scalars(query).all())
        total = self.db.scalar(count_query) or 0
        return items, total

    def update(self, plan: SubscriptionPlan, updates: dict[str, object]) -> SubscriptionPlan:
        for field, value in updates.items():
            setattr(plan, field, value)
        self.db.add(plan)
        self.db.flush()
        self.db.refresh(plan)
        return plan
