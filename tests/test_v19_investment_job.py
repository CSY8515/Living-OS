from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from subsystems.database import DatabaseSubsystem
from subsystems.database_management import DatabaseManagementSubsystem
from subsystems.investment import InvestmentSubsystem
from subsystems.investment.models import InvestmentRecord
from subsystems.job import JobSubsystem
from subsystems.job.models import JobRecord


class V19InvestmentJobTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = DatabaseSubsystem(
            self.root / "data/hub/living_os.sqlite3", self.root / "backups/v1.9/database", self.root
        )
        self.database.initialize(apply_migrations=True, actor="test")
        self.investment = InvestmentSubsystem(self.root, database_foundation=self.database)
        self.job = JobSubsystem(self.root, database_foundation=self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_models_reject_invalid_contracts(self) -> None:
        with self.assertRaises(ValueError):
            InvestmentRecord("", "").validate()
        with self.assertRaises(ValueError):
            InvestmentRecord("i", "Asset", quantity=-1).validate()
        with self.assertRaises(ValueError):
            JobRecord("j", "Company", "Role", status="UNKNOWN").validate()
        with self.assertRaises(ValueError):
            JobRecord("j", "Company", "Role", salary_min=2, salary_max=1).validate()

    def test_investment_crud_valuation_archive_and_management(self) -> None:
        created = self.investment.create(
            "Index ETF", investment_id="inv-1", asset_type="ETF", symbol="INDEX",
            quantity=10, unit_cost=100, current_price=120, currency="USD", status="ACTIVE",
        )
        self.assertEqual(self.investment.get(created["investment_id"])["symbol"], "INDEX")
        updated = self.investment.update_valuation(created["investment_id"], 125)
        self.assertEqual(updated["current_price"], 125)
        summary = self.investment.management_summary()
        self.assertEqual(summary["valuation_by_currency"]["USD"]["cost"], 1000)
        self.assertEqual(summary["valuation_by_currency"]["USD"]["value"], 1250)
        self.assertEqual(self.investment.archive(created["investment_id"])["status"], "ARCHIVED")
        self.assertEqual(self.investment.list(), [])

    def test_job_search_transition_due_actions_and_management(self) -> None:
        due = (date.today() - timedelta(days=1)).isoformat()
        created = self.job.create(
            "Example Corp", "Platform Engineer", job_id="job-1", location="Seoul",
            status="APPLIED", applied_on=date.today().isoformat(), next_action_on=due,
        )
        self.assertEqual(self.job.search("platform")[0]["job_id"], created["job_id"])
        self.assertEqual(self.job.management_summary()["due_actions"], 1)
        self.assertEqual(self.job.transition(created["job_id"], "INTERVIEW")["status"], "INTERVIEW")
        self.assertEqual(self.job.archive(created["job_id"])["status"], "ARCHIVED")

    def test_registry_execution_integrity_backup_and_restore(self) -> None:
        management = DatabaseManagementSubsystem(self.database)
        registered = {item["component_id"] for item in management.registered_components()}
        self.assertTrue({"SUB-INVESTMENT", "SUB-JOB"}.issubset(registered))
        registrations = {item["component_id"]: item for item in management.registered_components()}
        self.assertEqual(registrations["SUB-INVESTMENT"]["integration_mode"], "record-repository")
        self.assertEqual(registrations["SUB-JOB"]["integration_mode"], "record-repository")
        self.investment.create("Bond", investment_id="restore-me", asset_type="BOND")
        self.job.create("Company", "Role")
        actions = {(item["subsystem"], item["action"]) for item in self.database.execution_records(500)}
        self.assertIn(("SUB-INVESTMENT", "create"), actions)
        self.assertIn(("SUB-JOB", "create"), actions)
        statuses = {item["component_id"]: item for item in management.component_status()}
        self.assertEqual(statuses["SUB-INVESTMENT"]["integrity"], "ok")
        self.assertEqual(statuses["SUB-JOB"]["integrity"], "ok")
        backup = management.request_component_backup("SUB-INVESTMENT", actor="test")
        self.investment.update("restore-me", name="Changed")
        management.request_component_restore("SUB-INVESTMENT", backup, actor="test")
        self.assertEqual(self.investment.get("restore-me")["name"], "Bond")

    def test_lazy_storage_idempotent_schema_and_transaction_rollback(self) -> None:
        empty_root = self.root / "lazy"
        investment = InvestmentSubsystem(empty_root, database_foundation=self.database)
        self.assertFalse(investment.repository.database_path.exists())
        self.assertEqual(investment.list(), [])
        self.assertFalse(investment.repository.database_path.exists())
        investment.create("One", investment_id="fixed")
        investment.repository.initialize()
        with self.assertRaises(Exception):
            investment.create("Duplicate", investment_id="fixed")
        self.assertEqual(len(investment.list()), 1)

    def test_registry_policy_and_no_direct_sqlite_access(self) -> None:
        repository_root = Path(__file__).parents[1]
        registry = json.loads((repository_root / "config/database_integration_registry.json").read_text(encoding="utf-8"))
        self.assertTrue({"SUB-INVESTMENT", "SUB-JOB"}.issubset(registry["runtime_components"]))
        self.assertNotIn("Investment", registry["required_future_components"])
        self.assertNotIn("Job", registry["required_future_components"])
        for subsystem in ("investment", "job"):
            for source_path in (repository_root / "subsystems" / subsystem).glob("*.py"):
                source = source_path.read_text(encoding="utf-8")
                self.assertNotIn("import sqlite3", source)
                self.assertNotIn("sqlite3.connect", source)
        ignored = (repository_root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("data/investment/", ignored)
        self.assertIn("data/job/", ignored)


if __name__ == "__main__":
    unittest.main()
