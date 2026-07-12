from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


DATE_WINDOWS = {
    "All time": None,
    "Last 7 days": 6,
    "Last 30 days": 29,
    "This month": "month",
}


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except (TypeError, ValueError):
        return None


def window_bounds(window: str, today: date | None = None) -> tuple[date | None, date | None]:
    current = today or date.today()
    selected = DATE_WINDOWS.get(window)
    if selected == "month":
        return current.replace(day=1), current
    if isinstance(selected, int):
        return current - timedelta(days=selected), current
    return None, None


def record_date(record: dict[str, Any]) -> date | None:
    for field in ("updated_at", "created_at", "date"):
        parsed = parse_date(record.get(field))
        if parsed is not None:
            return parsed
    return None


def filter_records_by_window(
    records: list[dict[str, Any]],
    window: str,
    today: date | None = None,
) -> list[dict[str, Any]]:
    start, end = window_bounds(window, today)
    if start is None or end is None:
        return records
    return [
        record
        for record in records
        if (parsed := record_date(record)) is not None and start <= parsed <= end
    ]
