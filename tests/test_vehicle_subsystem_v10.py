from __future__ import annotations

import ast
import sqlite3
import tempfile
import unittest
from pathlib import Path

import subsystems.vehicle as vehicle_package
from subsystems.operations.engines.catalog import V14_STABLE_MANIFESTS, V15_STABLE_MANIFESTS
from subsystems.vehicle import VehicleSubsystem


class VehicleSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / "vehicle.sqlite3"
        self.vehicle = VehicleSubsystem(self.root, self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def create_vehicle(self, name: str = "Daily Car") -> dict[str, object]:
        return self.vehicle.create_vehicle(name, "Maker", "Model", 2024, "hybrid")

    def test_public_interface_lazy_storage_and_manifest(self) -> None:
        self.assertEqual(vehicle_package.__all__, ["VehicleSubsystem"])
        self.assertFalse(self.database.exists())
        self.assertEqual(self.vehicle.health()["status"], "ready")
        self.assertEqual(self.vehicle.list_vehicles(), [])
        self.assertEqual(self.vehicle.export_snapshot()["vehicles"], [])
        self.assertFalse(self.database.exists())
        manifest = self.vehicle.interface_manifest()
        self.assertEqual(manifest["privacy_class"], "sensitive")
        self.assertIn("vehicle-report", manifest["capabilities"])
        second = VehicleSubsystem(self.root, self.root / "second.sqlite3")
        self.create_vehicle()
        self.assertEqual(second.list_vehicles(), [])

    def test_vehicle_lifecycle_validation_and_filtering(self) -> None:
        first = self.create_vehicle()
        self.assertEqual(self.vehicle.get_vehicle(first["vehicle_id"])["display_name"], "Daily Car")
        updated = self.vehicle.update_vehicle(first["vehicle_id"], display_name="Updated", powertrain="electric")
        self.assertEqual(updated["powertrain"], "electric")
        archived = self.vehicle.archive_vehicle(first["vehicle_id"])
        self.assertEqual(archived["status"], "archived")
        self.assertEqual(self.vehicle.list_vehicles("active"), [])
        self.assertEqual(len(self.vehicle.list_vehicles("archived")), 1)
        with self.assertRaises(ValueError):
            self.vehicle.create_vehicle("")
        with self.assertRaises(ValueError):
            self.vehicle.create_vehicle("Old", model_year=1885)
        with self.assertRaises(ValueError):
            self.vehicle.update_vehicle(first["vehicle_id"], unsupported=True)
        with self.assertRaises(KeyError):
            self.vehicle.get_vehicle("missing")

    def test_odometer_chronology_backfill_and_validation(self) -> None:
        vehicle = self.create_vehicle()
        vehicle_id = vehicle["vehicle_id"]
        self.vehicle.record_odometer(vehicle_id, 100, "2026-01-01")
        self.vehicle.record_odometer(vehicle_id, 300, "2026-03-01")
        self.vehicle.record_odometer(vehicle_id, 200, "2026-02-01")
        self.vehicle.record_odometer(vehicle_id, 300, "2026-04-01")
        self.assertEqual(
            [item["odometer_km"] for item in self.vehicle.list_odometer_readings(vehicle_id)],
            [100, 200, 300, 300],
        )
        with self.assertRaises(ValueError):
            self.vehicle.record_odometer(vehicle_id, 50, "2026-02-15")
        with self.assertRaises(ValueError):
            self.vehicle.record_odometer(vehicle_id, 400, "2026-02-15")
        with self.assertRaises(ValueError):
            self.vehicle.record_odometer(vehicle_id, -1, "2026-05-01")

    def test_maintenance_schedule_due_and_completion(self) -> None:
        vehicle = self.create_vehicle()
        vehicle_id = vehicle["vehicle_id"]
        self.vehicle.record_odometer(vehicle_id, 5000, "2026-07-01")
        by_date = self.vehicle.create_maintenance_schedule(
            vehicle_id, "Inspection", due_on="2026-07-10"
        )
        by_km = self.vehicle.create_maintenance_schedule(
            vehicle_id, "Oil", due_odometer_km=5000
        )
        due = self.vehicle.due_maintenance(vehicle_id, "2026-07-16")
        self.assertEqual({item["schedule_id"] for item in due}, {by_date["schedule_id"], by_km["schedule_id"]})
        maintenance = self.vehicle.record_maintenance(
            vehicle_id, "Oil", "2026-07-16", 5000, 50000, "Garage"
        )
        completed = self.vehicle.complete_maintenance_schedule(
            by_km["schedule_id"], maintenance["maintenance_id"]
        )
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(len(self.vehicle.list_maintenance_records(vehicle_id)), 1)
        with self.assertRaises(ValueError):
            self.vehicle.create_maintenance_schedule(vehicle_id, "Missing criteria")

    def test_energy_cost_filters_and_deterministic_report(self) -> None:
        vehicle = self.create_vehicle()
        vehicle_id = vehicle["vehicle_id"]
        self.vehicle.record_odometer(vehicle_id, 1000, "2026-01-01")
        self.vehicle.record_odometer(vehicle_id, 1100, "2026-02-01")
        fuel = self.vehicle.record_energy(
            vehicle_id, "fuel", "2026-01-15", "30.125", 60000, 1050
        )
        self.vehicle.record_energy(vehicle_id, "charge", "2026-02-01", 10, 10000, 1100)
        self.vehicle.record_maintenance(vehicle_id, "Inspection", "2026-02-01", 1100, 30000)
        self.assertEqual(fuel["quantity_milliunits"], 30125)
        self.assertEqual(len(self.vehicle.list_energy_logs(vehicle_id, energy_type="fuel")), 1)
        report = self.vehicle.vehicle_report(vehicle_id, "2026-01-01", "2026-12-31", "2026-02-01")
        self.assertEqual(report["distance_km"], 100)
        self.assertEqual(report["energy_cost"], 70000)
        self.assertEqual(report["maintenance_cost"], 30000)
        self.assertEqual(report["operating_cost"], 100000)
        self.assertEqual(report["fuel_milliunits"], 30125)
        with self.assertRaises(ValueError):
            self.vehicle.record_energy(vehicle_id, "fuel", "2026-03-01", "1.0001")

    def test_transaction_integrity_health_and_export(self) -> None:
        vehicle = self.create_vehicle()
        vehicle_id = vehicle["vehicle_id"]
        self.vehicle.record_odometer(vehicle_id, 100, "2026-01-01")
        with self.assertRaises(sqlite3.IntegrityError):
            self.vehicle.record_odometer(vehicle_id, 100, "2026-01-01")
        self.assertEqual(len(self.vehicle.list_odometer_readings(vehicle_id)), 1)
        connection = sqlite3.connect(self.database)
        try:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            connection.close()
        self.assertEqual(self.vehicle.health()["status"], "healthy")
        snapshot = self.vehicle.export_snapshot()
        self.assertEqual(len(snapshot["vehicles"]), 1)
        self.assertEqual(len(snapshot["odometer_readings"]), 1)

    def test_privacy_catalog_and_domain_boundaries(self) -> None:
        self.assertNotIn("vehicle", {item.module_id for item in V14_STABLE_MANIFESTS})
        manifest = next(item for item in V15_STABLE_MANIFESTS if item.module_id == "vehicle")
        self.assertEqual(manifest.privacy_class, "sensitive")
        repository = Path(__file__).resolve().parent.parent
        self.assertIn("data/vehicle/", (repository / ".gitignore").read_text(encoding="utf-8"))
        forbidden = {"finance", "health", "housing", "compatibility", "investment", "job"}
        violations: list[str] = []
        for path in (repository / "subsystems" / "vehicle").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                if module and module.startswith("subsystems.") and module.split(".")[1] in forbidden:
                    violations.append(str(path.relative_to(repository)))
        self.assertEqual(violations, [])
        engine_imports: list[str] = []
        for path in (repository / "subsystems").rglob("*.py"):
            if path.is_relative_to(repository / "subsystems" / "vehicle"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if (isinstance(node, ast.ImportFrom) and node.module
                        and node.module.startswith("subsystems.vehicle.engines")):
                    engine_imports.append(str(path.relative_to(repository)))
        self.assertEqual(engine_imports, [])


if __name__ == "__main__":
    unittest.main()
