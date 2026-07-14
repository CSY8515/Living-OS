from __future__ import annotations

import ast
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from core.contracts import CommandEnvelope, ModuleManifest, RecordRef
from core.errors import CommandRejected, ConcurrencyError, MigrationError
from core.hub import LivingHub
from modules.catalog import V2_STABLE_MANIFESTS
from modules.decision import DecisionService
from modules.journal import JournalService


class HubCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.hub = LivingHub(self.root)
        self.hub.bootstrap(V2_STABLE_MANIFESTS)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_commands_are_transactional_versioned_evented_and_audited(self) -> None:
        journal = JournalService(self.hub)
        record = journal.create("2026-07-15", "Core", "Entry", ["v2"], "FOCUSED")
        self.assertEqual(record["_version"], 1)
        self.assertEqual(self.hub.store.count("records"), 1)
        self.assertEqual(self.hub.store.count("domain_events"), 1)
        self.assertEqual(self.hub.store.count("audit_entries"), 1)

        with self.assertRaises(CommandRejected):
            self.hub.commands.execute(CommandEnvelope("journal", "unknown", {}))
        self.assertEqual(self.hub.store.count("records"), 1)
        self.assertEqual(self.hub.store.count("audit_entries"), 2)

    def test_optimistic_concurrency_rejects_stale_decision_revision(self) -> None:
        decisions = DecisionService(self.hub)
        record = decisions.create("Choose Core", "Stable", "Safe", "", "", "active")
        revised = decisions.revise(record["id"], 1, status="review")
        self.assertEqual(revised["_version"], 2)
        with self.assertRaises(ConcurrencyError):
            decisions.revise(record["id"], 1, status="done")
        stored = self.hub.store.get_record(RecordRef("decision", "decision", record["id"]))
        self.assertEqual(stored["status"], "review")
        self.assertEqual(stored["_version"], 2)

    def test_module_lifecycle_is_validated_and_admin_modules_are_protected(self) -> None:
        self.hub.modules.transition("journal", "disabled")
        journal = next(item for item in self.hub.modules.list_modules() if item["module_id"] == "journal")
        self.assertEqual(journal["status"], "disabled")
        with self.assertRaises(ValueError):
            self.hub.modules.transition("journal", "installed")
        with self.assertRaises(ValueError):
            self.hub.modules.transition("settings", "disabled")
        registered = {item["module_id"] for item in self.hub.modules.list_modules()}
        self.assertNotIn("calendar", registered)
        self.assertNotIn("health", registered)
        self.assertNotIn("vehicle", registered)

    def test_document_content_is_hashed_and_integrity_checked(self) -> None:
        document = self.hub.documents.add("note.txt", b"Living OS", privacy_class="sensitive")
        self.assertEqual(document.content_hash, hashlib.sha256(b"Living OS").hexdigest())
        self.assertEqual(self.hub.documents.read(document.document_id), b"Living OS")
        self.assertEqual(self.hub.store.count("documents"), 1)
        self.assertEqual(self.hub.store.count("domain_events"), 1)
        self.assertEqual(self.hub.store.count("audit_entries"), 1)

    def test_verified_backup_restore_creates_safety_backup_and_rolls_state_back(self) -> None:
        journal = JournalService(self.hub)
        first = journal.create("2026-07-15", "First", "Before backup", [], "NORMAL")
        archive = self.hub.backups.create()
        self.assertTrue(self.hub.backups.verify(archive))
        journal.create("2026-07-15", "Second", "After backup", [], "NORMAL")
        self.assertEqual(len(journal.list()), 2)
        safety = self.hub.backups.restore(archive)
        self.assertTrue(self.hub.backups.verify(safety))
        restored = JournalService(self.hub).list()
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored[0]["id"], first["id"])


class MigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for relative in ("data", "logs", "reports", "state", "config"):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        (self.root / "data/daily_logs.json").write_text(
            json.dumps({"logs": [{"id": "LOG-00001", "date": "2026-07-15", "title": "Legacy"}]}),
            encoding="utf-8",
        )
        (self.root / "data/archive.json").write_text(
            json.dumps({"items": [{"id": "ARC-00001", "title": "Case"}]}), encoding="utf-8"
        )
        (self.root / "logs/decision_log.jsonl").write_text(
            json.dumps({"id": "DEC-00001", "decision": "Migrate", "status": "active"}) + "\ninvalid\n",
            encoding="utf-8",
        )
        (self.root / "reports/report_index.json").write_text('{"reports": []}', encoding="utf-8")
        (self.root / "config/module_registry.json").write_text('{"modules": []}', encoding="utf-8")
        (self.root / "data/housing_candidates.json").write_text('{"candidates": []}', encoding="utf-8")
        (self.root / "state/settings.json").write_text('{"app_name": "Living OS"}', encoding="utf-8")
        (self.root / "data/finance_budget.json").write_text('{"monthly_income": 0}', encoding="utf-8")
        self.original = {
            path: path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.hub = LivingHub(self.root)
        self.hub.bootstrap(())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_dry_run_is_read_only_and_apply_is_backed_up_and_reconciled(self) -> None:
        dry_run = self.hub.migration.dry_run()
        self.assertEqual(dry_run.accepted_total, 5)
        self.assertEqual(len(dry_run.quarantined), 1)
        self.assertEqual(self.hub.store.count("records"), 0)
        self.assertEqual(list((self.root / "backups").rglob("*.zip")), [])

        applied = self.hub.migration.apply()
        self.assertTrue(applied.applied)
        self.assertEqual(applied.accepted_total, 5)
        self.assertTrue(Path(applied.backup_path).exists())
        self.assertTrue(self.hub.backups.verify(Path(applied.backup_path)))
        self.assertTrue(self.hub.v1_migration_complete)
        self.assertEqual(self.hub.store.count("records"), 5)
        for path, content in self.original.items():
            self.assertEqual(path.read_bytes(), content)
        with self.assertRaises(MigrationError):
            self.hub.migration.apply()


class ArchitectureBoundaryTests(unittest.TestCase):
    def test_core_never_imports_app_modules_or_expansion(self) -> None:
        root = Path(__file__).resolve().parent.parent
        violations: list[str] = []
        for path in (root / "core").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    if name == "app" or name.startswith("app.") or name == "modules" or name.startswith("modules.") or name == "expansion" or name.startswith("expansion."):
                        violations.append(f"{path.name}: {name}")
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
