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

    def get(self, record_id: Any) -> dict[str, Any]:
        key = str(record_id or "").strip()
        row = self.store.query_one("SELECT * FROM body_compositions WHERE record_id=?", (key,))
        if row is None:
            raise KeyError("InBody record not found.")
        return self._public(row)

    def update(self, record_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(record_id)
        allowed = {"measured_on", "skeletal_muscle_kg", "body_fat_percent", "bmi", "note"}
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported InBody fields: {sorted(unexpected)}")
        with self.store.transaction() as connection:
            connection.execute(
                "UPDATE body_compositions SET measured_on=?,skeletal_muscle_kg=?,body_fat_percent=?,bmi=?,note=? WHERE record_id=?",
                (
                    require_date(changes.get("measured_on", current["measured_on"]), "measured_on"),
                    require_decimal(changes.get("skeletal_muscle_kg", current["skeletal_muscle_kg"]), "skeletal_muscle_kg", "1", "150"),
                    require_decimal(changes.get("body_fat_percent", current["body_fat_percent"]), "body_fat_percent", "1", "75"),
                    require_decimal(changes.get("bmi", current["bmi"]), "bmi", "5", "100"),
                    optional_text(changes.get("note", current["note"])),
                    current["record_id"],
                ),
            )
        return self.get(current["record_id"])

    def delete(self, record_id: Any) -> bool:
        current = self.get(record_id)
        with self.store.transaction() as connection:
            cursor = connection.execute("DELETE FROM body_compositions WHERE record_id=?", (current["record_id"],))
        return cursor.rowcount == 1

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

