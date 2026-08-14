from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from subsystems.experience import LIVING_OS_UI, LivingOSUIInterface
from subsystems.experience.engines.theme import OFFICIAL_UI_CSS
from subsystems.experience.engines.theme_adapter import ThemeAdapter
from subsystems.experience.engines.ui_contracts import (
    UI_CONTRACT_ID,
    UI_CONTRACT_VERSION,
)
from subsystems.experience.engines.ui_registry import DEFAULT_UI_REGISTRY
from tests.test_streamlit import PAGES


ROOT = Path(__file__).resolve().parent.parent
V2098_OFFICIAL_CSS_SHA256 = (
    "292071ac441b24e16003829b461bb8bd8c244ced0e7a1d1d6b1fa13413e4756b"
)


class UIFoundationCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = ThemeAdapter()

    def test_v2098_official_visual_css_is_locked(self) -> None:
        digest = hashlib.sha256(OFFICIAL_UI_CSS.encode("utf-8")).hexdigest()
        self.assertEqual(digest, V2098_OFFICIAL_CSS_SHA256)
        default = self.adapter.render(OFFICIAL_UI_CSS, {})
        self.assertTrue(default.startswith(OFFICIAL_UI_CSS))
        self.assertIn('data-living-os-ui-contract="v2.096"', default)

    def test_registry_matches_checked_in_contract(self) -> None:
        registry = json.loads(
            (ROOT / "config" / "ui_integration_registry.json").read_text(
                encoding="utf-8"
            )
        )
        audit = DEFAULT_UI_REGISTRY.audit()
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(registry["contract_id"], UI_CONTRACT_ID)
        self.assertEqual(registry["contract_version"], UI_CONTRACT_VERSION)
        self.assertEqual(
            set(registry["components"]), set(DEFAULT_UI_REGISTRY.component_ids())
        )
        self.assertEqual(set(registry["modules"]), set(DEFAULT_UI_REGISTRY.module_ids()))
        registered_pages = {
            page
            for module_id in DEFAULT_UI_REGISTRY.module_ids()
            for page in DEFAULT_UI_REGISTRY.module(module_id).pages
        }
        self.assertTrue(set(PAGES).issubset(registered_pages))

    def test_theme_contract_accepts_supported_ultra_brain_settings(self) -> None:
        settings = {
            "source": "ultra-brain",
            "theme_id": "ultra-brain-owner-theme",
            "mode": "light",
            "design_tokens": {
                "color": {"accent": "#123456", "accent_bright": "#345678"},
                "typography": {"font_sans": '"Inter",sans-serif'},
                "shape": {"card_radius": "24px"},
                "shadow": {"card": "0 8px 24px rgba(0,0,0,.18)"},
                "layout": {"max_width": "1440px"},
                "motion": {"enabled": False, "scale": 0},
            },
            "component_overrides": {
                "card": {"border-radius": "24px"},
                "button": {"border-radius": "12px"},
                "dialog": {"border-radius": "24px"},
                "widget": {"border-radius": "12px"},
                "dashboard": {"border-radius": "24px"},
            },
            "module_overrides": {
                "finance": {
                    "accent": "#abcdef",
                    "background_image": "linear-gradient(#101820,#182430)",
                }
            },
            "assets": {"background.home": "https://example.com/world.png"},
            "icons": {"navigation.Finance": "F"},
        }
        contract = self.adapter.resolve(settings)
        css = self.adapter.render(OFFICIAL_UI_CSS, settings)
        self.assertEqual(contract.theme_id, "ultra-brain-owner-theme")
        self.assertEqual(contract.mode, "light")
        for marker in (
            "color-scheme:light",
            "--los-gold:#123456",
            '--los-font-sans:"Inter",sans-serif',
            "--los-card-radius:24px",
            "--los-layout-max-width:1440px",
            ".los-ui-scope-finance",
            "animation:none!important",
        ):
            self.assertIn(marker, css)
        self.assertEqual(
            self.adapter.asset("background.home", "fallback", contract),
            "https://example.com/world.png",
        )
        self.assertEqual(self.adapter.icon("navigation.Finance", "◐", contract), "F")

    def test_dark_light_and_system_modes_have_registered_bases(self) -> None:
        dark = self.adapter.resolve({"mode": "dark"})
        light = self.adapter.resolve({"mode": "light"})
        system_css = self.adapter.render(OFFICIAL_UI_CSS, {"mode": "system"})
        self.assertEqual(dark.design_tokens.values["color"]["background"], "#02070b")
        self.assertEqual(light.design_tokens.values["color"]["background"], "#f4f1e8")
        self.assertIn("color-scheme:light dark", system_css)

    def test_unregistered_or_unsafe_overrides_are_rejected(self) -> None:
        invalid_settings = (
            {"unknown": True},
            {"component_overrides": {"unknown": {"color": "red"}}},
            {"component_overrides": {"card": {"display": "none"}}},
            {"module_overrides": {"unknown": {"accent": "#fff"}}},
            {"module_overrides": {"finance": {"unknown": "#fff"}}},
            {"design_tokens": {"color": {"accent": "red;display:none"}}},
            {"design_tokens": {"color": {"accent": "expression(alert(1))"}}},
            {"assets": {"background.home": 'https://example.com/" onerror="x'}},
            {"assets": {"background.home": "data:text/html;base64,PHNjcmlwdD4="}},
            {"icons": {"navigation.Finance": "<script>"}},
        )
        for settings in invalid_settings:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                self.adapter.resolve(settings)

    def test_every_registered_module_can_receive_scoped_tokens(self) -> None:
        overrides = {
            module_id: {"accent": "#aabbcc"}
            for module_id in DEFAULT_UI_REGISTRY.module_ids()
        }
        css = self.adapter.render(OFFICIAL_UI_CSS, {"module_overrides": overrides})
        for module_id in DEFAULT_UI_REGISTRY.module_ids():
            self.assertIn(f".los-ui-scope-{module_id}", css)
            marker = LIVING_OS_UI.scope_marker(module_id)
            self.assertIn("hidden", marker)
            self.assertIn(f"los-ui-scope-{module_id}", marker)

    def test_default_assets_and_icons_keep_existing_fallbacks(self) -> None:
        contract = self.adapter.resolve({})
        self.assertEqual(self.adapter.asset("background.home", "existing.png", contract), "existing.png")
        self.assertEqual(self.adapter.icon("navigation.Finance", "◐", contract), "◐")

    def test_public_interface_is_experience_only_and_reports_pass(self) -> None:
        interface = LivingOSUIInterface()
        audit = interface.audit()
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(audit["contract"], "ultra-brain.ui/v1")
        source = (
            ROOT / "subsystems" / "experience" / "engines" / "ui_interface.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("subsystems.foundation", source)
        self.assertNotIn("subsystems.operations", source)
        self.assertNotIn("subsystems.insight", source)
        self.assertNotIn("subsystems.database", source)

    def test_default_streamlit_world_renders_without_contract_errors(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn("los-ui-scope-dashboard", rendered)
        self.assertNotIn("Ultra Brain UI", rendered)


if __name__ == "__main__":
    unittest.main()
