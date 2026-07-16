from __future__ import annotations

import ast
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import subsystems.housing as housing_package
from subsystems.compatibility.engines.housing import calculate_housing_candidate
from subsystems.housing import HousingSubsystem
from subsystems.operations.engines.catalog import V13_STABLE_MANIFESTS, V14_STABLE_MANIFESTS


class HousingSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / "housing.sqlite3"
        self.housing = HousingSubsystem(self.root, self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def values(self, name: str = "Candidate A", **changes: object) -> dict[str, object]:
        values: dict[str, object] = {
            "name": name,
            "deposit": 10_000_000,
            "monthly_rent": 600_000,
            "maintenance_fee": 100_000,
            "maintenance_fee_provided": True,
            "commute_minutes": 30,
            "parking_available": True,
            "options_memo": "Elevator",
            "special_notes": "Review contract",
        }
        values.update(changes)
        return values

    def test_public_interface_lazy_storage_and_manifest(self) -> None:
        self.assertEqual(housing_package.__all__, ["HousingSubsystem"])
        self.assertFalse(self.database.exists())
        self.assertEqual(self.housing.health()["status"], "ready")
        self.assertEqual(self.housing.list_candidates(), [])
        self.assertEqual(self.housing.housing_report()["candidate_count"], 0)
        self.assertFalse(self.database.exists())
        second = HousingSubsystem(self.root, self.root / "second.sqlite3")
        self.housing.create_candidate(**self.values())
        self.assertEqual(second.list_candidates(), [])
        manifest = self.housing.interface_manifest()
        self.assertEqual(manifest["privacy_class"], "sensitive")
        self.assertIn("housing-report", manifest["capabilities"])

    def test_scoring_matches_legacy_contract(self) -> None:
        cases = (
            self.values(),
            self.values(monthly_rent=1_300_000, maintenance_fee=0, commute_minutes=80,
                        parking_available=False, maintenance_fee_provided=False),
        )
        for values in cases:
            legacy = calculate_housing_candidate(**values)
            current = self.housing.calculate_candidate(**values)
            for field in ("total_monthly_cost", "score", "grade", "deductions"):
                self.assertEqual(current[field], legacy[field])

    def test_candidate_crud_validation_and_recalculation(self) -> None:
        first = self.housing.create_candidate(**self.values())
        self.assertEqual(self.housing.get_candidate(first["candidate_id"])["name"], "Candidate A")
        updated = self.housing.update_candidate(
            first["candidate_id"], monthly_rent=900_000, status="shortlisted"
        )
        self.assertEqual(updated["total_monthly_cost"], 1_000_000)
        self.assertEqual(updated["status"], "shortlisted")
        self.assertTrue(self.housing.delete_candidate(first["candidate_id"]))
        self.assertEqual(self.housing.list_candidates(), [])
        with self.assertRaises(ValueError):
            self.housing.create_candidate(**self.values(deposit=-1))
        with self.assertRaises(ValueError):
            self.housing.create_candidate(**self.values(name=""))
        with self.assertRaises(KeyError):
            self.housing.get_candidate("missing")

    def test_comparison_ranking_and_report(self) -> None:
        lower = self.housing.create_candidate(
            **self.values("Long commute", commute_minutes=80, parking_available=False)
        )
        higher = self.housing.create_candidate(
            **self.values("Near home", monthly_rent=500_000, commute_minutes=10), status="shortlisted"
        )
        ranking = self.housing.rank_candidates()
        self.assertEqual(ranking[0]["candidate_id"], higher["candidate_id"])
        self.assertEqual(ranking[1]["candidate_id"], lower["candidate_id"])
        report = self.housing.housing_report()
        self.assertEqual(report["candidate_count"], 2)
        self.assertEqual(report["best_candidate"]["name"], "Near home")
        self.assertEqual(report["status_distribution"]["shortlisted"], 1)
        self.assertIn("Review the leading shortlisted candidate", report["next_actions"][0])

    def test_migration_dry_run_transaction_idempotence_and_checksum(self) -> None:
        source = self.root / "housing_candidates.json"
        legacy = calculate_housing_candidate(**self.values("Legacy home"))
        legacy.update({"id": "legacy-1", "created_at": "2026-07-01T00:00:00+09:00"})
        source.write_text(json.dumps({"candidates": [legacy]}), encoding="utf-8")
        original = source.read_bytes()
        original_hash = hashlib.sha256(original).hexdigest()
        unreviewed = HousingSubsystem(self.root, self.root / "unreviewed.sqlite3")
        with self.assertRaises(ValueError):
            unreviewed.migrate_legacy_json(source)
        self.assertFalse(unreviewed.database_path.exists())
        dry = self.housing.dry_run_legacy_json(source)
        self.assertTrue(dry["dry_run"])
        self.assertEqual(dry["accepted"]["candidates"], 1)
        self.assertFalse(self.database.exists())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), original_hash)
        first = self.housing.migrate_legacy_json(source)
        second = self.housing.migrate_legacy_json(source)
        self.assertFalse(first["already_migrated"])
        self.assertTrue(second["already_migrated"])
        self.assertEqual(self.housing.list_candidates()[0]["candidate_id"], "legacy-1")
        source.write_text('{"candidates": []}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.housing.migrate_legacy_json(source)

    def test_invalid_migration_has_no_partial_state(self) -> None:
        source = self.root / "invalid.json"
        source.write_text(json.dumps({"candidates": [self.values("Valid"), self.values("Invalid", deposit=-1)]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.housing.dry_run_legacy_json(source)
        with self.assertRaises(ValueError):
            self.housing.migrate_legacy_json(source)
        self.assertFalse(self.database.exists())

    def test_integrity_privacy_catalog_and_domain_boundaries(self) -> None:
        self.housing.create_candidate(**self.values())
        connection = sqlite3.connect(self.database)
        try:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            connection.close()
        self.assertNotIn("housing", {item.module_id for item in V13_STABLE_MANIFESTS})
        manifest = next(item for item in V14_STABLE_MANIFESTS if item.module_id == "housing")
        self.assertEqual(manifest.privacy_class, "sensitive")
        repository = Path(__file__).resolve().parent.parent
        self.assertIn("data/housing/", (repository / ".gitignore").read_text(encoding="utf-8"))
        forbidden = {"finance", "health", "vehicle", "investment", "job", "personal_growth"}
        violations: list[str] = []
        for path in (repository / "subsystems" / "housing").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                if module and module.startswith("subsystems.") and module.split(".")[1] in forbidden:
                    violations.append(str(path.relative_to(repository)))
        self.assertEqual(violations, [])
        engine_imports: list[str] = []
        for path in (repository / "subsystems").rglob("*.py"):
            if path.is_relative_to(repository / "subsystems" / "housing"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("subsystems.housing.engines"):
                    engine_imports.append(str(path.relative_to(repository)))
        self.assertEqual(engine_imports, [])


if __name__ == "__main__":
    unittest.main()
