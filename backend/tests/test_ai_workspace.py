from __future__ import annotations

from app.services.ai_assistant_service import AIAssistantService


def test_ai_assistant_and_reorder_suggestions_use_live_tenant_data(db, tenant_context):
    service = AIAssistantService(db)

    answer, facts = service.ask(current_user=tenant_context.user, question="What should I reorder first?")
    suggestions = service.get_reorder_suggestions(current_user=tenant_context.user, limit=10)
    integrations = service.integration_catalog(current_user=tenant_context.user)

    assert isinstance(answer, str)
    assert facts
    assert suggestions == []
    assert len(integrations) == 3
