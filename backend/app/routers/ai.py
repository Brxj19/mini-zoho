from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.ai import AIAssistantRequest
from app.schemas.ai import AIAssistantResponse
from app.schemas.ai import IntegrationCatalogResponse
from app.schemas.ai import ReportSummaryRequest
from app.schemas.ai import ReportSummaryResponse
from app.schemas.ai import ReorderSuggestionListResponse
from app.services.ai_assistant_service import AIAssistantService

router = APIRouter()


@router.post("/ai/assistant", response_model=AIAssistantResponse)
def ask_ai_assistant(payload: AIAssistantRequest, db: DbSession, current_user: CurrentUser) -> AIAssistantResponse:
    answer, facts = AIAssistantService(db).ask(current_user=current_user, question=payload.question, tenant_id=payload.tenant_id)
    return AIAssistantResponse(answer=answer, facts=facts, generated_at=datetime.now(timezone.utc))


@router.get("/ai/reorder-suggestions", response_model=ReorderSuggestionListResponse)
def list_reorder_suggestions(
    db: DbSession,
    current_user: CurrentUser,
    tenant_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> ReorderSuggestionListResponse:
    items = AIAssistantService(db).get_reorder_suggestions(current_user=current_user, tenant_id=tenant_id, limit=limit)
    return ReorderSuggestionListResponse(items=items, generated_at=datetime.now(timezone.utc))


@router.post("/ai/report-summary", response_model=ReportSummaryResponse)
def summarize_report(payload: ReportSummaryRequest, db: DbSession, current_user: CurrentUser) -> ReportSummaryResponse:
    summary = AIAssistantService(db).summarize_report(current_user=current_user, report_key=payload.report_key, tenant_id=payload.tenant_id)
    return ReportSummaryResponse(report_key=payload.report_key, summary=summary, generated_at=datetime.now(timezone.utc))


@router.get("/integrations/catalog", response_model=IntegrationCatalogResponse)
def integration_catalog(db: DbSession, current_user: CurrentUser, tenant_id: int | None = Query(default=None)) -> IntegrationCatalogResponse:
    items = AIAssistantService(db).integration_catalog(current_user=current_user, tenant_id=tenant_id)
    return IntegrationCatalogResponse(items=items)
