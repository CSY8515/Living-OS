from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from subsystems.experience.engines.theme import OFFICIAL_UI_CSS


ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "subsystems" / "experience" / "engines" / "design_system.py"
PAGES = ROOT / "subsystems" / "experience" / "engines" / "pages.py"
SHELL = ROOT / "subsystems" / "experience" / "engines" / "shell.py"


class OfficialUiRefinementTests(unittest.TestCase):
    def test_version_is_final_release(self) -> None:
        version = (ROOT / "VERSION.md").read_text(encoding="utf-8")
        self.assertIn("Workspace version: Living OS v2.0.9.7", version)
        self.assertIn("Production release: Living OS v2.0.9.7", version)
        self.assertIn("Theme World Integration Hotfix", version)

    def test_structural_design_components_exist_in_experience_engine(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        for function in (
            "navigation_identity", "system_banner", "page_header", "home_world",
            "metric_deck", "workspace_rail", "record_gallery", "state_panel",
        ):
            with self.subTest(function=function):
                self.assertIn(f"def {function}(", design)
        self.assertIn("los-world-style-layer", design)
        self.assertIn('st.image(str(WORLD_ASSET), width="stretch")', design)
        self.assertNotIn("los-world-overlay-repair", design)
        self.assertIn("living-os-v2092-official-style-clean.png", design)

    def test_key_screens_use_new_information_hierarchy(self) -> None:
        pages = PAGES.read_text(encoding="utf-8")
        for marker in (
            "MEMORY ORBIT / TIMELINE", "LIVING INDEX / SEARCH",
            "MEMORY ATLAS / REPORT", "LIFE OBSERVATORY / ANALYTICS",
            "SYSTEM CONSTELLATION / MODULES", "SYSTEM SANCTUM / SETTINGS",
            "record_gallery", "workspace_rail", "metric_deck",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, pages)
        shell = SHELL.read_text(encoding="utf-8")
        self.assertIn("official_user_navigation", shell)

    def test_premium_interaction_contract_is_complete(self) -> None:
        for marker in (
            ":hover", ":focus-visible", ":active", "backdrop-filter", "blur(",
            "los-ripple", "los-enter-refined", "los-chrome-sweep", "los-float",
            "los-orbit", "transition:", "stDialog", "stToast",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, OFFICIAL_UI_CSS)

    def test_responsive_and_reduced_motion_contract_is_complete(self) -> None:
        for marker in (
            "@media(max-width:1280px)", "@media(max-width:1024px)",
            "@media(max-width:760px)", "@media(max-width:480px)",
            "prefers-reduced-motion", "final responsive orbit refinement",
            "@media(max-width:1024px) and (min-width:761px)",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, OFFICIAL_UI_CSS)

    def test_refined_primary_screens_render_without_errors(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
        self.assertFalse(app.exception)
        for page in ("Command Center", "Timeline", "Search", "Reports", "Analytics", "Finance", "Health"):
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.assertFalse(app.exception)

    def test_architecture_boundary_remains_unchanged(self) -> None:
        self.assertFalse((ROOT / "foundation").exists())
        self.assertFalse((ROOT / "subsystems" / "ui").exists())
        self.assertTrue(DESIGN.is_file())
        architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for layer in ("Subsystem", "Engine", "Function"):
            self.assertIn(layer, architecture)


if __name__ == "__main__":
    unittest.main()
