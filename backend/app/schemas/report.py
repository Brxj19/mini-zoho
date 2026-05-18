from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ReportTableResponse(BaseModel):
    report_name: str
    generated_at: datetime
    filters: dict[str, Any]
    row_count: int
    rows: list[dict[str, Any]]
