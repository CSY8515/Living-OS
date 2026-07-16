from __future__ import annotations

from statistics import mean
from typing import Any

from subsystems.health.engines.body_composition import BodyCompositionEngine
from subsystems.health.engines.exercise import ExerciseEngine
from subsystems.health.engines.sleep import SleepEngine
from subsystems.health.engines.weight import WeightEngine


class TrendEngine:
    def __init__(self, weight: WeightEngine, body: BodyCompositionEngine,
                 sleep: SleepEngine, exercise: ExerciseEngine) -> None:
        self.weight, self.body, self.sleep, self.exercise = weight, body, sleep, exercise

    def weight_trend(self, start_on: Any | None = None, end_on: Any | None = None) -> dict[str, Any]:
        rows = self.weight.list(start_on, end_on)
        return _numeric_trend(rows, "measured_on", "weight_kg")

    def inbody_trend(self, start_on: Any | None = None, end_on: Any | None = None) -> dict[str, Any]:
        rows = self.body.timeline(start_on, end_on)
        return {field: _numeric_trend(rows, "measured_on", field) for field in (
            "skeletal_muscle_kg", "body_fat_percent", "bmi"
        )}

    def sleep_trend(self, start_on: Any | None = None, end_on: Any | None = None) -> dict[str, Any]:
        rows = self.sleep.list(start_on, end_on)
        duration = _numeric_trend(rows, "sleep_on", "duration_minutes")
        fatigue = _numeric_trend(rows, "sleep_on", "fatigue")
        return {"duration_minutes": duration, "fatigue": fatigue}

    def exercise_trend(self, start_on: Any | None = None, end_on: Any | None = None) -> dict[str, Any]:
        rows = self.exercise.list(start_on, end_on)
        daily: dict[str, dict[str, int]] = {}
        for row in rows:
            value = daily.setdefault(row["exercised_on"], {"sessions": 0, "duration_minutes": 0, "repetitions": 0})
            value["sessions"] += 1
            value["duration_minutes"] += int(row["duration_minutes"])
            value["repetitions"] += int(row["repetitions"] or 0)
        points = [{"date": key, **value} for key, value in sorted(daily.items())]
        return {"points": points, **self.exercise.statistics(start_on, end_on)}


def _numeric_trend(rows: list[dict[str, Any]], date_field: str, value_field: str) -> dict[str, Any]:
    points = [{"date": row[date_field], "value": float(row[value_field])} for row in rows]
    values = [point["value"] for point in points]
    return {
        "points": points, "count": len(points),
        "first": values[0] if values else None, "latest": values[-1] if values else None,
        "change": round(values[-1] - values[0], 2) if values else None,
        "average": round(mean(values), 2) if values else None,
    }

