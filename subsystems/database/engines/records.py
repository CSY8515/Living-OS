from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def query_records(
    records: Iterable[Mapping[str, Any]],
    *,
    search: str | None = None,
    status: str | None = None,
    sort_by: str | None = None,
    descending: bool = True,
    limit: int = 500,
) -> list[dict[str, Any]]:
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1 or limit > 1000:
        raise ValueError("limit must be an integer between 1 and 1000.")
    needle = str(search or "").strip().casefold()
    selected_status = str(status or "").strip().casefold()
    result: list[dict[str, Any]] = []
    for source in records:
        item = dict(source)
        if selected_status and str(item.get("status", "")).casefold() != selected_status:
            continue
        if needle and needle not in " ".join(
            str(value) for value in item.values() if value is not None
        ).casefold():
            continue
        result.append(item)
    if sort_by:
        field = str(sort_by).strip()
        if result and not any(field in item for item in result):
            raise ValueError(f"Unsupported sort field: {field}")
        result.sort(
            key=lambda item: (
                item.get(field) is None,
                str(item.get(field, "")).casefold(),
            ),
            reverse=bool(descending),
        )
    return result[:limit]


def record_detail(
    records: Iterable[Mapping[str, Any]],
    record_id: Any,
    *,
    id_fields: tuple[str, ...] = (
        "record_id", "transaction_id", "ingredient_id", "recipe_id", "meal_id",
        "candidate_id", "contract_id", "charge_id", "vehicle_id", "trip_id",
        "maintenance_id", "energy_id", "goal_id",
    ),
) -> dict[str, Any]:
    selected = str(record_id or "").strip()
    if not selected:
        raise ValueError("record_id is required.")
    for source in records:
        item = dict(source)
        if any(str(item.get(field, "")) == selected for field in id_fields):
            return item
    raise KeyError("Record not found.")


def dashboard_counts(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    counts = {key: len(value) for key, value in snapshot.items() if isinstance(value, list)}
    return {
        "record_count": sum(counts.values()),
        "collections": counts,
        "archive_count": sum(
            1
            for value in snapshot.values()
            if isinstance(value, list)
            for item in value
            if isinstance(item, Mapping)
            and str(item.get("status", "")).lower() in {"archive", "archived"}
        ),
    }
