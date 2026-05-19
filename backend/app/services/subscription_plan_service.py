from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.subscription_plan import SubscriptionPlan
from app.repositories.subscription_plan_repository import SubscriptionPlanRepository


class SubscriptionPlanService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = SubscriptionPlanRepository(db)

    def get_plan_or_404(self, plan_id: int) -> SubscriptionPlan:
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found.")
        return plan

    def list_plans(self, *, page: int, page_size: int, search: str | None = None) -> tuple[list[SubscriptionPlan], int]:
        return self.repository.list(page=page, page_size=page_size, search=search)

    def create_plan(self, payload) -> SubscriptionPlan:
        self._ensure_unique_fields(code=payload.code, name=payload.name)
        plan = SubscriptionPlan(**payload.model_dump())
        self.repository.create(plan)
        self.db.commit()
        return self.get_plan_or_404(plan.id)

    def update_plan(self, plan_id: int, payload) -> SubscriptionPlan:
        plan = self.get_plan_or_404(plan_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return plan
        self._ensure_unique_fields(code=updates.get("code"), name=updates.get("name"), exclude_id=plan.id)
        self.repository.update(plan, updates)
        self.db.commit()
        return self.get_plan_or_404(plan.id)

    def _ensure_unique_fields(self, *, code: str | None, name: str | None, exclude_id: int | None = None) -> None:
        if code:
            existing = self.repository.get_by_code(code)
            if existing and existing.id != exclude_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subscription plan code already exists.")

        if name:
            items, _ = self.repository.list(page=1, page_size=1000, search=name)
            for existing in items:
                if existing.name.lower() == name.lower() and existing.id != exclude_id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subscription plan name already exists.")
