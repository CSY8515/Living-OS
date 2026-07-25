from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from subsystems.experience.engines.localization import localize_data, ui_text
from subsystems.experience.engines.theme import OFFICIAL_UI_CSS
from tests.test_streamlit import PAGES


ROOT = Path(__file__).resolve().parent.parent
UI_FILES = (
    ROOT / "subsystems" / "experience" / "engines" / "pages.py",
    ROOT / "subsystems" / "experience" / "engines" / "shell.py",
)
UI_METHODS = {
    "title", "header", "subheader", "caption", "info", "warning", "error", "success",
    "button", "radio", "selectbox", "multiselect", "text_input", "text_area", "number_input",
    "date_input", "checkbox", "toggle", "metric", "tabs", "expander", "form_submit_button",
    "download_button", "file_uploader", "write",
}
ALLOWED_TERMS = ("Living OS", "OpenAI", "SQLite", "JSON", "ISO", "BMI", "KRW", "URL", "API", "AI", "OS", "kg", "km", "kWh")


def english_residue(text: str) -> str:
    value = text
    for term in ALLOWED_TERMS:
        value = value.replace(term, "")
    value = re.sub(r"v\d+(?:\.\d+)*", "", value, flags=re.I)
    return value


class OfficialUiContractTests(unittest.TestCase):
    def test_localization_is_display_only(self) -> None:
        self.assertEqual(ui_text("Global Timeline"), "통합 타임라인")
        self.assertEqual(ui_text("Create verified backup"), "검증 백업 생성")
        source = {"Status": "ACTIVE", "Title": "Owner text"}
        localized = localize_data(source)
        self.assertEqual(localized["상태"], "활성")
        self.assertEqual(source, {"Status": "ACTIVE", "Title": "Owner text"})

    def test_static_streamlit_labels_have_korean_projection(self) -> None:
        unresolved: list[str] = []
        for path in UI_FILES:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in UI_METHODS
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    continue
                source = node.args[0].value
                if not re.search(r"[A-Za-z]", source):
                    continue
                rendered = str(ui_text(source, context=node.func.attr))
                if re.search(r"[A-Za-z]{2,}", english_residue(rendered)):
                    unresolved.append(f"{path.name}:{node.lineno}: {source} -> {rendered}")
        self.assertEqual(unresolved, [])

    def test_official_theme_covers_interaction_and_responsive_contracts(self) -> None:
        required = (
            "Noto Sans KR", "--los-gold", "backdrop-filter", ":hover", ":focus-visible", ":active",
            "los-ripple", "los-enter", "los-float", "los-orbit", "los-scan",
            "@media(max-width:1280px)", "@media(max-width:1024px)",
            "@media(max-width:760px)", "@media(max-width:480px)",
            "prefers-reduced-motion",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, OFFICIAL_UI_CSS)

    def test_concept_world_has_all_subsystems_and_official_asset(self) -> None:
        pages = UI_FILES[0].read_text(encoding="utf-8")
        design = (ROOT / "subsystems" / "experience" / "engines" / "design_system.py").read_text(encoding="utf-8")
        theme = (ROOT / "subsystems" / "experience" / "engines" / "theme.py").read_text(encoding="utf-8")
        self.assertIn('key=f"world_node_{key}"', pages)
        self.assertIn('key=f"world_nav_{key}"', pages)
        for key in (
            "finance", "job", "investment", "knowledge", "routine", "growth",
            "food", "housing", "health", "vehicle", "collaboration",
        ):
            self.assertIn(f'"{key}")', pages)
            self.assertIn(f"st-key-world_node_{key}", theme)
        for key in ("dashboard", "today", "search", "reports", "ai"):
            self.assertIn(f'"{key}")', pages)
        self.assertIn("los-world-stage", design)
        asset = ROOT / "assets" / "living-os-official-world.png"
        self.assertTrue(asset.is_file())
        self.assertGreater(asset.stat().st_size, 1_000_000)

    def test_home_renders_korean_world_without_errors(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
        self.assertFalse(app.exception)
        labels = {button.label for button in app.button}
        for label in ("◒  재무", "♡  건강", "△  자기계발", "대시보드", "리포트"):
            self.assertIn(label, labels)
        self.assertEqual(app.sidebar.caption[0].value, "v2.0.9")
        self.assertEqual(app.sidebar.caption[1].value, "개인 생활 운영 시스템")

    def test_all_canonical_pages_render_without_ui_contract_errors(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
        for page in PAGES:
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.assertFalse(app.exception)

    def test_architecture_boundary_is_unchanged(self) -> None:
        localization = ROOT / "subsystems" / "experience" / "engines" / "localization.py"
        self.assertTrue(localization.is_file())
        self.assertFalse((ROOT / "subsystems" / "localization").exists())
        self.assertFalse((ROOT / "foundation").exists())
        architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("Subsystem", architecture)
        self.assertIn("Engine", architecture)
        self.assertIn("Function", architecture)


if __name__ == "__main__":
    unittest.main()