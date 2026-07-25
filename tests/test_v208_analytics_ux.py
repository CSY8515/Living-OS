from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from subsystems.foundation.engines.hub import LivingHub
from subsystems.insight.engines.analytics import AnalyticsEngine
from subsystems.insight.engines.search import GlobalSearchEngine
from subsystems.operations.engines.reports import REPORT_TYPES, ReportsService


class AnalyticsUxEnhancementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.hub = LivingHub(self.root)
        self.hub.bootstrap(())
        records = [
            {
                "transaction_id": "FIN-1",
                "description": "Monthly salary",
                "category": "income",
                "occurred_on": "2026-07-01",
                "created_at": "2026-07-01T00:00:00+00:00",
                "updated_at": "2026-07-01T00:00:00+00:00",
                "status": "active",
            },
            {
                "transaction_id": "FIN-2",
                "description": "Food budget",
                "category": "expense",
                "occurred_on": "2026-07-15",
                "created_at": "2026-07-15T00:00:00+00:00",
                "updated_at": "2026-07-20T00:00:00+00:00",
                "status": "archived",
            },
        ]
        self.hub.timeline.register_subsystem_source(
            "finance",
            lambda: records,
            summary_field="category",
        )
        self.hub.timeline.register_subsystem_source(
            "health",
            lambda: [
                {
                    "record_id": "HLT-1",
                    "title": "Weight trend",
                    "note": "Progress",
                    "measured_on": "2026-06-15",
                    "created_at": "2026-06-15T00:00:00+00:00",
                    "updated_at": "2026-06-15T00:00:00+00:00",
                    "status": "active",
                }
            ],
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_timeline_search_category_sort_and_archive_filters(self) -> None:
        newest = self.hub.timeline.query(
            subsystem="finance", search="food", category="transaction"
        )
        self.assertEqual([item.record_id for item in newest], ["FIN-2"])
        self.assertEqual(newest[0].category, "transaction")
        self.assertEqual(newest[0].to_dict()["category"], "transaction")
        self.assertEqual(
            [item.record_id for item in self.hub.timeline.query(
                subsystem="finance", sort_order="asc"
            )],
            ["FIN-1", "FIN-2"],
        )
        self.assertEqual(
            [item.record_id for item in self.hub.timeline.query(
                subsystem="finance", include_archived=False
            )],
            ["FIN-1"],
        )
        self.assertIn("transaction", self.hub.timeline.categories())

    def test_dashboard_trend_month_year_comparison_and_growth(self) -> None:
        engine = AnalyticsEngine(self.hub.timeline)
        summary = engine.monthly_summary(2026, 7)
        self.assertEqual(summary["total_activity"], 2)
        self.assertEqual(summary["archived_activity"], 1)
        yearly = engine.yearly_summary(2026)
        self.assertEqual(yearly["total_activity"], 3)
        trend = engine.trend(date(2026, 6, 1), date(2026, 7, 31))
        self.assertEqual([row["period"] for row in trend], ["2026-06", "2026-07"])
        comparison = engine.comparison(date(2026, 7, 1), date(2026, 7, 31))
        self.assertEqual(comparison["current"]["total_activity"], 2)
        self.assertEqual(comparison["previous"]["total_activity"], 1)
        growth = engine.growth_analysis(as_of=date(2026, 7, 31), months=2)
        self.assertEqual(growth["net_growth"], 1)
        dashboard = engine.dashboard(as_of=date(2026, 7, 31))
        self.assertEqual(len(dashboard["state_cards"]), 4)
        self.assertEqual(
            {item["target"] for item in dashboard["quick_actions"]},
            {"Timeline", "Search", "Reports", "Analytics"},
        )

    def test_global_and_subsystem_search_return_navigation_targets(self) -> None:
        search = GlobalSearchEngine(self.hub.timeline)
        result = search.search("salary")[0]
        self.assertEqual(result.record_id, "FIN-1")
        self.assertEqual(result.target["subsystem"], "finance")
        health = search.subsystem_search("health", "weight")
        self.assertEqual([item.record_id for item in health], ["HLT-1"])
        self.assertEqual(search.search("missing"), [])

    def test_yearly_report_summary_and_cross_subsystem_summary(self) -> None:
        self.assertIn("yearly", REPORT_TYPES)
        reports = ReportsService(self.hub)
        summary = reports.report_summary("yearly", as_of=date(2026, 7, 31))
        self.assertEqual(summary["timeline_events"], 3)
        self.assertEqual(summary["by_subsystem"], {"finance": 2, "health": 1})
        cross = reports.cross_subsystem_summary(
            "yearly", as_of=date(2026, 7, 31)
        )
        self.assertEqual(
            cross,
            [
                {"subsystem": "finance", "activity": 2},
                {"subsystem": "health", "activity": 1},
            ],
        )
        content = reports.build("yearly", as_of=date(2026, 7, 31))
        self.assertIn("Living OS Yearly Report", content)
        self.assertIn("## Cross Subsystem Summary", content)

    def test_invalid_ranges_and_options_are_rejected(self) -> None:
        engine = AnalyticsEngine(self.hub.timeline)
        with self.assertRaises(ValueError):
            engine.summary(date(2026, 7, 2), date(2026, 7, 1))
        with self.assertRaises(ValueError):
            engine.trend(
                date(2026, 7, 1), date(2026, 7, 31), granularity="quarter"
            )
        with self.assertRaises(ValueError):
            self.hub.timeline.query(sort_order="sideways")
        with self.assertRaises(ValueError):
            GlobalSearchEngine(self.hub.timeline).search(sort_by="unknown")


if __name__ == "__main__":
    unittest.main()
