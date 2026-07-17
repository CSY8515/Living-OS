from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from subsystems.database import DatabaseSubsystem
from subsystems.database.engines.component import (
    ALLOWED_COMPONENT_LAYERS,
    DatabaseIntegrationContract,
)
from subsystems.database_management import DatabaseManagementSubsystem
from subsystems.finance import FinanceSubsystem
from subsystems.food import FoodSubsystem
from subsystems.health import HealthSubsystem
from subsystems.housing import HousingSubsystem
from subsystems.vehicle import VehicleSubsystem


class DatabaseIntegrationV171Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = DatabaseSubsystem(
            self.root / "data" / "hub" / "living_os.sqlite3",
            self.root / "backups" / "v1.7.1" / "database",
            self.root,
        )
        self.database.initialize(apply_migrations=True, actor="test")
        self.management = DatabaseManagementSubsystem(self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def build_components(self) -> tuple[object, ...]:
        return (
            FinanceSubsystem(self.root, database_foundation=self.database),
            HealthSubsystem(self.root, database_foundation=self.database),
            VehicleSubsystem(self.root, database_foundation=self.database),
            HousingSubsystem(self.root, database_foundation=self.database),
            FoodSubsystem(self.root, database_foundation=self.database),
        )

    def test_all_existing_components_register_before_first_write(self) -> None:
        components = self.build_components()
        self.assertEqual(len(components), 5)
        registered = self.management.registered_components()
        self.assertEqual(
            {item["component_id"] for item in registered},
            {"SUB-FINANCE", "SUB-HEALTH", "SUB-VEHICLE", "SUB-HOUSING", "SUB-FOOD"},
        )
        self.assertTrue(all(item["integration_mode"] == "compatibility-adapter" for item in registered))
        self.assertTrue(all(not item["initialized"] for item in self.management.component_status()))

    def test_domain_writes_use_adapter_and_operational_execution_database(self) -> None:
        finance, health, vehicle, housing, food = self.build_components()
        finance.record_income(1000, "Salary", "2026-07-01")
        health.record_weight(80, "2026-07-01")
        vehicle.create_vehicle("Daily Car", "Maker", "Model", 2024, "hybrid")
        housing.create_candidate(
            name="Candidate", deposit=10_000_000, monthly_rent=600_000,
            maintenance_fee=100_000, maintenance_fee_provided=True,
            commute_minutes=30, parking_available=True,
            options_memo="Elevator", special_notes="Review",
        )
        food.create_ingredient("Rice", "grain", "100", "g")
        statuses = self.management.component_status()
        self.assertTrue(all(item["initialized"] for item in statuses))
        self.assertTrue(all(item["integrity"] == "ok" for item in statuses))
        actions = self.database.execution_records(1000)
        transaction_components = {
            item["subsystem"] for item in actions if item["action"] == "transaction"
        }
        self.assertEqual(
            transaction_components,
            {"SUB-FINANCE", "SUB-HEALTH", "SUB-VEHICLE", "SUB-HOUSING", "SUB-FOOD"},
        )

    def test_management_initializes_every_attached_component_schema(self) -> None:
        self.build_components()
        for component_id in (
            "SUB-FINANCE", "SUB-HEALTH", "SUB-VEHICLE", "SUB-HOUSING", "SUB-FOOD"
        ):
            status = self.management.request_component_initialization(
                component_id, actor="test"
            )
            self.assertEqual(status["status"], "HEALTHY")
            self.assertEqual(status["migration_status"], "CURRENT")
        self.assertTrue(all(item["initialized"] for item in self.management.component_status()))

    def test_component_backup_restore_is_verified_and_control_plane_only(self) -> None:
        finance = FinanceSubsystem(self.root, database_foundation=self.database)
        finance.record_income(1000, "Salary", "2026-07-01")
        backup = self.management.request_component_backup("SUB-FINANCE", actor="test")
        finance.record_expense(250, "Food", "2026-07-02")
        self.assertEqual(len(finance.list_transactions()), 2)
        result = self.management.request_component_restore(
            "SUB-FINANCE", backup, actor="test"
        )
        self.assertTrue(Path(result["safety_backup"]).is_file())
        self.assertEqual(len(finance.list_transactions()), 1)
        self.assertTrue(self.management.component_backups("SUB-FINANCE"))

    def test_contract_registry_covers_future_components_and_upper_layers(self) -> None:
        registry = json.loads(
            (Path(__file__).parents[1] / "config" / "database_integration_registry.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(set(registry["contract_required_layers"]), ALLOWED_COMPONENT_LAYERS)
        self.assertEqual(set(registry["required_future_components"]), set())
        self.assertTrue(
            {"SUB-PERSONAL-GROWTH", "SUB-COLLABORATION"}.issubset(registry["runtime_components"])
        )
        self.assertTrue({"SUB-INVESTMENT", "SUB-JOB"}.issubset(registry["runtime_components"]))
        self.assertTrue({"SUB-KNOWLEDGE", "SUB-ROUTINE"}.issubset(registry["runtime_components"]))
        template = json.loads(
            (Path(__file__).parents[1] / "config" / "templates" / "database_component.json").read_text(
                encoding="utf-8"
            )
        )
        for layer in ALLOWED_COMPONENT_LAYERS:
            contract = DatabaseIntegrationContract(
                **{**template, "component_id": f"TEST-{layer}", "layer": layer, "owner": "test"}
            )
            contract.validate()

    def test_component_storage_has_no_direct_sqlite_connection(self) -> None:
        repository = Path(__file__).parents[1]
        for name in ("finance", "health", "vehicle", "housing", "food"):
            source = (repository / "subsystems" / name / "engines" / "storage.py").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("import sqlite3", source)
            self.assertNotIn("sqlite3.connect", source)


if __name__ == "__main__":
    unittest.main()
