from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import optional_text, require_date, require_decimal, require_text, utc_now_iso


class WeightEngine:
    def __init__(self, store: HealthStorageEngine) -> None:
        self.store = store

    def record(self, weight_kg: Any, measured_on: Any, note: Any = "") -> dict[str, Any]:
        now = utc_now_iso()
        record = {
            "record_id": str(uuid4()), "measured_on": require_date(measured_on, "measured_on"),
            "weight_kg": require_decimal(weight_kg, "weight_kg", "20", "500"),
            "note": optional_text(note), "created_at": now, "updated_at": now,
        }
        with self.store.transaction() as connection:
            connection.execute(
                "INSERT INTO weight_records VALUES(?,?,?,?,?,?)", tuple(record.values())
            )
        return self._public(record)

    def update(self, record_id: Any, weight_kg: Any | None = None,
               measured_on: Any | None = None, note: Any | None = None) -> dict[str, Any]:
        identifier = require_text(record_id, "record_id", 80)
        current = self.store.query_one("SELECT * FROM weight_records WHERE record_id=?", (identifier,))
        if current is None:
            raise KeyError("Weight record not found.")
        values = {
            **current,
            "weight_kg": current["weight_kg"] if weight_kg is None else require_decimal(weight_kg, "weight_kg", "20", "500"),
            "measured_on": current["measured_on"] if measured_on is None else require_date(measured_on, "measured_on"),
            "note": current["note"] if note is None else optional_text(note),
            "updated_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                "UPDATE weight_records SET measured_on=?,weight_kg=?,note=?,updated_at=? WHERE record_id=?",
                (values["measured_on"], values["weight_kg"], values["note"], values["updated_at"], identifier),
            )
        return self._public(values)

    def delete(self, record_id: Any) -> bool:
        identifier = require_text(record_id, "record_id", 80)
        with self.store.transaction() as connection:
            deleted = connection.execute("DELETE FROM weight_records WHERE record_id=?", (identifier,)).rowcount
        if not deleted:
            raise KeyError("Weight record not found.")
        return True

    def list(self, start_on: Any | None = None, end_on: Any | None = None) -> list[dict[str, Any]]:
        clauses, parameters = _date_filter("measured_on", start_on, end_on)
        return [self._public(row) for row in self.store.query(
            "SELECT * FROM weight_records" + clauses + " ORDER BY measured_on,created_at", parameters
        )]

    def baseline_comparison(self, record_id: Any | None = None) -> dict[str, Any]:
        records = self.list()
        if not records:
            return {"baseline": None, "current": None, "change_kg": None}
        current = records[-1] if record_id is None else next(
            (row for row in records if row["record_id"] == require_text(record_id, "record_id", 80)), None
        )
        if current is None:
            raise KeyError("Weight record not found.")
        baseline = records[0]
        return {
            "baseline": baseline, "current": current,
            "change_kg": round(current["weight_kg"] - baseline["weight_kg"], 2),
        }

    @staticmethod
    def _public(row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        result["weight_kg"] = float(result["weight_kg"])
        return result


def _date_filter(column: str, start_on: Any | None, end_on: Any | None) -> tuple[str, tuple[Any, ...]]:
    clauses: list[str] = []
    parameters: list[Any] = []
    start = require_date(start_on, "start_on") if start_on is not None else None
    end = require_date(end_on, "end_on") if end_on is not None else None
    if start and end and start > end:
        raise ValueError("start_on cannot be after end_on.")
    if start:
        clauses.append(f"{column}>=?")
        parameters.append(start)
    if end:
        clauses.append(f"{column}<=?")
        parameters.append(end)
    return (f" WHERE {' AND '.join(clauses)}" if clauses else "", tuple(parameters))

