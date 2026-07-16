from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import optional_text, require_date, require_integer, require_text, utc_now_iso
from subsystems.health.engines.weight import _date_filter


class ExerciseEngine:
    def __init__(self, store: HealthStorageEngine) -> None:
        self.store = store

    def record(self, exercised_on: Any, activity: Any, duration_minutes: Any,
               repetitions: Any | None = None, note: Any = "") -> dict[str, Any]:
        record = {
            "record_id": str(uuid4()), "exercised_on": require_date(exercised_on, "exercised_on"),
            "activity": require_text(activity, "activity", 120),
            "duration_minutes": require_integer(duration_minutes, "duration_minutes", 1, 1440),
            "repetitions": None if repetitions is None or repetitions == "" else require_integer(repetitions, "repetitions", 0, 1000000),
            "note": optional_text(note), "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute("INSERT INTO exercise_records VALUES(?,?,?,?,?,?,?)", tuple(record.values()))
        return record

    def list(self, start_on: Any | None = None, end_on: Any | None = None) -> list[dict[str, Any]]:
        where, parameters = _date_filter("exercised_on", start_on, end_on)
        return self.store.query("SELECT * FROM exercise_records" + where + " ORDER BY exercised_on,created_at", parameters)

    def statistics(self, start_on: Any | None = None, end_on: Any | None = None) -> dict[str, Any]:
        rows = self.list(start_on, end_on)
        by_activity: dict[str, dict[str, int]] = {}
        for row in rows:
            item = by_activity.setdefault(row["activity"], {"sessions": 0, "duration_minutes": 0, "repetitions": 0})
            item["sessions"] += 1
            item["duration_minutes"] += int(row["duration_minutes"])
            item["repetitions"] += int(row["repetitions"] or 0)
        return {
            "sessions": len(rows), "duration_minutes": sum(int(row["duration_minutes"]) for row in rows),
            "repetitions": sum(int(row["repetitions"] or 0) for row in rows), "by_activity": by_activity,
        }

