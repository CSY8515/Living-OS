from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.hub import LivingHub
from modules.decision import DecisionService
from modules.journal import JournalService
from modules.knowledge import KnowledgeService
from modules.projections import analytics_projection, dashboard_projection, review_projection
from modules.reports import ReportsService


class CanonicalModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.hub = LivingHub(Path(self.temporary.name))
        self.hub.bootstrap(())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_parity_modules_write_only_through_core_commands(self) -> None:
        journal = JournalService(self.hub)
        decision = DecisionService(self.hub)
        knowledge = KnowledgeService(self.hub)
        reports = ReportsService(self.hub)

        journal.create("2026-07-15", "Entry", "Real data", ["core"], "FOCUSED")
        selected = decision.create("Use Hub", "Single truth", "Stable", "", "", "review")
        item = knowledge.create("Evidence", "Reviewed material", "journal", ["case"], "archive")
        promoted = knowledge.promote(item["id"], 1, "Reviewed as a reusable case")
        report_text = reports.build("daily")
        report = reports.save("daily", report_text)

        self.assertEqual(promoted["kind"], "case")
        self.assertIn("Living OS Daily Report", report_text)
        self.assertEqual(report["generated_by"], "deterministic")
        self.assertEqual(self.hub.store.count("records"), 4)
        self.assertEqual(self.hub.store.count("domain_events"), 5)
        self.assertEqual(self.hub.store.count("audit_entries"), 5)

        dashboard = dashboard_projection(self.hub)
        self.assertEqual(dashboard["journal_count"], 1)
        self.assertEqual(dashboard["review_count"], 1)
        analytics = analytics_projection(self.hub)
        self.assertEqual(analytics["journal_tags"]["core"], 1)
        review = review_projection(self.hub)
        self.assertEqual(review["queue"][0]["id"], selected["id"])

    def test_reports_are_immutable_new_artifacts(self) -> None:
        reports = ReportsService(self.hub)
        first = reports.save("daily", "# First")
        second = reports.save("daily", "# Second")
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(first["_version"], 1)
        self.assertEqual(second["_version"], 1)
        self.assertEqual(len(reports.list()), 2)


if __name__ == "__main__":
    unittest.main()
