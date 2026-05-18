from __future__ import annotations

import csv
from io import StringIO

from fastapi.responses import StreamingResponse


def build_csv_response(*, filename: str, rows: list[dict]) -> StreamingResponse:
    buffer = StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    else:
        writer = csv.writer(buffer)
        writer.writerow(["message"])
        writer.writerow(["No data"])
    buffer.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers=headers)
