from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path

from subsystems.database import DatabaseSubsystem
from subsystems.finance import FinanceSubsystem
from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.release_gate import evaluate_release_gate
from subsystems.foundation.engines.runtime_config import (
    RuntimeConfigurationError,
    RuntimeStorageConfig,
)
from subsystems.foundation.engines.version import PRODUCT_VERSION
from subsystems.operations.engines.catalog import V20_STABLE_MANIFESTS
from subsystems.operations.engines.reports import ReportsService


ROOT = Path(__file__).resolve().parents[1]


class RuntimeStorageTests(unittest.TestCase):
    def test_development_defaults_preserve_existing_paths(self) -> None:
        config = RuntimeStorageConfig.from_environment(ROOT, {})
        self.assertEqual(config.environment, "development")
        self.assertEqual(config.data_root, ROOT / "data")
        self.assertEqual(config.backup_root, ROOT / "backups")
        self.assertFalse(config.authentication_required)
        with self.assertRaises(RuntimeConfigurationError):
            config.component_database_path("../outside")
        with self.assertRaises(RuntimeConfigurationError):
            config.component_database_path("finance/nested")

    def test_production_rejects_ephemeral_nested_and_unauthenticated_storage(self) -> None:
        with self.assertRaises(RuntimeConfigurationError):
            RuntimeStorageConfig.from_environment(ROOT, {"LIVING_OS_ENV": "production"})
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            with self.assertRaises(RuntimeConfigurationError):
                RuntimeStorageConfig.from_environment(
                    ROOT,
                    {
                        "LIVING_OS_ENV": "production",
                        "LIVING_OS_DATA_ROOT": str(temporary / "data"),
                        "LIVING_OS_BACKUP_ROOT": str(temporary / "backup"),
                        "LIVING_OS_STORAGE_DURABILITY": "durable",
                        "LIVING_OS_BACKUP_INDEPENDENT": "true",
                        "LIVING_OS_REQUIRE_AUTH": "true",
                    },
                )

    def test_release_gate_requires_all_production_conditions_and_owner_security(self) -> None:
        drive = Path(ROOT.anchor or "/")
        config = RuntimeStorageConfig.from_environment(
            ROOT,
            {
                "LIVING_OS_ENV": "production",
                "LIVING_OS_DATA_ROOT": str(drive / "living-os-v205-data"),
                "LIVING_OS_BACKUP_ROOT": str(drive / "living-os-v205-backup"),
                "LIVING_OS_STORAGE_DURABILITY": "durable",
                "LIVING_OS_BACKUP_INDEPENDENT": "true",
                "LIVING_OS_REQUIRE_AUTH": "true",
            },
        )
        blocked = evaluate_release_gate(config, owner_security_configured=False)
        self.assertFalse(blocked.passed)
        self.assertIn("owner_security_configured", blocked.failures)
        self.assertTrue(
            evaluate_release_gate(config, owner_security_configured=True).passed
        )

    def test_restart_persistence_and_backup_recovery_use_configured_roots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "checkout"
            repository.mkdir()
            config = RuntimeStorageConfig(
                repository_root=repository,
                environment="test",
                data_root=root / "persistent-data",
                backup_root=root / "independent-backup",
                durability="test-persistent",
                backup_independent=True,
                authentication_required=False,
            )
            config.validate()
            first = LivingHub(repository, config)
            first.bootstrap(V20_STABLE_MANIFESTS)
            first.database.create(
                "test", "persistence", "one", {"value": "before"}, actor="test"
            )
            backup = first.database.create_backup(actor="test")
            first.database.update(
                "test",
                "persistence",
                "one",
                {"value": "after"},
                expected_version=1,
                actor="test",
            )

            restarted = LivingHub(repository, config)
            restarted.bootstrap(V20_STABLE_MANIFESTS)
            self.assertEqual(
                restarted.database.read("test", "persistence", "one")["value"],
                "after",
            )
            result = restarted.database.restore(backup, actor="test")
            self.assertEqual(result["recovery_result"], "NOT_REQUIRED")

            verified_restart = LivingHub(repository, config)
            verified_restart.bootstrap(V20_STABLE_MANIFESTS)
            self.assertEqual(
                verified_restart.database.read("test", "persistence", "one")["value"],
                "before",
            )
            self.assertTrue(backup.is_relative_to(config.backup_root))
            self.assertTrue(
                verified_restart.store.database_path.is_relative_to(config.data_root)
            )


