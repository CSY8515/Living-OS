from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from subsystems.experience.engines.shell import FEATURE_PAGES, USER_PAGE_ORDER
from subsystems.experience.engines.theme import OFFICIAL_UI_CSS


ROOT = Path(__file__).resolve().parent.parent
SHELL = ROOT / "subsystems" / "experience" / "engines" / "shell.py"
PAGES = ROOT / "subsystems" / "experience" / "engines" / "pages.py"
DESIGN = ROOT / "subsystems" / "experience" / "engines" / "design_system.py"


class OfficialConceptUiTests(unittest.TestCase):
    def test_candidate_version_and_release_boundary(self) -> None:
        version = (ROOT / "VERSION.md").read_text(encoding="utf-8")
        self.assertIn("Workspace version: Living OS v2.0.9.7", version)
        self.assertIn("Production release: Living OS v2.0.9.7", version)
        self.assertIn("Theme World Integration Hotfix", version)

    def test_general_user_navigation_exposes_only_life_surfaces(self) -> None:
        forbidden = {
            "Archive", "Review", "Documents", "Knowledge Management",
            "Routine Management", "Investment Management", "Job Management",
            "Personal Growth Management", "Collaboration Management", "Database",
            "Database Management", "Module Manager", "Settings", "Collaboration",
        }
        self.assertEqual(len(USER_PAGE_ORDER), 18)
        self.assertTrue(FEATURE_PAGES.issubset(set(USER_PAGE_ORDER)))
        self.assertTrue(forbidden.isdisjoint(USER_PAGE_ORDER))
        shell = SHELL.read_text(encoding="utf-8")
        self.assertIn('initial_sidebar_state="collapsed"', shell)
        self.assertIn("official_user_navigation", shell)

    def test_sidebar_is_hidden_and_custom_navigation_is_responsive(self) -> None:
        required = (
            '[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{display:none!important}',
            "st-key-official_user_navigation", "los-user-navigation",
            "@media(max-width:1280px)", "@media(max-width:1024px)",
            "@media(max-width:760px)", "@media(max-width:480px)",
            "overflow-x:auto", "prefers-reduced-motion",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, OFFICIAL_UI_CSS)

    def test_final_answer_image_is_the_first_screen_structure(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        pages = PAGES.read_text(encoding="utf-8")
        for marker in ("los-world-stage", "los-world-style-layer", 'st.image(str(WORLD_ASSET), width="stretch")'):
            self.assertIn(marker, design)
        self.assertIn('WORLD_ASSET = ROOT / "assets" / "living-os-v2092-official-style-clean.png"', design)
        self.assertNotIn("los-world-overlay-repair", design)
        asset = ROOT / "assets" / "living-os-v2092-official-style-clean.png"
        self.assertTrue(asset.exists())
        self.assertGreater(asset.stat().st_size, 1_000_000)
        for key in (
            "finance", "investment", "job", "health", "housing",
            "food", "knowledge", "routine", "growth",
        ):
            self.assertIn(f'"{key}"', pages)
        dashboard = pages.split("def render_dashboard", 1)[1].split("def render_personal_growth", 1)[0]
        self.assertIn('"Vehicle", "vehicle"', dashboard)
        self.assertIn('("의사결정 로그", "Decision Log", "decision")', dashboard)
        self.assertIn('key="world_enter"', dashboard)
        self.assertNotIn('"Collaboration", "collaboration"', dashboard)

    def test_final_answer_layout_uses_ten_orbital_hotspots(self) -> None:
        positions = {
            "finance": "left:23.4%!important", "health": "right:23.2%!important",
            "job": "left:11.1%!important", "housing": "right:10.9%!important",
            "investment": "left:4.7%!important", "food": "right:4.6%!important",
            "knowledge": "left:17.1%!important", "growth": "right:17.0%!important",
            "routine": "left:36.3%!important",
            "vehicle": "left:51.3%!important",
        }
        for key, position in positions.items():
            self.assertIn(f"st-key-world_node_{key}", OFFICIAL_UI_CSS)
            self.assertIn(position, OFFICIAL_UI_CSS)
        self.assertIn("v2.0.9.2 final visible labels, orbital alignment", OFFICIAL_UI_CSS)
        self.assertIn("aspect-ratio:1376/918", OFFICIAL_UI_CSS)
        self.assertIn(":has(img)", OFFICIAL_UI_CSS)
        self.assertIn("object-fit:fill!important", OFFICIAL_UI_CSS)
        self.assertNotIn("los-world-overlay-repair", OFFICIAL_UI_CSS)
        self.assertIn("los-world-object-vehicle", OFFICIAL_UI_CSS)
        self.assertNotIn("st-key-world_node_vehicle{display:none!important}", OFFICIAL_UI_CSS)
        self.assertIn("left:51.3%!important", OFFICIAL_UI_CSS)
        self.assertIn("top:66.1%!important", OFFICIAL_UI_CSS)
        self.assertIn("width:12%!important", OFFICIAL_UI_CSS)
        self.assertIn("height:18.7%!important", OFFICIAL_UI_CSS)
        self.assertIn('button:before{display:block!important', OFFICIAL_UI_CSS)

    def test_first_screen_has_no_management_dashboard_or_reinterpreted_world(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        pages = PAGES.read_text(encoding="utf-8")
        self.assertNotIn("los-world-core", design)
        self.assertNotIn("los-life-dome", design)
        self.assertNotIn("los-world-horizon", design)
        self.assertNotIn("los-world-paths", design)
        self.assertIn("Every function continues as a place in the same world", OFFICIAL_UI_CSS)
        dashboard = pages.split("def render_dashboard", 1)[1].split("def render_personal_growth", 1)[0]
        self.assertNotIn("LIVING SIGNAL MATRIX", dashboard)
        self.assertNotIn("dashboard_quick_", dashboard)
        self.assertNotIn("최근 활동", dashboard)

    def test_home_preserves_nine_blueprint_spaces_and_adds_vehicle_orbit(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("imgs")), 1)
        home_markup = "".join(str(markdown.value) for markdown in app.markdown)
        self.assertIn("los-world-stage", home_markup)
        labels = {button.label for button in app.button}
        for label in (
            "◒  재무", "▱  직업", "↗  투자", "◫  지식", "↻  루틴",
            "△  자기계발", "◒  식사", "⌂  주거", "♡  건강", "◇  차량", "입장 →",
        ):
            self.assertIn(label, labels)
        self.assertFalse(any("협업" in label for label in labels))
        next(button for button in app.button if button.label == "입장 →").click().run()
        self.assertEqual(app.sidebar.radio[0].value, "Daily Log")

        vehicle_app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        vehicle_app.sidebar.radio[0].set_value("Vehicle").run()
        self.assertEqual(vehicle_app.sidebar.radio[0].value, "Vehicle")
        self.assertFalse(vehicle_app.exception)
    def test_every_life_function_has_a_distinct_scene(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        for scene in (
            "finance", "investment", "job", "health", "vehicle", "housing",
            "food", "knowledge", "routine", "growth",
            "timeline", "reports", "analytics", "search",
        ):
            with self.subTest(scene=scene):
                self.assertIn(f'"{scene}"', design)
                self.assertIn(f"los-scene-{scene}", OFFICIAL_UI_CSS)
        for object_name in (
            "재무 금고", "투자 관측소", "커리어 정거장", "건강 생체 정원",
            "모빌리티 베이", "생활 주거 공간", "식생활 아틀리에", "지식 서고",
            "리듬 순환실", "성장 온실",
        ):
            self.assertIn(object_name, design)

    def test_internal_backends_are_preserved_but_not_navigable(self) -> None:
        shell = SHELL.read_text(encoding="utf-8")
        for renderer in (
            "render_database", "render_database_management", "render_module_manager",
            "render_settings", "render_investment_management", "render_job_management",
        ):
            self.assertIn(renderer, shell)
        self.assertNotIn("migration_tab", PAGES.read_text(encoding="utf-8"))
        self.assertNotIn("Legacy Finance migration", PAGES.read_text(encoding="utf-8"))
        self.assertIn('"Collaboration": lambda: render_collaboration', shell)

    def test_all_user_surfaces_render_without_runtime_errors(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.sidebar.radio[0].options), len(USER_PAGE_ORDER))
        self.assertNotIn("데이터베이스", " ".join(app.sidebar.radio[0].options))
        self.assertNotIn("모듈 관리", " ".join(app.sidebar.radio[0].options))
        for page in USER_PAGE_ORDER:
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.get("json")), 0)
                self.assertEqual(len(app.get("dataframe")), 0)
                self.assertEqual(len(app.get("code")), 0)

    def test_subsystem_world_assets_and_official_user_surfaces(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        pages = PAGES.read_text(encoding="utf-8")
        asset_names = (
            "finance", "investment", "job", "health", "vehicle",
            "housing", "food", "knowledge", "routine", "growth",
        )
        self.assertIn("SUBSYSTEM_WORLD_ASSETS", design)
        self.assertIn("los-subsystem-world-hero", design)
        self.assertIn('class="los-fixed-world-backdrop"', design)
        self.assertIn('<img src="{asset_uri}"', design)
        self.assertIn("los-world-threshold", design)
        for name in asset_names:
            with self.subTest(world=name):
                asset = ROOT / "assets" / "subsystem-worlds" / f"{name}-world.png"
                self.assertTrue(asset.exists())
                self.assertGreater(asset.stat().st_size, 1_000_000)
                self.assertIn(f'"{name}": ROOT / "assets" / "subsystem-worlds" / "{name}-world.png"', design)
        for marker in (
            "Subsystem World Continuity", "st-key-subsystem_world_hero_",
            "los-insight-canvas", "los-data-canvas", "los-subsystem-arrival",
            "Full Subsystem World Shell", "subsystem_world_backdrop_",
            "los-world-threshold", '[data-baseweb="tab-panel"]',
            "Official document surface", "los-document-canvas",
            "object-position:center right", "@media(max-width:760px)",
        ):
            self.assertIn(marker, OFFICIAL_UI_CSS)
        for renderer in (
            "render_investment_subsystem", "render_job_subsystem",
            "render_knowledge_subsystem", "render_routine_subsystem",
            "render_personal_growth", "render_finance", "render_health",
            "render_housing", "render_vehicle", "render_food",
        ):
            start = pages.index(f"def {renderer}(")
            end = pages.find("\ndef ", start + 5)
            segment = pages[start:] if end < 0 else pages[start:end]
            with self.subTest(renderer=renderer):
                self.assertNotIn(".json(", segment)
                self.assertNotIn(".dataframe(", segment)
                self.assertNotIn(".code(", segment)
                self.assertIn("official_records", segment)

    def test_subsystem_worlds_render_with_artwork_and_without_exceptions(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        for page in (
            "Finance", "Investment", "Job", "Health", "Vehicle",
            "Housing", "Food", "Knowledge", "Routine", "Personal Growth",
        ):
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.get("imgs")), 0)
                markup = "".join(str(markdown.value) for markdown in app.markdown)
                self.assertIn("los-fixed-world-backdrop", markup)
                self.assertIn("los-subsystem-world-hero", markup)
    def test_architecture_boundary_is_unchanged(self) -> None:
        self.assertFalse((ROOT / "foundation").exists())
        self.assertFalse((ROOT / "subsystems" / "ui").exists())
        architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for layer in ("Subsystem", "Engine", "Function"):
            self.assertIn(layer, architecture)


if __name__ == "__main__":
    unittest.main()
