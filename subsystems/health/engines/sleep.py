from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import optional_text, require_date, require_datetime, require_integer, utc_now_iso
from subsystems.health.engines.weight import _date_filter


class SleepEngine:
    def __init__(self, store: HealthStorageEngine) -> None:
        self.store = store

    def record(self, bedtime: Any, wake_time: Any, fatigue: Any, note: Any = "") -> dict[str, Any]:
        bed = require_datetime(bedtime, "bedtime")
        wake = require_datetime(wake_time, "wake_time")
        minutes = int((datetime.fromisoformat(wake) - datetime.fromisoformat(bed)).total_seconds() // 60)
        if minutes < 1 or minutes > 1440:
            raise ValueError("sleep duration must be between 1 and 1440 minutes.")
        record = {
            "record_id": str(uuid4()), "sleep_on": require_date(bed[:10], "sleep_on"),
            "bedtime": bed, "wake_time": wake, "duration_minutes": minutes,
            "fatigue": require_integer(fatigue, "fatigue", 1, 5),
            "note": optional_text(note), "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute("INSERT INTO sleep_records VALUES(?,?,?,?,?,?,?,?)", tuple(record.values()))
        return record

    def list(self, start_on: Any | None = None, end_on: Any | None = None) -> list[dict[str, Any]]:
        where, parameters = _date_filter("sleep_on", start_on, end_on)
        return self.store.query("SELECT * FROM sleep_records" + where + " ORDER BY sleep_on,bedtime", parameters)