class ExecutionDatabaseV205Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = DatabaseSubsystem(
            self.root / "data" / "living_os.sqlite3",
            self.root / "backups",
            self.root,
        )
        self.database.initialize(apply_migrations=True, actor="test")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_extended_execution_contract_is_persisted(self) -> None:
        self.database.executions.record(
            "TEST",
            "retry",
            "target",
            "COMPLETED",
            actor="test",
            retry_count=2,
            recovery_result="RETRIED_SUCCEEDED",
            validation_result="PASSED",
            failure_context={"attempt": 3},
        )
        record = self.database.execution_records(1)[0]
        self.assertEqual(record["retry_count"], 2)
        self.assertEqual(record["recovery_result"], "RETRIED_SUCCEEDED")
        self.assertEqual(record["product_version"], PRODUCT_VERSION)
        self.assertEqual(record["validation_result"], "PASSED")
        self.assertEqual(record["failure_context"], {"attempt": 3})
        self.assertTrue(record["recorded_at"])
        self.assertIsInstance(record["duration_ms"], int)

    def test_domain_validation_failure_is_not_dropped(self) -> None:
        finance = FinanceSubsystem(
            self.root,
            self.root / "data" / "finance.sqlite3",
            database_foundation=self.database,
        )
        with self.assertRaises(ValueError):
            finance.record_income(-1, "", "invalid-date")
        record = next(
            item
            for item in self.database.execution_records(50)
            if item["action"] == "record_income"
        )
        self.assertEqual(record["status"], "FAILED")
        self.assertEqual(record["validation_result"], "FAILED")
        self.assertEqual(record["product_version"], PRODUCT_VERSION)
        self.assertEqual(record["failure_context"]["operation"], "record_income")


class HealthUIAndDocumentationTests(unittest.TestCase):
    def test_existing_health_backend_capabilities_are_connected_to_ui(self) -> None:
        source = (
            ROOT / "subsystems" / "experience" / "engines" / "pages.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        render_health = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "render_health"
        )
        calls = {
            node.func.attr
            for node in ast.walk(render_health)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertTrue(
            {
                "record_health_checkup",
                "record_exercise",
                "record_nutrition",
                "update_weight",
                "delete_weight",
                "body_composition_baseline_comparison",
                "health_checkup_follow_ups",
                "health_goal_progress",
                "weight_trend",
                "inbody_trend",
                "sleep_trend",
                "exercise_trend",
                "daily_report",
                "weekly_report",
                "monthly_report",
            }.issubset(calls)
        )

    def test_design_docs_and_reading_order_are_complete(self) -> None:
        ui_root = ROOT / "docs" / "ui"
        required = (
            "OFFICIAL_DESIGN_BIBLE.md",
            "VISUAL_LANGUAGE.md",
            "INTERACTION_GUIDELINE.md",
            "KOREAN_UI_GUIDELINE.md",
            "RESPONSIVE_ACCESSIBILITY_GUIDELINE.md",
            "CONCEPT_ART/README.md",
        )
        readme = (ui_root / "README.md").read_text(encoding="utf-8")
        positions = []
        for relative in required:
            self.assertTrue((ui_root / relative).is_file(), relative)
            positions.append(readme.index(relative))
        self.assertEqual(positions, sorted(positions))

    def test_active_version_and_generated_report_are_v205(self) -> None:
        self.assertEqual(PRODUCT_VERSION, "v2.0.9.6")
        self.assertIn("Living OS v2.0.9.6", (ROOT / "VERSION.md").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hub = LivingHub(root)
            hub.bootstrap(V20_STABLE_MANIFESTS)
            self.assertIn(
                "- Version: Living OS v2.0.9.6",
                ReportsService(hub).build("daily"),
            )


if __name__ == "__main__":
    unittest.main()
