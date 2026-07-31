from __future__ import annotations

import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from subsystems.collaboration import CollaborationSubsystem
from subsystems.finance import FinanceSubsystem
from subsystems.food import FoodSubsystem
from subsystems.foundation.engines.data_reset import (
    OwnerDataResetError,
    OwnerDataResetService,
    development_legacy_empty_states,
)
from subsystems.foundation.engines.hub import LivingHub
from subsystems.health import HealthSubsystem
from subsystems.housing import HousingSubsystem
from subsystems.insight.engines.ai_credentials import resolve_api_key
from subsystems.investment import InvestmentSubsystem
from subsystems.job import JobSubsystem
from subsystems.knowledge import KnowledgeSubsystem
from subsystems.operations.engines.catalog import V206_STABLE_MANIFESTS
from subsystems.operations.engines.journal import JournalService
from subsystems.personal_growth import PersonalGrowthSubsystem
from subsystems.routine import RoutineSubsystem
from subsystems.vehicle import VehicleSubsystem


ROOT = Path(__file__).resolve().parent.parent


class FinalHotfixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.hub = LivingHub(self.root)
        self.hub.bootstrap(V206_STABLE_MANIFESTS)
        self.finance = FinanceSubsystem(
            self.root,
            self.hub.component_database_path("finance"),
            self.hub.database,
        )
        self.food = FoodSubsystem(
            self.root,
            self.hub.component_database_path("food"),
            self.hub.database,
        )
        self.health = HealthSubsystem(
            self.root,
            self.hub.component_database_path("health"),
            self.hub.database,
        )
        self.housing = HousingSubsystem(
            self.root,
            self.hub.component_database_path("housing"),
            self.hub.database,
        )
        self.vehicle = VehicleSubsystem(
            self.root,
            self.hub.component_database_path("vehicle"),
            self.hub.database,
        )
        self.knowledge = KnowledgeSubsystem(
            self.root,
            self.hub.component_database_path("knowledge"),
            self.hub.database,
        )
        self.routine = RoutineSubsystem(
            self.root,
            self.hub.component_database_path("routine"),
            self.hub.database,
        )
        self.investment = InvestmentSubsystem(
            self.root,
            self.hub.component_database_path("investment"),
            self.hub.database,
        )
        self.job = JobSubsystem(
            self.root,
            self.hub.component_database_path("job"),
            self.hub.database,
        )
        self.growth = PersonalGrowthSubsystem(
            self.root,
            self.hub.component_database_path("personal-growth"),
            self.hub.database,
        )
        self.collaboration = CollaborationSubsystem(
            self.root,
            self.hub.component_database_path("collaboration"),
            self.hub.database,
        )
        self.targets = (
            self.finance,
            self.food,
            self.health,
            self.housing,
            self.vehicle,
            self.knowledge,
            self.routine,
            self.investment,
            self.job,
            self.growth,
            self.collaboration,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def housing_values() -> dict[str, object]:
        return {
            "name": "Home",
            "deposit": 10_000_000,
            "monthly_rent": 600_000,
            "maintenance_fee": 100_000,
            "maintenance_fee_provided": True,
            "commute_minutes": 30,
            "parking_available": True,
            "options_memo": "",
            "special_notes": "",
        }

    def populate_all_owners(self) -> None:
        self.finance.record_income(1000, "Salary", "2026-07-01")
        self.food.create_ingredient("Rice", "grain", 100, "g")
        self.health.record_weight(70, "2026-07-01")
        self.housing.create_candidate(**self.housing_values())
        self.vehicle.create_vehicle("Car")
        self.knowledge.create("Knowledge", "Owner content")
        self.routine.create("Morning")
        self.investment.create("Index Fund")
        self.job.create("Company", "Engineer")
        self.growth.create("Learn")
        self.collaboration.create("Plan", "Partner")
        JournalService(self.hub).create(
            "2026-07-31", "Journal", "Owner entry", [], "NORMAL"
        )
        self.hub.documents.add("private.txt", b"owner document")

    def test_owner_reset_covers_every_store_and_preserves_system_state(self) -> None:
        self.populate_all_owners()
        self.hub.security.configure("correct horse battery staple")
        legacy = development_legacy_empty_states(self.root)
        daily_log = self.root / "data" / "daily_logs.json"
        daily_log.parent.mkdir(parents=True, exist_ok=True)
        daily_log.write_text(
            json.dumps({"logs": [{"id": "LOG-1", "title": "Owner log"}]}),
            encoding="utf-8",
        )
        service = OwnerDataResetService(
            self.hub,
            self.targets,
            legacy_empty_states=legacy,
        )

        preview = service.preview()
        self.assertTrue(all(preview[target.subsystem_id] > 0 for target in self.targets))
        self.assertGreater(preview["HUB"], 0)
        self.assertEqual(preview["LEGACY"], 1)

        report = service.reset(actor="test-owner")

        self.assertGreater(report.total_removed, len(self.targets))
        self.assertTrue(Path(report.backup_path).is_file())
        self.assertTrue(self.hub.backups.verify(Path(report.backup_path)))
        self.assertTrue(all(target.owner_data_count() == 0 for target in self.targets))
        self.assertEqual(JournalService(self.hub).list(), [])
        self.assertEqual(self.hub.documents.list(), [])
        self.assertTrue(self.hub.security.configured)
        self.assertTrue(self.hub.security.verify("correct horse battery staple"))
        self.assertTrue(
            {target.subsystem_id for target in self.targets}.issubset(
                {
                    item["component_id"]
                    for item in self.hub.database.registered_components()
                }
            )
        )
        self.assertEqual(json.loads(daily_log.read_text(encoding="utf-8")), {"logs": []})
        with zipfile.ZipFile(report.backup_path) as archive:
            self.assertTrue(
                any(name.startswith("hub/documents/") for name in archive.namelist())
            )

    def test_reset_failure_restores_already_deleted_owner_data(self) -> None:
        self.finance.record_income(1000, "Salary", "2026-07-01")
        self.health.record_weight(70, "2026-07-01")
        JournalService(self.hub).create(
            "2026-07-31", "Journal", "Keep after rollback", [], "NORMAL"
        )
        service = OwnerDataResetService(self.hub, (self.finance, self.health))

        with patch.object(
            self.health,
            "reset_owner_data",
            side_effect=RuntimeError("simulated reset failure"),
        ):
            with self.assertRaisesRegex(
                OwnerDataResetError,
                "verified backup was restored",
            ):
                service.reset(actor="test-owner")

        self.assertEqual(len(self.finance.list_transactions()), 1)
        self.assertEqual(len(self.health.list_weights()), 1)
        self.assertEqual(len(JournalService(self.hub).list()), 1)

    def test_policy_approved_physical_deletion_is_real(self) -> None:
        weight = self.health.record_weight(70, "2026-07-01")
        self.assertTrue(self.health.delete_weight(weight["record_id"]))
        self.assertEqual(self.health.list_weights(), [])

        candidate = self.housing.create_candidate(**self.housing_values())
        self.assertTrue(self.housing.delete_candidate(candidate["candidate_id"]))
        self.assertEqual(self.housing.list_candidates(), [])

    def test_byok_is_session_only_when_shared_sources_are_disabled(self) -> None:
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "environment-secret"}),
            patch(
                "subsystems.insight.engines.ai_credentials.load_saved_api_key",
                return_value="saved-secret",
            ),
        ):
            self.assertEqual(
                resolve_api_key("", allow_shared_sources=False),
                ("", "not configured"),
            )
            self.assertEqual(
                resolve_api_key(
                    "session-secret",
                    allow_shared_sources=False,
                ),
                ("session-secret", "session"),
            )

        pages = (
            ROOT / "subsystems" / "experience" / "engines" / "pages.py"
        ).read_text(encoding="utf-8")
        compatibility_settings = (
            ROOT / "subsystems" / "compatibility" / "engines" / "settings.py"
        ).read_text(encoding="utf-8")
        self.assertGreaterEqual(
            pages.count(
                "allow_shared_sources=not hub.runtime_config.production"
            ),
            2,
        )
        ai_briefing = pages.split("def render_ai_briefing", 1)[1].split(
            "def render_documents", 1
        )[0]
        self.assertIn('"OpenAI API Key"', ai_briefing)
        self.assertIn('type="password"', ai_briefing)
        self.assertIn('key="ai_session_api_key"', ai_briefing)
        self.assertNotIn("save_api_key(", compatibility_settings)
        self.assertNotIn("remove_saved_api_key(", compatibility_settings)

    def test_production_sources_have_no_dummy_records_or_input_placeholders(self) -> None:
        self.assertEqual(
            json.loads((ROOT / "data" / "daily_logs.json").read_text(encoding="utf-8")),
            {"logs": []},
        )
        self.assertEqual(
            json.loads((ROOT / "data" / "archive.json").read_text(encoding="utf-8")),
            {"items": []},
        )
        self.assertEqual(
            (ROOT / "logs" / "decision_log.jsonl").read_text(encoding="utf-8"),
            "",
        )
        self.assertEqual(
            json.loads(
                (ROOT / "config" / "module_registry.json").read_text(
                    encoding="utf-8"
                )
            ),
            {"modules": []},
        )
        for relative in (
            "subsystems/experience/engines/pages.py",
            "subsystems/compatibility/engines/archive.py",
            "subsystems/compatibility/engines/daily_log.py",
            "subsystems/compatibility/engines/settings.py",
        ):
            with self.subTest(relative=relative):
                source = (ROOT / relative).read_text(encoding="utf-8")
                self.assertNotIn("placeholder=", source)


if __name__ == "__main__":
    unittest.main()
