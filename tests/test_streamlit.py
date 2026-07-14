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
    ROOT / "data" / "housing_candidates.json",
    ROOT / "logs" / "decision_log.jsonl",
    ROOT / "reports" / "report_index.json",
    ROOT / "state" / "settings.json",
    ROOT / "config" / "module_registry.json",
]
PAGES = [
    "Dashboard",
    "Daily Log",
    "Decision Log",
    "Reports",
    "Archive",
    "Analytics",
    "Review",
    "AI Analysis",
    "Documents",
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
        self.assertEqual(app.sidebar.caption[0].value, "v2.0 Implementation")
        self.assertFalse(app.exception)

        for page in PAGES:
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.assertFalse(app.exception)

        self.assertEqual(fingerprints(), before)


if __name__ == "__main__":
    unittest.main()
