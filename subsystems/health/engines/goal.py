from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.health.engines.body_composition import BodyCompositionEngine
from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import optional_decimal, require_date, require_text, utc_now_iso
from subsystems.health.engines.weight import WeightEngine


class GoalEngine:
    def __init__(self, store: HealthStorageEngine, weight: WeightEngine,
                 body: BodyCompositionEngine) -> None:
        self.store, self.weight, self.body = store, weight, body

    def create(self, name: Any, start_on: Any, target_weight_kg: Any | None = None,
               target_body_fat_percent: Any | None = None, target_on: Any | None = None) -> dict[str, Any]:
        target_weight = optional_decimal(target_weight_kg, "target_weight_kg", "20", "500")
        target_fat = optional_decimal(target_body_fat_percent, "target_body_fat_percent", "1", "75")
        if target_weight is None and target_fat is None:
            raise ValueError("At least one Health target is required.")
        start = require_date(start_on, "start_on")
        target_date = require_date(target_on, "target_on") if target_on else None
        if target_date and target_date < start:
            raise ValueError("target_on cannot be before start_on.")
        now = utc_now_iso()
        record = {
            "goal_id": str(uuid4()), "name": require_text(name, "name", 150),
            "target_weight_kg": target_weight, "target_body_fat_percent": target_fat,
            "start_on": start, "target_on": target_date, "status": "active",
            "created_at": now, "updated_at": now,
        }
        with self.store.transaction() as connection:
            connection.execute("INSERT INTO health_goals VALUES(?,?,?,?,?,?,?,?,?)", tuple(record.values()))
        return self._public(record)

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        if status is not None and status not in {"active", "completed", "cancelled"}:
            raise ValueError("Unknown goal status.")
        where, parameters = (" WHERE status=?", (status,)) if status else ("", ())
        return [self._public(row) for row in self.store.query(
            "SELECT * FROM health_goals" + where + " ORDER BY start_on,created_at", parameters
        )]

    def progress(self, goal_id: Any) -> dict[str, Any]:
        identifier = require_text(goal_id, "goal_id", 80)
        goal = next((row for row in self.list() if row["goal_id"] == identifier), None)
        if goal is None:
            raise KeyError("Health goal not found.")
        weights, bodies = self.weight.list(), self.body.timeline()
        current_weight = weights[-1]["weight_kg"] if weights else None
        current_fat = bodies[-1]["body_fat_percent"] if bodies else None
        metrics: dict[str, Any] = {}
        if goal["target_weight_kg"] is not None:
            metrics["weight"] = _metric_progress(
                weights[0]["weight_kg"] if weights else None, current_weight, goal["target_weight_kg"]
            )
        if goal["target_body_fat_percent"] is not None:
            metrics["body_fat"] = _metric_progress(
                bodies[0]["body_fat_percent"] if bodies else None, current_fat, goal["target_body_fat_percent"]
            )
        available = [item["progress_percent"] for item in metrics.values() if item["progress_percent"] is not None]
        return {"goal": goal, "metrics": metrics, "progress_percent": round(sum(available) / len(available), 2) if available else None}

    @staticmethod
    def _public(row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        for field in ("target_weight_kg", "target_body_fat_percent"):
            result[field] = float(result[field]) if result[field] is not None else None
        return result


def _metric_progress(baseline: float | None, current: float | None, target: float) -> dict[str, Any]:
    if baseline is None or current is None:
        return {"baseline": baseline, "current": current, "target": target, "progress_percent": None, "remaining": None}
    distance = target - baseline
    progress = 100.0 if distance == 0 and current == target else (current - baseline) / distance * 100 if distance else 0.0
    return {"baseline": baseline, "current": current, "target": target,
            "progress_percent": round(max(0.0, min(100.0, progress)), 2),
            "remaining": round(abs(target - current), 2)}
