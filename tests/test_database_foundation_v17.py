from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from subsystems.database import DatabaseSubsystem
from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.database.engines.contracts import IntegrityResult
from subsystems.database.engines.migrations import DatabaseMigration, MigrationRegistry
from subsystems.database_management import DatabaseManagementSubsystem
from subsystems.finance import FinanceSubsystem
from subsystems.food import FoodSubsystem
from subsystems.health import HealthSubsystem
from subsystems.housing import HousingSubsystem
from subsystems.vehicle import VehicleSubsystem
from subsystems.foundation.engines.errors import ConcurrencyError


class DatabaseFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database_path = self.root / "data" / "hub" / "living_os.sqlite3"
        self.database = DatabaseSubsystem(
            self.database_path,
            self.root / "backups" / "v1.7" / "database",
            self.root,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def initialize(self) -> None:
        result = self.database.initialize(apply_migrations=True, actor="test")
        self.assertEqual(result["schema_version"], 3)

    def test_initialization_is_idempotent_and_creates_required_schema(self) -> None:
        self.initialize()
        second = self.database.initialize(apply_migrations=True, actor="test")
        self.assertEqual(second["applied_migrations"], [])
        registry = self.database.schema_registry()
        self.assertIn("execution_records", registry["tables"])
        self.assertIn("backup_history", registry["tables"])
        self.assertIn("ix_records_status", registry["indexes"])
        self.assertEqual(self.database.pending_migrations(), [])

    def test_crud_search_archive_and_optimistic_concurrency(self) -> None:
        self.initialize()
        created = self.database.create(
            "test", "note", "one", {"title": "First", "body": "alpha"}, actor="test"
        )
        self.assertEqual(created["_version"], 1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.database.create(
                "test", "note", "one", {"title": "Duplicate"}, actor="test"
            )
        self.assertEqual(self.database.read("test", "note", "one")["title"], "First")
        updated = self.database.update(
            "test",
            "note",
            "one",
            {"title": "Second", "body": "beta"},
            expected_version=1,
            actor="test",
        )
        self.assertEqual(updated["_version"], 2)
        self.assertEqual(self.database.search("test", "note", "beta")[0]["id"], "one")
        with self.assertRaises(ConcurrencyError):
            self.database.update(
                "test", "note", "one", {"title": "stale"}, expected_version=1, actor="test"
            )
        archived = self.database.archive(
            "test", "note", "one", expected_version=2, actor="test"
        )
        self.assertEqual(archived["_status"], "ARCHIVED")
        self.assertEqual(self.database.list("test", "note"), [])
        self.assertEqual(len(self.database.list("test", "note", include_archived=True)), 1)

    def test_transaction_rolls_back_all_writes(self) -> None:
        self.initialize()
        with self.assertRaises(RuntimeError):
            with self.database.transaction(actor="test") as connection:
                self.database.repository.create(
                    "test", "note", "rollback", {"title": "temporary"}, connection=connection
                )
                raise RuntimeError("forced failure")
        self.assertIsNone(self.database.read("test", "note", "rollback"))
        latest = self.database.execution_records(1)[0]
        self.assertEqual(latest["action"], "transaction")
        self.assertEqual(latest["status"], "FAILED")

    def test_failed_migration_rolls_back_and_records_failure(self) -> None:
        self.initialize()
        registry = MigrationRegistry(
            SQLiteConnectionLayer(self.database_path),
            (
                DatabaseMigration(
                    4,
                    "forced_failure",
                    (
                        "CREATE TABLE should_rollback(id INTEGER PRIMARY KEY)",
                        "INSERT INTO table_that_does_not_exist VALUES(1)",
                    ),
                ),
            ),
        )
        with self.assertRaises(sqlite3.Error):
            registry.apply_pending(execution_id="test-execution")
        with self.database.connections.connection(read_only=True) as connection:
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='should_rollback'"
            ).fetchone()
        self.assertIsNone(table)
        self.assertEqual(registry.failures()[0]["version"], 4)
        self.assertEqual(self.database.current_schema_version(), 3)

    def test_backup_restore_and_failure_recording(self) -> None:
        self.initialize()
        self.database.create("test", "note", "one", {"value": "before"}, actor="test")
        backup = self.database.create_backup(actor="test")
        self.assertTrue(backup.is_file())
        self.assertTrue(self.database.validate_restore(backup).valid)
        self.database.update(
            "test", "note", "one", {"value": "after"}, expected_version=1, actor="test"
        )
        result = self.database.restore(backup, actor="test")
        self.assertTrue(Path(result["safety_backup_path"]).is_file())
        self.assertEqual(self.database.read("test", "note", "one")["value"], "before")
        self.assertEqual(self.database.restore_history()[0]["status"], "COMPLETED")
        actions = [item["action"] for item in self.database.execution_records(100)]
        self.assertIn("backup_create", actions)
        self.assertIn("restore", actions)

        self.database.update(
            "test", "note", "one", {"value": "current"}, expected_version=1, actor="test"
        )
        invalid_result = IntegrityResult("DEGRADED", "ok", 0, ("required_table",), (), 2)
        with patch.object(self.database.integrity, "check", return_value=invalid_result):
            with self.assertRaises(ValueError):
                self.database.restore(backup, actor="test")
        self.assertEqual(self.database.read("test", "note", "one")["value"], "current")

        with patch.object(self.database.backups, "create", side_effect=OSError("denied")):
            with self.assertRaises(OSError):
                self.database.create_backup(actor="test")
        latest = self.database.execution_records(1)[0]
        self.assertEqual(latest["action"], "backup_create")
        self.assertEqual(latest["status"], "FAILED")
        self.assertEqual(latest["error_code"], "OSError")

        with patch.object(self.database.backups, "restore", side_effect=OSError("denied")):
            with self.assertRaises(OSError):
                self.database.restore(backup, actor="test")
        latest = self.database.execution_records(1)[0]
        self.assertEqual(latest["action"], "restore")
        self.assertEqual(latest["status"], "FAILED")

    def test_integrity_detects_corruption_and_missing_path(self) -> None:
        missing = DatabaseSubsystem(
            self.root / "missing" / "db.sqlite3",
            self.root / "missing-backups",
            self.root,
        )
        self.assertEqual(missing.integrity_check(record=False).status, "FAILED")
        corrupt_path = self.root / "corrupt.sqlite3"
        corrupt_path.write_bytes(b"not-a-sqlite-database")
        corrupt = DatabaseSubsystem(corrupt_path, self.root / "corrupt-backups", self.root)
        management = DatabaseManagementSubsystem(corrupt)
        self.assertEqual(management.health_check()["status"], "FAILED")
        directory_path = self.root / "directory-instead-of-database"
        directory_path.mkdir()
        invalid = DatabaseSubsystem(directory_path, self.root / "invalid-backups", self.root)
        with self.assertRaises(sqlite3.OperationalError):
            invalid.initialize(apply_migrations=True, actor="test")


class DatabaseManagementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = DatabaseSubsystem(
            self.root / "data" / "hub" / "living_os.sqlite3",
            self.root / "backups" / "v1.7" / "database",
            self.root,
        )
        self.management = DatabaseManagementSubsystem(self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_health_warning_migration_registry_and_healthy_status(self) -> None:
        self.database.initialize(apply_migrations=False)
        before = self.management.health_check()
        self.assertEqual(before["status"], "WARNING")
        self.assertEqual(before["migration_status"], "PENDING")
        applied = self.management.request_migration(actor="test")
        self.assertEqual(applied[0]["version"], 2)
        after = self.management.health_check(record=True, actor="test")
        self.assertEqual(after["status"], "HEALTHY")
        registry = self.management.schema_registry()
        self.assertEqual(registry["schema_version"], 3)
        self.assertEqual(self.management.migration_status()["pending"], [])

    def test_backup_listing_restore_preflight_and_management_report(self) -> None:
        self.database.initialize(apply_migrations=True, actor="test")
        backup = self.management.request_backup(actor="test")
        self.assertEqual(Path(self.management.backup_status()[0]["path"]), backup.resolve())
        self.assertTrue(self.management.preflight_restore(backup).valid)
        candidates = self.management.restore_candidates()
        self.assertTrue(any(candidate.path.resolve() == backup.resolve() for candidate in candidates))
        report = self.management.operational_report(record=True, actor="test")
        self.assertEqual(report["database_status"], "HEALTHY")
        self.assertEqual(report["schema_status"]["current"], 3)
        self.assertIn("recommendations", report)
        self.assertIn(
            "management_report",
            [item["action"] for item in self.database.execution_records(100)],
        )

    def test_capacity_warning_is_exposed_without_modifying_business_data(self) -> None:
        self.database.initialize(apply_migrations=True, actor="test")
        constrained = DatabaseManagementSubsystem(
            self.database,
            capacity_warning_bytes=1,
            degraded_check_ms=60_000,
        )
        health = constrained.health_check()
        self.assertEqual(health["status"], "WARNING")
        self.assertEqual(health["capacity_status"], "WARNING")
        report = constrained.operational_report()
        self.assertEqual(report["capacity_status"]["status"], "WARNING")

    def test_existing_subsystems_remain_independent_and_healthy(self) -> None:
        subsystems = (
            FinanceSubsystem(self.root, self.root / "finance.sqlite3"),
            HealthSubsystem(self.root, self.root / "health.sqlite3"),
            HousingSubsystem(self.root, self.root / "housing.sqlite3"),
            VehicleSubsystem(self.root, self.root / "vehicle.sqlite3"),
            FoodSubsystem(self.root, self.root / "food.sqlite3"),
        )
        for subsystem in subsystems:
            with self.subTest(subsystem=type(subsystem).__name__):
                health = subsystem.health()
                self.assertIn(health["status"], {"ready", "healthy"})
        self.assertFalse(any(self.root.glob("*.sqlite3")))


if __name__ == "__main__":
    unittest.main()
