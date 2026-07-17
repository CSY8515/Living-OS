from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.health.engines.body_composition import BodyCompositionEngine
from subsystems.health.engines.exercise import ExerciseEngine
from subsystems.health.engines.goal import GoalEngine
from subsystems.health.engines.health_checkup import HealthCheckupEngine
from subsystems.health.engines.migration import HealthMigrationEngine
from subsystems.health.engines.nutrition import NutritionEngine
from subsystems.health.engines.report import HealthReportEngine
from subsystems.health.engines.sleep import SleepEngine
from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.trend import TrendEngine
from subsystems.health.engines.weight import WeightEngine

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


class HealthSubsystem:
    """The only supported Living OS boundary for Health Subsystem v1.0."""

    VERSION = "1.0.0"
    LIVING_OS_COMPATIBILITY = ">=1.3,<2.0"
    PRIVACY_CLASS = "sensitive"

    def __init__(self, root: Path, database_path: Path | None = None,
                 database_foundation: DatabaseSubsystem | None = None) -> None:
        self.root = Path(root)
        path = Path(database_path) if database_path is not None else self.root / "data" / "health" / "health.sqlite3"
        store = HealthStorageEngine(path, database_foundation)
        store.register_contract(schema_version=1, migration_id="health-schema-v1")
        weight = WeightEngine(store)
        body = BodyCompositionEngine(store)
        checkup = HealthCheckupEngine(store)
        sleep = SleepEngine(store)
        exercise = ExerciseEngine(store)
        nutrition = NutritionEngine(store)
        goal = GoalEngine(store, weight, body)
        trend = TrendEngine(weight, body, sleep, exercise)
        report = HealthReportEngine(weight, body, checkup, sleep, exercise, nutrition, goal)
        self._store, self._weight, self._body, self._checkup = store, weight, body, checkup
        self._sleep, self._exercise, self._nutrition = sleep, exercise, nutrition
        self._goal, self._trend, self._report = goal, trend, report
        self._migration = HealthMigrationEngine(store)

    @property
    def database_path(self) -> Path:
        return self._store.database_path

    def health(self) -> dict[str, Any]:
        return {**self._store.health(), "subsystem": "health", "version": self.VERSION,
                "living_os_compatibility": self.LIVING_OS_COMPATIBILITY, "privacy_class": self.PRIVACY_CLASS}

    def interface_manifest(self) -> dict[str, Any]:
        return {
            "subsystem": "health", "version": self.VERSION,
            "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
            "privacy_class": self.PRIVACY_CLASS,
            "capabilities": ("weight", "body-composition", "health-checkup", "sleep", "exercise",
                             "nutrition", "trend", "goal", "health-report", "migration"),
        }

    def record_weight(self, weight_kg: Any, measured_on: Any, note: Any = "") -> dict[str, Any]:
        return self._weight.record(weight_kg, measured_on, note)

    def update_weight(self, record_id: Any, **changes: Any) -> dict[str, Any]:
        return self._weight.update(record_id, **changes)

    def delete_weight(self, record_id: Any) -> bool:
        return self._weight.delete(record_id)

    def list_weights(self, **filters: Any) -> list[dict[str, Any]]:
        return self._weight.list(**filters)

    def weight_baseline_comparison(self, record_id: Any | None = None) -> dict[str, Any]:
        return self._weight.baseline_comparison(record_id)

    def record_body_composition(self, measured_on: Any, skeletal_muscle_kg: Any,
                                body_fat_percent: Any, bmi: Any, note: Any = "") -> dict[str, Any]:
        return self._body.record(measured_on, skeletal_muscle_kg, body_fat_percent, bmi, note)

    def body_composition_timeline(self, **filters: Any) -> list[dict[str, Any]]:
        return self._body.timeline(**filters)

    def body_composition_baseline_comparison(self) -> dict[str, Any]:
        return self._body.baseline_comparison()

    def record_health_checkup(self, checked_on: Any, title: Any, assessment: Any,
                              follow_up_on: Any | None = None, metrics: Any = None,
                              note: Any = "") -> dict[str, Any]:
        return self._checkup.record(checked_on, title, assessment, follow_up_on, metrics, note)

    def list_health_checkups(self, **filters: Any) -> list[dict[str, Any]]:
        return self._checkup.list(**filters)

    def health_checkup_follow_ups(self, as_of: Any | None = None) -> list[dict[str, Any]]:
        return self._checkup.follow_ups(as_of)

    def health_checkup_baseline_comparison(self) -> dict[str, Any]:
        return self._checkup.baseline_comparison()

    def record_sleep(self, bedtime: Any, wake_time: Any, fatigue: Any, note: Any = "") -> dict[str, Any]:
        return self._sleep.record(bedtime, wake_time, fatigue, note)

    def list_sleep(self, **filters: Any) -> list[dict[str, Any]]:
        return self._sleep.list(**filters)

    def record_exercise(self, exercised_on: Any, activity: Any, duration_minutes: Any,
                        repetitions: Any | None = None, note: Any = "") -> dict[str, Any]:
        return self._exercise.record(exercised_on, activity, duration_minutes, repetitions, note)

    def list_exercise(self, **filters: Any) -> list[dict[str, Any]]:
        return self._exercise.list(**filters)

    def exercise_statistics(self, **filters: Any) -> dict[str, Any]:
        return self._exercise.statistics(**filters)

    def record_nutrition(self, eaten_on: Any, meal_type: Any, note: Any,
                         goal_id: Any | None = None) -> dict[str, Any]:
        return self._nutrition.record(eaten_on, meal_type, note, goal_id)

    def list_nutrition(self, **filters: Any) -> list[dict[str, Any]]:
        return self._nutrition.list(**filters)

    def create_health_goal(self, name: Any, start_on: Any, target_weight_kg: Any | None = None,
                           target_body_fat_percent: Any | None = None,
                           target_on: Any | None = None) -> dict[str, Any]:
        return self._goal.create(name, start_on, target_weight_kg, target_body_fat_percent, target_on)

    def list_health_goals(self, status: str | None = None) -> list[dict[str, Any]]:
        return self._goal.list(status)

    def health_goal_progress(self, goal_id: Any) -> dict[str, Any]:
        return self._goal.progress(goal_id)

    def weight_trend(self, **filters: Any) -> dict[str, Any]:
        return self._trend.weight_trend(**filters)

    def inbody_trend(self, **filters: Any) -> dict[str, Any]:
        return self._trend.inbody_trend(**filters)

    def sleep_trend(self, **filters: Any) -> dict[str, Any]:
        return self._trend.sleep_trend(**filters)

    def exercise_trend(self, **filters: Any) -> dict[str, Any]:
        return self._trend.exercise_trend(**filters)

    def daily_report(self, on: Any) -> dict[str, Any]:
        return self._report.daily(on)

    def weekly_report(self, week_ending: Any) -> dict[str, Any]:
        return self._report.weekly(week_ending)

    def monthly_report(self, month: Any) -> dict[str, Any]:
        return self._report.monthly(month)

    def dry_run_legacy_json(self, source: Path) -> dict[str, Any]:
        return self._migration.dry_run_legacy_json(Path(source))

    def migrate_legacy_json(self, source: Path) -> dict[str, Any]:
        return self._migration.migrate_legacy_json(Path(source))

    def export_snapshot(self) -> dict[str, Any]:
        return self._store.export_snapshot()
