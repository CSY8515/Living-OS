from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

import subsystems.health as health_package
from subsystems.health import HealthSubsystem
from subsystems.operations.engines.catalog import V13_STABLE_MANIFESTS


class HealthSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / "health.sqlite3"
        self.health = HealthSubsystem(self.root, self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_public_interface_and_lazy_independent_storage(self) -> None:
        self.assertEqual(health_package.__all__, ["HealthSubsystem"])
        self.assertFalse(self.database.exists())
        self.assertEqual(self.health.health()["status"], "ready")
        self.assertEqual(self.health.list_weights(), [])
        self.assertEqual(self.health.monthly_report("2026-07")["weight"]["records"], 0)
        self.assertFalse(self.database.exists())
        second = HealthSubsystem(self.root, self.root / "second.sqlite3")
        self.health.record_weight(80, "2026-07-01")
        self.assertEqual(second.list_weights(), [])
        manifest = self.health.interface_manifest()
        self.assertEqual(manifest["privacy_class"], "sensitive")
        self.assertIn("health-report", manifest["capabilities"])

    def test_weight_crud_baseline_and_validation(self) -> None:
        first = self.health.record_weight(80, "2026-07-01", "baseline")
        second = self.health.record_weight("78.25", "2026-07-15")
        comparison = self.health.weight_baseline_comparison()
        self.assertEqual(comparison["change_kg"], -1.75)
        updated = self.health.update_weight(second["record_id"], weight_kg=77.5, note="updated")
        self.assertEqual(updated["weight_kg"], 77.5)
        self.assertTrue(self.health.delete_weight(first["record_id"]))
        self.assertEqual(len(self.health.list_weights()), 1)
        with self.assertRaises(ValueError):
            self.health.record_weight(float("nan"), "2026-07-01")
        with self.assertRaises(ValueError):
            self.health.record_weight(10, "2026-07-01")
        with self.assertRaises(KeyError):
            self.health.delete_weight("missing")

    def test_body_checkup_sleep_exercise_and_nutrition_engines(self) -> None:
        self.health.record_body_composition("2026-07-01", 30, 25, 24)
        self.health.record_body_composition("2026-07-15", 31, 23, 23.5)
        body = self.health.body_composition_baseline_comparison()
        self.assertEqual(body["changes"]["skeletal_muscle_kg"], 1.0)
        self.assertEqual(body["changes"]["body_fat_percent"], -2.0)
        self.health.record_health_checkup(
            "2026-07-01", "Annual", "Follow-up", "2026-08-01",
            {"glucose": 100, "cholesterol": 180},
        )
        self.health.record_health_checkup(
            "2026-07-15", "Review", "Improved", metrics={"glucose": 95, "cholesterol": 170}
        )
        self.assertEqual(self.health.health_checkup_baseline_comparison()["metric_changes"]["glucose"], -5.0)
        sleep = self.health.record_sleep("2026-07-01T23:00:00+09:00", "2026-07-02T07:00:00+09:00", 2)
        self.assertEqual(sleep["duration_minutes"], 480)
        self.health.record_exercise("2026-07-02", "Run", 30, 1)
        self.health.record_exercise("2026-07-03", "Run", 45, 1)
        self.assertEqual(self.health.exercise_statistics()["duration_minutes"], 75)
        goal = self.health.create_health_goal("Cut", "2026-07-01", 75, 20)
        meal = self.health.record_nutrition("2026-07-02", "Dinner", "Balanced", goal["goal_id"])
        self.assertEqual(meal["goal_id"], goal["goal_id"])
        with self.assertRaises(KeyError):
            self.health.record_nutrition("2026-07-03", "Lunch", "Note", "missing")

    def test_trend_goal_and_report_engines(self) -> None:
        self.health.record_weight(80, "2026-07-01")
        self.health.record_weight(77.5, "2026-07-15")
        self.health.record_body_composition("2026-07-01", 30, 25, 24)
        self.health.record_body_composition("2026-07-15", 31, 22, 23)
        self.health.record_sleep("2026-07-01T23:00:00+09:00", "2026-07-02T06:00:00+09:00", 3)
        self.health.record_exercise("2026-07-02", "Walk", 40)
        goal = self.health.create_health_goal("Target", "2026-07-01", 75, 20)
        self.assertEqual(self.health.weight_trend()["change"], -2.5)
        self.assertEqual(self.health.inbody_trend()["body_fat_percent"]["change"], -3.0)
        self.assertEqual(self.health.sleep_trend()["duration_minutes"]["average"], 420.0)
        self.assertEqual(self.health.exercise_trend()["duration_minutes"], 40)
        progress = self.health.health_goal_progress(goal["goal_id"])
        self.assertEqual(progress["metrics"]["weight"]["progress_percent"], 50.0)
        daily = self.health.daily_report("2026-07-02")
        weekly = self.health.weekly_report("2026-07-07")
        monthly = self.health.monthly_report("2026-07")
        self.assertEqual(daily["period"]["kind"], "daily")
        self.assertEqual(weekly["period"]["start_on"], "2026-07-01")
        self.assertEqual(monthly["exercise"]["duration_minutes"], 40)
        self.assertIn("medical_notice", monthly)

    def test_migration_dry_run_transaction_idempotence_and_checksum(self) -> None:
        source = self.root / "legacy_health.json"
        source.write_text(json.dumps({
            "weights": [{"measured_on": "2026-07-01", "weight_kg": 80}],
            "body_compositions": [{"measured_on": "2026-07-01", "skeletal_muscle_kg": 30, "body_fat_percent": 25, "bmi": 24}],
            "health_checkups": [{"checked_on": "2026-07-01", "title": "Annual", "assessment": "Normal", "metrics": {"glucose": 95}}],
            "sleep": [{"bedtime": "2026-07-01T23:00:00+09:00", "wake_time": "2026-07-02T07:00:00+09:00", "fatigue": 2}],
            "exercise": [{"exercised_on": "2026-07-01", "activity": "Walk", "duration_minutes": 30}],
            "nutrition": [{"eaten_on": "2026-07-01", "meal_type": "Dinner", "note": "Balanced", "goal_id": "legacy-goal"}],
            "goals": [{"goal_id": "legacy-goal", "name": "Target", "start_on": "2026-07-01", "target_weight_kg": 75}],
        }), encoding="utf-8")
        original = source.read_bytes()
        dry = self.health.dry_run_legacy_json(source)
        self.assertTrue(dry["dry_run"])
        self.assertEqual(dry["accepted"]["weights"], 1)
        self.assertFalse(self.database.exists())
        self.assertEqual(source.read_bytes(), original)
        first = self.health.migrate_legacy_json(source)
        second = self.health.migrate_legacy_json(source)
        self.assertFalse(first["already_migrated"])
        self.assertTrue(second["already_migrated"])
        self.assertEqual(len(self.health.list_weights()), 1)
        self.assertEqual(len(self.health.list_health_checkups()), 1)
        self.assertEqual(len(self.health.list_sleep()), 1)
        self.assertEqual(len(self.health.list_exercise()), 1)
        self.assertEqual(len(self.health.list_nutrition()), 1)
        self.assertEqual(len(self.health.list_health_goals()), 1)
        source.write_text('{"weights": []}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.health.migrate_legacy_json(source)

    def test_invalid_migration_has_no_partial_state(self) -> None:
        source = self.root / "invalid.json"
        source.write_text(json.dumps({
            "weights": [{"measured_on": "2026-07-01", "weight_kg": 80}],
            "exercise": [{"exercised_on": "invalid", "activity": "Walk", "duration_minutes": 30}],
        }), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.health.migrate_legacy_json(source)
        self.assertFalse(self.database.exists())

    def test_privacy_manifest_gitignore_and_domain_boundaries(self) -> None:
        manifest = next(item for item in V13_STABLE_MANIFESTS if item.module_id == "health")
        self.assertEqual(manifest.privacy_class, "sensitive")
        repository = Path(__file__).resolve().parent.parent
        self.assertIn("data/health/", (repository / ".gitignore").read_text(encoding="utf-8"))
        violations: list[str] = []
        forbidden = {"finance", "vehicle", "housing", "investment", "job", "personal_growth"}
        for path in (repository / "subsystems" / "health").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                if module and module.startswith("subsystems.") and module.split(".")[1] in forbidden:
                    violations.append(str(path.relative_to(repository)))
        self.assertEqual(violations, [])
        engine_imports: list[str] = []
        for path in (repository / "subsystems").rglob("*.py"):
            if path.is_relative_to(repository / "subsystems" / "health"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("subsystems.health.engines"):
                    engine_imports.append(str(path.relative_to(repository)))
        self.assertEqual(engine_imports, [])


if __name__ == "__main__":
    unittest.main()
