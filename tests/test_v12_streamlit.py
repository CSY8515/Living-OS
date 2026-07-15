from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


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
    "Finance",
    "Module Manager",
    "Settings",
]


class CanonicalStreamlitTests(unittest.TestCase):
    def test_every_canonical_v12_page_renders_without_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "canonical_app.py"
            script.write_text(
                "\n".join(
                    [
                        "import streamlit as st",
                        "from pathlib import Path",
                        "from core.hub import LivingHub",
                        "from subsystems.finance import FinanceSubsystem",
                        "from modules.catalog import V12_STABLE_MANIFESTS",
                        "from app.pages import render_dashboard, render_journal, render_decisions, render_reports, render_knowledge, render_analytics, render_review, render_ai_briefing, render_documents, render_finance, render_module_manager, render_settings",
                        f"hub = LivingHub(Path({str(root)!r}))",
                        "hub.bootstrap(V12_STABLE_MANIFESTS)",
                        f"finance = FinanceSubsystem(Path({str(root)!r}), Path({str(root / 'finance.sqlite3')!r}))",
                        "hub.store.set_meta('v1_migration_complete', 'true')",
                        f"pages = {PAGES!r}",
                        "page = st.sidebar.radio('Menu', pages)",
                        "renderers = {'Dashboard': render_dashboard, 'Daily Log': render_journal, 'Decision Log': render_decisions, 'Reports': render_reports, 'Archive': render_knowledge, 'Analytics': render_analytics, 'Review': render_review, 'AI Analysis': render_ai_briefing, 'Documents': render_documents, 'Module Manager': render_module_manager, 'Settings': render_settings}",
                        "render_finance(finance) if page == 'Finance' else renderers[page](hub)",
                    ]
                ),
                encoding="utf-8",
            )
            app = AppTest.from_file(str(script), default_timeout=10).run()
            self.assertFalse(app.exception)
            for page in PAGES:
                with self.subTest(page=page):
                    app.sidebar.radio[0].set_value(page).run()
                    self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
