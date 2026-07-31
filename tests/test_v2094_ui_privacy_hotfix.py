from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from subsystems.experience.engines.theme import OFFICIAL_UI_CSS


ROOT = Path(__file__).resolve().parent.parent


class UiPrivacyHotfixTests(unittest.TestCase):
    def test_subsystem_world_plaque_keeps_long_titles_inside(self) -> None:
        self.assertIn("width:min(520px,46%)", OFFICIAL_UI_CSS)
        self.assertIn("grid-template-columns:minmax(180px,44%) minmax(0,1fr)", OFFICIAL_UI_CSS)
        self.assertIn("overflow-wrap:anywhere", OFFICIAL_UI_CSS)
        self.assertIn(".los-page-glyph{display:none!important}", OFFICIAL_UI_CSS)

    def test_reports_surface_never_renders_storage_source(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        app.sidebar.radio[0].set_value("Reports").run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.text_area), 0)
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn("생활 리포트", rendered)
        self.assertIn("전체 생활 기록 0건", rendered)
        self.assertNotIn("```json", rendered)
        self.assertNotIn("CANONICAL DRAFT", rendered)
        self.assertNotIn("Deterministic Report", rendered)
        self.assertNotIn("협업", rendered)
        self.assertNotIn("하위 시스템", rendered)
        self.assertNotIn("database_contract_registration", rendered)

    def test_reports_keep_raw_contract_internal(self) -> None:
        pages = (ROOT / "subsystems/experience/engines/pages.py").read_text(encoding="utf-8")
        report_view = pages.split("def render_reports", 1)[1].split("def _render_counter", 1)[0]
        self.assertIn("preview = service.build(report_type)", report_view)
        self.assertIn("service.save(report_type, preview)", report_view)
        self.assertNotIn('st.text_area("Deterministic Report"', report_view)
        self.assertNotIn('official_document("결정론적 리포트 원문"', report_view)

    def test_production_ui_hides_developer_details(self) -> None:
        config = (ROOT / ".streamlit/config.toml").read_text(encoding="utf-8")
        shell = (ROOT / "subsystems/experience/engines/shell.py").read_text(encoding="utf-8")
        self.assertIn('toolbarMode = "minimal"', config)
        self.assertIn('showErrorDetails = "none"', config)
        runtime_failure = shell.split("except RuntimeConfigurationError", 1)[1].split("st.stop()", 1)[0]
        self.assertNotIn("st.code", runtime_failure)
        self.assertNotIn("str(exc)", runtime_failure)


if __name__ == "__main__":
    unittest.main()
