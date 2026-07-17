from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from subsystems.database import DatabaseSubsystem
from subsystems.database_management import DatabaseManagementSubsystem
from subsystems.knowledge import KnowledgeSubsystem
from subsystems.knowledge.models import KnowledgeRecord
from subsystems.routine import RoutineSubsystem
from subsystems.routine.models import RoutineExecutionRecord, RoutineRecord


class V18KnowledgeRoutineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = DatabaseSubsystem(self.root / "data/hub/living_os.sqlite3", self.root / "backups/v1.8/database", self.root)
        self.database.initialize(apply_migrations=True, actor="test")
        self.knowledge = KnowledgeSubsystem(self.root, database_foundation=self.database)
        self.routine = RoutineSubsystem(self.root, database_foundation=self.database)

    def tearDown(self) -> None: self.temporary.cleanup()

    def test_models_reject_invalid_contracts(self) -> None:
        with self.assertRaises(ValueError): KnowledgeRecord("", "", "").validate()
        with self.assertRaises(ValueError): RoutineRecord("r", "name", frequency="YEARLY").validate()
        with self.assertRaises(ValueError): RoutineExecutionRecord("e", "r", "invalid").validate()

    def test_knowledge_crud_search_archive_and_management(self) -> None:
        created = self.knowledge.create("Architecture", "Database contract", category="Design", tags=["db"], importance=5)
        self.assertEqual(self.knowledge.get(created["record_id"])["title"], "Architecture")
        self.assertEqual(len(self.knowledge.search("contract")), 1)
        updated = self.knowledge.update(created["record_id"], status="ACTIVE", summary="Approved")
        self.assertEqual(updated["status"], "ACTIVE")
        self.assertEqual(self.knowledge.archive(created["record_id"])["status"], "ARCHIVED")
        self.assertEqual(self.knowledge.list(), [])
        summary = self.knowledge.management_summary()
        self.assertEqual(summary["total"], 1); self.assertTrue(summary["registry_registered"])

    def test_routine_schedule_completion_failure_skip_and_streak(self) -> None:
        item = self.routine.create("Morning review", frequency="DAILY", status="ACTIVE")
        first = self.routine.schedule(item["routine_id"])
        self.routine.complete(first["execution_id"], result="done", duration=10)
        after = self.routine.get(item["routine_id"])
        self.assertEqual(after["completion_count"], 1); self.assertEqual(after["streak"], 1)
        second = self.routine.schedule(item["routine_id"]); self.routine.fail(second["execution_id"], note="blocked")
        after = self.routine.get(item["routine_id"])
        self.assertEqual(after["failure_count"], 1); self.assertEqual(after["streak"], 0)
        third = self.routine.schedule(item["routine_id"]); self.assertEqual(self.routine.skip(third["execution_id"])["status"], "SKIPPED")

    def test_due_and_schedule_calculation(self) -> None:
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        item = self.routine.create("Due now", frequency="WEEKLY", status="ACTIVE", next_due_at=past)
        self.assertEqual(self.routine.due()[0]["routine_id"], item["routine_id"])
        due = datetime.fromisoformat(self.routine.calculate_next_due("INTERVAL", past, "3"))
        self.assertEqual(due, datetime.fromisoformat(past) + timedelta(days=3))
        monthly = self.routine.calculate_next_due("MONTHLY", "2026-01-31T09:00:00+00:00")
        self.assertEqual(monthly, "2026-02-28T09:00:00+00:00")

    def test_registry_execution_and_management_contract(self) -> None:
        registered = {r["component_id"] for r in DatabaseManagementSubsystem(self.database).registered_components()}
        self.assertTrue({"SUB-KNOWLEDGE", "SUB-ROUTINE"}.issubset(registered))
        knowledge = self.knowledge.create("Execution", "record me")
        routine = self.routine.create("Execute", status="ACTIVE")
        execution = self.routine.schedule(routine["routine_id"]); self.routine.complete(execution["execution_id"])
        actions = {(r["subsystem"], r["action"]) for r in self.database.execution_records(500)}
        self.assertIn(("SUB-KNOWLEDGE", "create"), actions); self.assertIn(("SUB-ROUTINE", "completed"), actions)
        self.assertTrue(knowledge["record_id"])

    def test_duplicate_ids_and_invalid_input_do_not_corrupt_database(self) -> None:
        self.knowledge.create("One", "content", record_id="fixed")
        with self.assertRaises(Exception): self.knowledge.create("Two", "content", record_id="fixed")
        self.assertEqual(len(self.knowledge.list()), 1)
        with self.assertRaises(ValueError): self.routine.create("Bad", frequency="INTERVAL", schedule_rule="never", status="ACTIVE")
        self.assertEqual(self.database.integrity_check(record=False).integrity, "ok")


if __name__ == "__main__": unittest.main()
