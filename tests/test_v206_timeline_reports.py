from __future__ import annotations

from datetime import date
import tempfile
import unittest
from pathlib import Path

from modules.decision import DecisionService
from modules.journal import JournalService
from modules.reports import ReportsService
from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.timeline import (
    TIMELINE_SUBSYSTEMS,
    TimelineRecord,
    TimelineSource,
)
from subsystems.operations.engines.reports import (
    REPORT_SOURCE_SUBSYSTEMS,
    ReportContract,
)


class TimelineContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.hub = LivingHub(self.root)
        self.hub.bootstrap(())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_contract_contains_navigation_archive_and_metadata(self) -> None:
        record = TimelineRecord(
            record_id="INV-1",
            subsystem="investment",
            record_type="investment",
            event_type="ARCHIVED",
            title="Index Fund",
            summary="Position archived.",
            event_time="2026-07-25T12:00:00+00:00",
            created_time="2026-07-01T12:00:00+00:00",
            updated_time="2026-07-25T12:00:00+00:00",
            status="ARCHIVED",
            source="investment",
            metadata={"reason": "closed"},
        )
        self.assertTrue(record.archived)
        self.assertEqual(
            record.record_ref,
            {
                "subsystem": "investment",
                "record_type": "investment",
                "record_id": "INV-1",
            },
        )
        self.assertEqual(record.to_dict()["metadata"]["reason"], "closed")

    def test_all_required_subsystems_share_snapshot_contract(self) -> None:
        samples = {
            "finance": {"transaction_id": "FIN-1", "description": "Income", "occurred_on": "2026-07-25"},
            "investment": {"investment_id": "INV-1", "name": "Fund"},
            "job": {"job_id": "JOB-1", "title": "Engineer"},
            "health": {"record_id": "HLT-1", "title": "Checkup", "measured_on": "2026-07-25"},
            "vehicle": {"vehicle_id": "VEH-1", "display_name": "Car"},
            "housing": {"candidate_id": "HOU-1", "title": "Home"},
            "food": {"ingredient_id": "FOD-1", "name": "Rice"},
            "knowledge": {"record_id": "KNW-1", "title": "Note"},
            "routine": {"routine_id": "ROU-1", "name": "Review"},
            "personal-growth": {"goal_id": "GRO-1", "title": "Learn"},
            "collaboration": {"collaboration_id": "COL-1", "title": "Project"},
        }
        for subsystem in TIMELINE_SUBSYSTEMS:
            payload = {
                **samples[subsystem],
                "created_at": "2026-07-20T00:00:00+00:00",
                "updated_at": "2026-07-25T00:00:00+00:00",
                "status": "ACTIVE",
            }
            self.hub.timeline.register_subsystem_source(
                subsystem,
                lambda payload=payload: [payload],
            )
        records = self.hub.timeline.query(start="2026-07-24", end="2026-07-26")
        self.assertEqual({record.subsystem for record in records}, set(TIMELINE_SUBSYSTEMS))
        self.assertTrue(all(record.record_ref["record_id"] for record in records))

    def test_global_timeline_filters_sorts_and_tracks_status(self) -> None:
        JournalService(self.hub).create(
            "2026-07-25", "Timeline", "Journal event", ["timeline"], "FOCUSED"
        )
        decisions = DecisionService(self.hub)
        decision = decisions.create("Ship Timeline", "Foundation", "Ready", "", "", "active")
        decisions.revise(decision["id"], 1, status="review")
        self.hub.database.executions.record(
            "SUB-JOB",
            "archive",
            "JOB-1",
            "COMPLETED",
            actor="job",
            result={"target_id": "JOB-1", "record_type": "job", "status": "ARCHIVED"},
        )

        all_records = self.hub.timeline.query(include_archived=True)
        times = [record.event_time for record in all_records]
        self.assertEqual(times, sorted(times, reverse=True))
        self.assertTrue(any(record.subsystem == "journal" for record in all_records))
        self.assertTrue(any(record.subsystem == "job" and record.archived for record in all_records))
        active_only = self.hub.timeline.query(subsystem="job", include_archived=False)
        self.assertEqual(active_only, [])
        history = self.hub.timeline.status_history("decision", decision["id"])
        self.assertEqual(history[-1].metadata["status"], "review")


class ReportFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.hub = LivingHub(self.root)
        self.hub.bootstrap(())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_report_contract_and_all_source_definitions(self) -> None:
        self.assertEqual(
            set(REPORT_SOURCE_SUBSYSTEMS),
            {
                "journal",
                "decision",
                "finance",
                "health",
                "vehicle",
                "housing",
                "food",
                "investment",
                "job",
                "knowledge",
                "routine",
                "personal-growth",
                "collaboration",
            },
        )
        contract = ReportContract(
            report_id="RPT-1",
            report_type="weekly",
            title="Weekly Report",
            summary="Summary",
            content="Content",
            period_start="2026-07-19",
            period_end="2026-07-25",
            source_subsystems=("journal", "finance", "investment"),
        )
        self.assertEqual(contract.to_payload()["schema_version"], 2)

    def test_daily_weekly_monthly_build_and_source_connection(self) -> None:
        JournalService(self.hub).create(
            "2026-07-25", "Report", "Report source", ["report"], "FOCUSED"
        )
        reports = ReportsService(
            self.hub,
            {
                "finance": lambda report_type, start, end: {
                    "type": report_type,
                    "period": [start, end],
                    "balance": 100,
                },
                "investment": lambda report_type, start, end: {
                    "positions": 2,
                    "period_end": end,
                },
            },
        )
        for report_type in ("daily", "weekly", "monthly"):
            content = reports.build(report_type, as_of=date(2026, 7, 25))
            self.assertIn(f"Living OS {report_type.title()} Report", content)
            self.assertIn("### Finance", content)
            self.assertIn('"balance": 100', content)
            self.assertIn("### Investment", content)

    def test_report_crud_archive_and_lookup(self) -> None:
        reports = ReportsService(self.hub)
        preview = reports.create("daily", as_of=date(2026, 7, 25), save=False)
        self.assertEqual(preview["status"], "ACTIVE")
        saved = reports.save(
            "daily",
            preview["content"],
            period_start=date(2026, 7, 25),
            period_end=date(2026, 7, 25),
        )
        self.assertEqual(reports.get(saved["id"])["_status"], "ACTIVE")
        archived = reports.archive(saved["id"], saved["_version"])
        self.assertEqual(archived["_status"], "ARCHIVED")
        self.assertEqual(reports.list(), [])
        self.assertEqual(len(reports.list(include_archived=True)), 1)
        timeline = self.hub.timeline.query(record_id=saved["id"], include_archived=True)
        self.assertTrue(any(item.event_type == "ReportArchived" for item in timeline))


if __name__ == "__main__":
    unittest.main()
