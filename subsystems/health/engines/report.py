from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from subsystems.health.engines.body_composition import BodyCompositionEngine
from subsystems.health.engines.exercise import ExerciseEngine
from subsystems.health.engines.goal import GoalEngine
from subsystems.health.engines.health_checkup import HealthCheckupEngine
from subsystems.health.engines.nutrition import NutritionEngine
from subsystems.health.engines.sleep import SleepEngine
from subsystems.health.engines.validation import require_date
from subsystems.health.engines.weight import WeightEngine


class HealthReportEngine:
    def __init__(self, weight: WeightEngine, body: BodyCompositionEngine,
                 checkup: HealthCheckupEngine, sleep: SleepEngine,
                 exercise: ExerciseEngine, nutrition: NutritionEngine,
                 goal: GoalEngine) -> None:
        self.weight, self.body, self.checkup = weight, body, checkup
        self.sleep, self.exercise, self.nutrition, self.goal = sleep, exercise, nutrition, goal

    def daily(self, on: Any) -> dict[str, Any]:
        day = require_date(on, "on")
        return self._period("daily", day, day)

    def weekly(self, week_ending: Any) -> dict[str, Any]:
        end = date.fromisoformat(require_date(week_ending, "week_ending"))
        return self._period("weekly", (end - timedelta(days=6)).isoformat(), end.isoformat())

    def monthly(self, month: Any) -> dict[str, Any]:
        text = str(month)
        try:
            start = date.fromisoformat(f"{text}-01")
        except ValueError as exc:
            raise ValueError("month must use YYYY-MM.") from exc
        next_month = date(start.year + (start.month == 12), 1 if start.month == 12 else start.month + 1, 1)
        return self._period("monthly", start.isoformat(), (next_month - timedelta(days=1)).isoformat())

    def _period(self, kind: str, start_on: str, end_on: str) -> dict[str, Any]:
        weights = self.weight.list(start_on, end_on)
        bodies = self.body.timeline(start_on, end_on)
        sleeps = self.sleep.list(start_on, end_on)
        exercises = self.exercise.statistics(start_on, end_on)
        meals = self.nutrition.list(start_on, end_on)
        checkups = self.checkup.list(start_on, end_on)
        active_goals = self.goal.list("active")
        progress = [self.goal.progress(item["goal_id"]) for item in active_goals]
        average_sleep = round(sum(row["duration_minutes"] for row in sleeps) / len(sleeps), 2) if sleeps else None
        actions: list[str] = []
        if not weights:
            actions.append("Record a weight measurement for baseline continuity.")
        if average_sleep is None:
            actions.append("Record sleep and fatigue.")
        elif average_sleep < 420:
            actions.append("Review the next sleep opportunity; the period average is below seven hours.")
        if exercises["duration_minutes"] == 0:
            actions.append("Plan the next exercise session.")
        if not meals:
            actions.append("Add a nutrition note linked to the current Health goal.")
        for item in checkups:
            if item["follow_up_on"] and item["follow_up_on"] <= end_on:
                actions.append(f"Review follow-up for {item['title']} ({item['follow_up_on']}).")
        return {
            "period": {"kind": kind, "start_on": start_on, "end_on": end_on},
            "weight": {"records": len(weights), "baseline_comparison": self.weight.baseline_comparison()},
            "body_composition": {"records": len(bodies), "baseline_comparison": self.body.baseline_comparison()},
            "checkups": checkups, "sleep": {"records": len(sleeps), "average_minutes": average_sleep},
            "exercise": exercises, "nutrition": {"records": len(meals)},
            "goals": progress, "next_actions": actions,
            "medical_notice": "Informational personal record summary; not a diagnosis or medical advice.",
        }
