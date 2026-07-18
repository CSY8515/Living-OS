from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parent.parent
PERSISTED_FILES = [
    ROOT / "data" / "daily_logs.json",
    ROOT / "data" / "archive.json",
    ROOT / "data" / "finance_budget.json",
    ROOT / "data" / "finance" / "finance.sqlite3",
    ROOT / "data" / "health" / "health.sqlite3",
    ROOT / "data" / "housing" / "housing.sqlite3",
    ROOT / "data" / "vehicle" / "vehicle.sqlite3",
    ROOT / "data" / "food" / "food.sqlite3",
    ROOT / "data" / "knowledge" / "knowledge.sqlite3",
    ROOT / "data" / "routine" / "routine.sqlite3",
    ROOT / "data" / "investment" / "investment.sqlite3",
    ROOT / "data" / "job" / "job.sqlite3",
    ROOT / "data" / "personal_growth" / "personal_growth.sqlite3",
    ROOT / "data" / "collaboration" / "collaboration.sqlite3",
    ROOT / "data" / "housing_candidates.json",
    ROOT / "logs" / "decision_log.jsonl",
    ROOT / "reports" / "report_index.json",
    ROOT / "state" / "settings.json",
    ROOT / "config" / "module_registry.json",
]
PAGES = [
    "Command Center",
    "Daily Log",
    "Decision Log",
    "Reports",
    "Archive",
    "Analytics",
    "Review",
    "AI Analysis",
    "Documents",
    "Finance",
    "Health",
    "Housing",
    "Vehicle",
    "Food",
    "Knowledge",
    "Routine",
    "Knowledge Management",
    "Routine Management",
    "Investment",
    "Job",
    "Investment Management",
    "Job Management",
    "Personal Growth",
    "Personal Growth Management",
    "Collaboration",
    "Collaboration Management",
    "Database",
    "Database Management",
    "Module Manager",
    "Settings",
]


def fingerprints() -> dict[Path, str]:
    return {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in PERSISTED_FILES
        if path.exists()
    }


class StreamlitPageSmokeTests(unittest.TestCase):
    def test_every_page_renders_without_errors_or_page_load_writes(self) -> None:
        before = fingerprints()
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        self.assertEqual(app.sidebar.caption[0].value, "v2.0.4")
        self.assertFalse(app.exception)
        next(button for button in app.button if "Learning" in button.label).click().run()
        self.assertEqual(app.sidebar.radio[0].value, "Personal Growth")
        self.assertFalse(app.exception)

        for page in PAGES:
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.assertFalse(app.exception)

        self.assertEqual(fingerprints(), before)


if __name__ == "__main__":
    unittest.main()
