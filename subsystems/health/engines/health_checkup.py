from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import optional_text, require_date, require_metrics, require_text, utc_now_iso
from subsystems.health.engines.weight import _date_filter


class HealthCheckupEngine:
    def __init__(self, store: HealthStorageEngine) -> None:
        self.store = store

    def record(self, checked_on: Any, title: Any, assessment: Any,
               follow_up_on: Any | None = None, metrics: Any = None, note: Any = "") -> dict[str, Any]:
        checked = require_date(checked_on, "checked_on")
        follow_up = require_date(follow_up_on, "follow_up_on") if follow_up_on else None
        if follow_up and follow_up < checked:
            raise ValueError("follow_up_on cannot be before checked_on.")
        record = {
            "record_id": str(uuid4()), "checked_on": checked,
            "title": require_text(title, "title", 200),
            "assessment": require_text(assessment, "assessment", 1000),
            "follow_up_on": follow_up, "metrics": require_metrics(metrics),
            "note": optional_text(note), "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                "INSERT INTO health_checkups VALUES(?,?,?,?,?,?,?,?)",
                (record["record_id"], checked, record["title"], record["assessment"], follow_up,
                 json.dumps(record["metrics"], sort_keys=True), record["note"], record["created_at"]),
            )
        return record

    def list(self, start_on: Any | None = None, end_on: Any | None = None) -> list[dict[str, Any]]:
        where, parameters = _date_filter("checked_on", start_on, end_on)
        rows = self.store.query("SELECT * FROM health_checkups" + where + " ORDER BY checked_on,created_at", parameters)
        for row in rows:
            row["metrics"] = json.loads(row.pop("metrics_json"))
        return rows

    def get(self, record_id: Any) -> dict[str, Any]:
        key = str(record_id or "").strip()
        row = self.store.query_one("SELECT * FROM health_checkups WHERE record_id=?", (key,))
        if row is None:
            raise KeyError("Health checkup not found.")
        row["metrics"] = json.loads(row.pop("metrics_json"))
        return row

    def update(self, record_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(record_id)
        allowed = {"checked_on", "title", "assessment", "follow_up_on", "metrics", "note"}
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported checkup fields: {sorted(unexpected)}")
        checked = require_date(changes.get("checked_on", current["checked_on"]), "checked_on")
        follow_value = changes.get("follow_up_on", current["follow_up_on"])
        follow = require_date(follow_value, "follow_up_on") if follow_value else None
        if follow and follow < checked:
            raise ValueError("follow_up_on cannot be before checked_on.")
        with self.store.transaction() as connection:
            connection.execute(
                "UPDATE health_checkups SET checked_on=?,title=?,assessment=?,follow_up_on=?,metrics_json=?,note=? WHERE record_id=?",
                (
                    checked,
                    require_text(changes.get("title", current["title"]), "title", 200),
                    require_text(changes.get("assessment", current["assessment"]), "assessment", 1000),
                    follow,
                    json.dumps(require_metrics(changes.get("metrics", current["metrics"])), sort_keys=True),
                    optional_text(changes.get("note", current["note"])),
                    current["record_id"],
                ),
            )
        return self.get(current["record_id"])

    def delete(self, record_id: Any) -> bool:
        current = self.get(record_id)
        with self.store.transaction() as connection:
            cursor = connection.execute("DELETE FROM health_checkups WHERE record_id=?", (current["record_id"],))
        return cursor.rowcount == 1

    def follow_ups(self, as_of: Any | None = None) -> list[dict[str, Any]]:
        reference = require_date(as_of, "as_of") if as_of else None
        rows = self.list()
        return [row for row in rows if row["follow_up_on"] and (reference is None or row["follow_up_on"] >= reference)]

    def baseline_comparison(self) -> dict[str, Any]:
        rows = self.list()
        if not rows:
            return {"baseline": None, "current": None, "metric_changes": {}}
        baseline, current = rows[0], rows[-1]
        shared = baseline["metrics"].keys() & current["metrics"].keys()
        return {"baseline": baseline, "current": current, "metric_changes": {
            key: round(current["metrics"][key] - baseline["metrics"][key], 4) for key in shared
        }}
