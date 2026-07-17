from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from subsystems.collaboration import CollaborationSubsystem
from subsystems.database.subsystem import DatabaseSubsystem
from subsystems.database_management.subsystem import DatabaseManagementSubsystem
from subsystems.personal_growth import PersonalGrowthSubsystem


class V20GrowthCollaborationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = DatabaseSubsystem(self.root / "data/hub/living_os.sqlite3", self.root / "backups/v2/database", self.root)
        self.database.initialize(apply_migrations=True, actor="test")
        self.growth = PersonalGrowthSubsystem(self.root, database_foundation=self.database)
        self.collaboration = CollaborationSubsystem(self.root, database_foundation=self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_lazy_storage_crud_management_and_validation(self) -> None:
        self.assertFalse(self.growth.repository.database_path.exists())
        goal = self.growth.create("Build communication skill", goal_id="growth-1", area="RELATIONSHIPS", status="ACTIVE", progress=25)
        self.assertEqual(goal["progress"], 25)
        self.assertEqual(self.growth.update("growth-1", progress=60)["progress"], 60)
        self.assertEqual(self.growth.management_summary()["active"], 1)
        with self.assertRaises(ValueError): self.growth.update("growth-1", progress=101)

        item = self.collaboration.create("Launch project", "Design team", collaboration_id="collab-1", status="ACTIVE")
        self.assertEqual(item["partner"], "Design team")
        self.assertEqual(self.collaboration.update("collab-1", status="BLOCKED")["status"], "BLOCKED")
        self.assertEqual(self.collaboration.management_summary()["blocked"], 1)

    def test_registry_execution_integrity_backup_restore(self) -> None:
        self.growth.create("Goal", goal_id="restore-growth")
        self.collaboration.create("Work", "Partner", collaboration_id="restore-collab")
        components = {item["component_id"] for item in self.database.registered_components()}
        self.assertTrue({"SUB-PERSONAL-GROWTH", "SUB-COLLABORATION"}.issubset(components))
        management = DatabaseManagementSubsystem(self.database)
        self.assertTrue(all(item["integrity"] == "ok" for item in management.component_status() if item["component_id"] in components))
        backup = management.request_component_backup("SUB-PERSONAL-GROWTH", actor="test")
        self.growth.update("restore-growth", title="Changed")
        management.request_component_restore("SUB-PERSONAL-GROWTH", backup, actor="test")
        self.assertEqual(self.growth.get("restore-growth")["title"], "Goal")
        actions = [item["action"] for item in self.database.execution_records(500)]
        self.assertIn("component_backup", actions)

    def test_registry_policy_and_no_direct_sqlite_access(self) -> None:
        registry = json.loads((Path(__file__).parents[1] / "config/database_integration_registry.json").read_text(encoding="utf-8"))
        self.assertTrue({"SUB-PERSONAL-GROWTH", "SUB-COLLABORATION"}.issubset(registry["runtime_components"]))
        self.assertEqual(registry["required_future_components"], [])
        for directory in ("personal_growth", "collaboration"):
            source = "\n".join(path.read_text(encoding="utf-8") for path in (Path(__file__).parents[1] / "subsystems" / directory).glob("*.py"))
            self.assertNotIn("sqlite3.connect", source)


if __name__ == "__main__":
    unittest.main()
