from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from modules.analytics import count_tags, count_values
from modules.date_utils import filter_records_by_window, parse_date, window_bounds
from modules.report_system import build_report_text
from modules.review import recent_activity, reviewable_decisions
from modules.storage import load_dashboard_data, read_json, read_jsonl


class DateUtilityTests(unittest.TestCase):
    def test_parse_date_supports_dates_and_iso_timestamps(self) -> None:
        self.assertEqual(parse_date("2026-07-12"), date(2026, 7, 12))
        self.assertEqual(parse_date("2026-07-12T08:30:00+09:00"), date(2026, 7, 12))
        self.assertEqual(parse_date("2026-07-12T00:00:00Z"), date(2026, 7, 12))
        self.assertIsNone(parse_date("not-a-date"))
        self.assertIsNone(parse_date(""))
        self.assertIsNone(parse_date(None))

    def test_window_boundaries_are_inclusive(self) -> None:
        today = date(2026, 7, 12)
        self.assertEqual(window_bounds("Last 7 days", today), (date(2026, 7, 6), today))
        self.assertEqual(window_bounds("Last 30 days", today), (date(2026, 6, 13), today))
        self.assertEqual(window_bounds("This month", today), (date(2026, 7, 1), today))
        self.assertEqual(window_bounds("All time", today), (None, None))

    def test_filter_uses_existing_date_fields_and_skips_invalid_values(self) -> None:
        records = [
            {"id": "start", "date": "2026-07-06"},
            {"id": "end", "updated_at": "2026-07-12T23:59:00+09:00"},
            {"id": "old", "date": "2026-07-05"},
            {"id": "invalid", "date": "bad"},
        ]
        filtered = filter_records_by_window(records, "Last 7 days", date(2026, 7, 12))
        self.assertEqual([item["id"] for item in filtered], ["start", "end"])
        self.assertIs(filter_records_by_window(records, "All time"), records)


class StorageReliabilityTests(unittest.TestCase):
    def test_json_and_jsonl_readers_fail_safely(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed_json = root / "bad.json"
            malformed_json.write_text("{bad", encoding="utf-8")
            self.assertEqual(read_json(malformed_json, {"items": []}), {"items": []})

            mixed_jsonl = root / "mixed.jsonl"
            mixed_jsonl.write_text('{"id": 1}\ninvalid\n[1, 2]\n{"id": 2}\n', encoding="utf-8")
            self.assertEqual(read_jsonl(mixed_jsonl), [{"id": 1}, {"id": 2}])

            self.assertEqual(read_json(root / "missing.json", {"safe": True}), {"safe": True})
            self.assertEqual(read_jsonl(root / "missing.jsonl"), [])

    def test_dashboard_counts_only_reviewable_decisions(self) -> None:
        decisions = [
            {"id": "1", "status": "draft"},
            {"id": "2", "status": "active"},
            {"id": "3", "status": "review"},
            {"id": "4", "status": "done"},
            {"id": "5", "status": "archive"},
        ]
        with (
            patch("modules.daily_log.load_daily_logs", return_value=[]),
            patch("modules.decision_log.read_decision_logs", return_value=decisions),
            patch("modules.storage.list_report_files", return_value=[]),
        ):
            data = load_dashboard_data()
        self.assertEqual(data["decision_count"], 5)
        self.assertEqual(data["reviewable_decision_count"], 3)


class AnalyticsAndReviewTests(unittest.TestCase):
    def test_analytics_counters_ignore_invalid_tags_and_use_fallbacks(self) -> None:
        records = [
            {"tags": ["work", " work ", ""], "status": "active"},
            {"tags": "not-a-list", "status": ""},
            {},
        ]
        self.assertEqual(count_tags(records)["work"], 2)
        self.assertEqual(count_values(records, "status", "draft")["draft"], 2)

    def test_review_queue_filters_status_and_orders_recent_first(self) -> None:
        decisions = [
            {"id": "old", "status": "draft", "updated_at": "2026-07-01"},
            {"id": "new", "status": "review", "updated_at": "2026-07-12"},
            {"id": "done", "status": "done", "updated_at": "2026-07-13"},
        ]
        self.assertEqual(
            [item["id"] for item in reviewable_decisions(decisions)],
            ["new", "old"],
        )
        self.assertEqual(
            [item["id"] for item in reviewable_decisions(decisions, "draft")],
            ["old"],
        )

    def test_recent_activity_handles_empty_and_invalid_dates(self) -> None:
        self.assertEqual(recent_activity([], [], [], []), [])
        activity = recent_activity(
            [{"id": "bad", "date": "bad", "title": "Bad"}],
            [{"id": "good", "status": "active", "updated_at": "2026-07-12", "decision": "Good"}],
            [],
            [],
        )
        self.assertEqual([item["id"] for item in activity], ["good", "bad"])


class ReportTests(unittest.TestCase):
    def test_report_preview_has_v10_label_without_saving(self) -> None:
        with (
            patch("modules.report_system.load_daily_logs", return_value=[]),
            patch("modules.report_system.read_decision_logs", return_value=[]),
        ):
            report = build_report_text("daily")
        self.assertIn("- Version: v1.2 Stable", report)


if __name__ == "__main__":
    unittest.main()
