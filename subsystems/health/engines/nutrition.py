from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import optional_text, require_date, require_text, utc_now_iso
from subsystems.health.engines.weight import _date_filter


class NutritionEngine:
    def __init__(self, store: HealthStorageEngine) -> None:
        self.store = store

    def record(self, eaten_on: Any, meal_type: Any, note: Any,
               goal_id: Any | None = None) -> dict[str, Any]:
        identifier = require_text(goal_id, "goal_id", 80) if goal_id else None
        if identifier and self.store.query_one("SELECT goal_id FROM health_goals WHERE goal_id=?", (identifier,)) is None:
            raise KeyError("Health goal not found.")
        record = {
            "record_id": str(uuid4()), "eaten_on": require_date(eaten_on, "eaten_on"),
            "meal_type": require_text(meal_type, "meal_type", 80),
            "note": optional_text(note), "goal_id": identifier, "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute("INSERT INTO nutrition_records VALUES(?,?,?,?,?,?)", tuple(record.values()))
        return record

    def list(self, start_on: Any | None = None, end_on: Any | None = None) -> list[dict[str, Any]]:
        where, parameters = _date_filter("eaten_on", start_on, end_on)
        return self.store.query("SELECT * FROM nutrition_records" + where + " ORDER BY eaten_on,created_at", parameters)
