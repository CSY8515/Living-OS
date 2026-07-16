from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import optional_text, require_date, require_decimal, utc_now_iso
from subsystems.health.engines.weight import _date_filter


class BodyCompositionEngine:
    def __init__(self, store: HealthStorageEngine) -> None:
        self.store = store

    def record(self, measured_on: Any, skeletal_muscle_kg: Any, body_fat_percent: Any,
               bmi: Any, note: Any = "") -> dict[str, Any]:
        record = {
            "record_id": str(uuid4()), "measured_on": require_date(measured_on, "measured_on"),
            "skeletal_muscle_kg": require_decimal(skeletal_muscle_kg, "skeletal_muscle_kg", "1", "150"),
            "body_fat_percent": require_decimal(body_fat_percent, "body_fat_percent", "1", "75"),
            "bmi": require_decimal(bmi, "bmi", "5", "100"), "note": optional_text(note),
            "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute("INSERT INTO body_compositions VALUES(?,?,?,?,?,?,?)", tuple(record.values()))
        return self._public(record)

    def timeline(self, start_on: Any | None = None, end_on: Any | None = None) -> list[dict[str, Any]]:
        where, parameters = _date_filter("measured_on", start_on, end_on)
        return [self._public(row) for row in self.store.query(
            "SELECT * FROM body_compositions" + where + " ORDER BY measured_on,created_at", parameters
        )]

    def baseline_comparison(self) -> dict[str, Any]:
        rows = self.timeline()
        if not rows:
            return {"baseline": None, "current": None, "changes": {}}
        fields = ("skeletal_muscle_kg", "body_fat_percent", "bmi")
        return {"baseline": rows[0], "current": rows[-1], "changes": {
            field: round(rows[-1][field] - rows[0][field], 2) for field in fields
        }}

    @staticmethod
    def _public(row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        for field in ("skeletal_muscle_kg", "body_fat_percent", "bmi"):
            result[field] = float(result[field])
        return result

