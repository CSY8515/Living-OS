from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from subsystems.database import DatabaseSubsystem
from subsystems.database.engines.contracts import (
    OPERATIONAL_DATA_REGISTRY,
    OperationalDataRecord,
)
from subsystems.database_management import DatabaseManagementSubsystem
from subsystems.foundation.engines.personal_secretary import PersonalSecretaryAggregator
from subsystems.foundation.engines.time import utc_now_iso
from subsystems.operations.engines.catalog import V20_STABLE_MANIFESTS


ROOT = Path(__file__).parents[1]


class DatabaseArchitectureRecoveryV2095Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = DatabaseSubsystem(
            self.root / "data" / "hub" / "living_os.sqlite3",
            self.root / "backups" / "v2.095" / "database",
            self.root,
        )
        self.database.initialize(apply_migrations=True, actor="test")
        self.management = DatabaseManagementSubsystem(self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def record(
        self,
        operational_id: str,
        data_type: str,
        *,
        source: str = "SUB-TEST",
        title: str | None = None,
        summary: str | None = None,
    ) -> dict[str, object]:
        return self.database.record_operational_data(
            OperationalDataRecord(
                operational_id=operational_id,
                data_type=data_type,
                source_subsystem=source,
                title=title or data_type,
                summary=summary or f"Preserved {data_type} fact.",
                occurred_at=utc_now_iso(),
            ),
            actor="test",
        )

    def test_registry_recovers_all_required_types_and_preservation_rules(self) -> None:
        registry = self.database.operational_data_registry()
        self.assertEqual(set(registry["types"]), set(OPERATIONAL_DATA_REGISTRY))
        self.assertEqual(registry["retention_policy"], "PRESERVE")
        self.assertEqual(registry["deduplication_policy"], "LOGICAL_ONLY")
        configured = json.loads(
            (ROOT / "config" / "database_integration_registry.json").read_text(
                encoding="utf-8"
            )
        )["operational_data_contract"]
        self.assertEqual(set(configured["types"]), set(OPERATIONAL_DATA_REGISTRY))
        self.assertEqual(configured["retention_policy"], "PRESERVE")

    def test_data_plane_preserves_every_operational_category(self) -> None:
        for index, data_type in enumerate(OPERATIONAL_DATA_REGISTRY):
            self.record(f"OP-{index}", data_type)
        stored = self.database.operational_data()
        self.assertEqual(len(stored), len(OPERATIONAL_DATA_REGISTRY))
        self.assertEqual({item["data_type"] for item in stored}, set(OPERATIONAL_DATA_REGISTRY))
        self.assertTrue(all(item["retention_policy"] == "PRESERVE" for item in stored))

    def test_logical_deduplication_never_deletes_source_or_business_records(self) -> None:
        business = self.database.create(
            "SUB-TEST", "business", "BUSINESS-1", {"value": "unchanged"}, actor="test"
        )
        for index in range(3):
            self.record(
                f"DUPLICATE-{index}",
                "WARNING",
                title="Repeated warning",
                summary="Same operational fact",
            )
        analysis = self.management.operational_analysis()
        self.assertGreaterEqual(len(analysis["duplicates"]), 2)
        self.assertTrue(analysis["rule_candidates"])
        self.assertEqual(len(self.database.operational_data()), 3)
        self.assertEqual(self.database.read("SUB-TEST", "business", "BUSINESS-1"), business)

    def test_execution_failures_are_classified_without_rewriting_history(self) -> None:
        execution_id = self.database.executions.record(
            "SUB-TEST",
            "invalid_write",
            "record",
            "FAILED",
            actor="test",
            error=ValueError("invalid"),
            recovery_result="ROLLED_BACK",
            validation_result="FAILED",
            failure_context={"operational_type": "UNRESOLVED_ISSUE"},
        )
        analysis = self.management.operational_analysis()
        projected = next(
            item for item in analysis["unresolved_issues"] if item["record_id"] == execution_id
        )
        self.assertTrue(
            {
                "FAILURE",
                "ERROR",
                "RECOVERY",
                "ROLLBACK",
                "VALIDATION_FAILURE",
                "EXECUTION_FAILURE",
                "INVALID_DATA",
                "UNRESOLVED_ISSUE",
            }.issubset(projected["categories"])
        )
        original = next(
            item for item in self.database.execution_records(100) if item["execution_id"] == execution_id
        )
        self.assertEqual(original["status"], "FAILED")
        self.assertEqual(original["recovery_result"], "ROLLED_BACK")

    def test_running_execution_is_not_misclassified_as_success(self) -> None:
        with self.database.executions.track(
            "SUB-TEST", "active_work", "record", actor="test"
        ) as state:
            projected_ids = {
                item["record_id"] for item in self.management.operational.collect()
            }
            self.assertNotIn(state["execution_id"], projected_ids)

    def test_manager_generates_patterns_recommendations_and_candidates(self) -> None:
        for index in range(3):
            self.record(
                f"RULE-{index}",
                "WARNING",
                source="SUB-A",
                title="Repeated pattern",
                summary="Same pattern",
            )
        self.record("STANDARD-A", "WARNING", source="SUB-A")
        self.record("STANDARD-B", "WARNING", source="SUB-B")
        self.record("STANDARD-C", "WARNING", source="SUB-C")
        report = self.management.operational_report()
        self.assertGreaterEqual(report["operational_summary"]["classification"]["WARNING"], 6)
        self.assertTrue(report["patterns"]["repeated_fingerprints"])
        self.assertTrue(report["recommendations"])
        self.assertTrue(report["rule_candidates"])
        self.assertTrue(
            any(item.get("category") == "WARNING" for item in report["standard_candidates"])
        )

    def test_personal_secretary_contract_aggregates_prioritizes_and_reports(self) -> None:
        self.record("INCIDENT-1", "INCIDENT", source="SUB-OPERATIONS")
        brief = self.management.report_to_personal_secretary(
            PersonalSecretaryAggregator(), record=False, actor="test"
        )
        self.assertEqual(brief["priority"], "CRITICAL")
        self.assertEqual(brief["summary"]["report_count"], 1)
        self.assertGreaterEqual(brief["summary"]["unresolved_issues"], 1)
        self.assertTrue(brief["source_reports"][0].startswith("DBR-"))
        self.assertIn("운영 보고", brief["user_report"])

    def test_runtime_registry_exposes_recovered_contracts(self) -> None:
        manifests = {item.module_id: item for item in V20_STABLE_MANIFESTS}
        self.assertIn("operational-data-preservation", manifests["database"].capabilities)
        self.assertIn("logical-deduplication", manifests["database_management"].capabilities)
        self.assertIn("personal-secretary-contract", manifests["database_management"].capabilities)


if __name__ == "__main__":
    unittest.main()
