from __future__ import annotations

import json
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

from subsystems.experience.engines.design_system import SUBSYSTEM_WORLD_ASSETS
from subsystems.experience.engines.living_world import (
    FEATURE_NAVIGATION_SHAPES,
    FEATURE_WORLD_IDENTITY,
    THEME_WORLD_LANGUAGE,
    build_living_world_definition,
    living_world_css,
)
from subsystems.experience.engines.ultra_brain_world import (
    PROPAGATION_TARGETS,
    WORLD_ASSETS,
    build_theme_settings,
    inherited_world_css,
    parse_inherited_world,
)


ROOT = Path(__file__).resolve().parents[1]


def inherited_query(theme: str, **values: object) -> dict[str, object]:
    return {
        "source": "ultra-brain",
        "contract": "ultra-brain.ui/v1",
        "interface": "1.0",
        "revision": "0.985",
        "theme": theme,
        "world": f"{theme}-living-world",
        **values,
    }


class ThemeWorldIntegrationTests(unittest.TestCase):
    def definition(self, theme: str):
        return build_living_world_definition(
            theme_id=theme,
            world_id=f"{theme}-living-world",
            home_asset=str(WORLD_ASSETS[theme]),
            feature_assets=SUBSYSTEM_WORLD_ASSETS,
        )

    def test_world_registry_covers_current_scenes_and_distinct_pilot_features(self) -> None:
        self.assertEqual(set(FEATURE_WORLD_IDENTITY), {
            "living", "finance", "investment", "job", "health", "vehicle",
            "housing", "food", "knowledge", "routine", "growth", "collaboration",
            "timeline", "reports", "analytics", "search", "today", "decision",
            "assistant",
        })
        definition = self.definition("calm")
        pilots = [definition.feature(name) for name in ("finance", "health", "vehicle")]
        self.assertEqual({item.asset for item in pilots}, {definition.home_asset})
        self.assertEqual({item.asset_state for item in pilots}, {"parent-world-fallback"})
        self.assertTrue(all(item.theme_asset_required for item in pilots))
        self.assertEqual(len({item.main_object for item in pilots}), 3)
        self.assertEqual(len({item.navigation_object for item in pilots}), 3)
        self.assertEqual(len({item.composition for item in pilots}), 3)

    def test_theme_languages_change_world_composition_not_only_color(self) -> None:
        calm = self.definition("calm")
        ocean = self.definition("ocean")
        self.assertNotEqual(calm.home_asset, ocean.home_asset)
        self.assertNotEqual(calm.language.composition, ocean.language.composition)
        self.assertNotEqual(calm.language.frame, ocean.language.frame)
        self.assertNotEqual(calm.language.lighting, ocean.language.lighting)
        self.assertNotEqual(calm.language.texture, ocean.language.texture)
        self.assertNotEqual(calm.language.material, ocean.language.material)
        self.assertNotEqual(calm.language.effects, ocean.language.effects)

    def test_missing_theme_feature_art_uses_declared_parent_world_fallback(self) -> None:
        state = parse_inherited_world(inherited_query("calm"))
        assert state is not None
        settings = build_theme_settings(state)
        self.assertEqual(settings["assets"], {"background.home": str(WORLD_ASSETS["calm"])})
        definition = self.definition("calm")
        for scene in ("finance", "health", "vehicle"):
            feature = definition.feature(scene)
            self.assertEqual(feature.asset, definition.home_asset)
            self.assertNotEqual(feature.asset, str(SUBSYSTEM_WORLD_ASSETS[scene]))
            self.assertEqual(feature.asset_state, "parent-world-fallback")
            self.assertTrue(feature.theme_asset_required)

    def test_root_theme_filter_excludes_reused_official_feature_art(self) -> None:
        state = parse_inherited_world(inherited_query("calm", brightness=1.2, hue=12.0))
        assert state is not None
        css = inherited_world_css(state)
        scope = '.los-world-scene-scope:not([data-feature-asset-state="reused-official-feature"])'
        self.assertIn(f"{scope} .los-fixed-world-backdrop img", css)
        self.assertIn(f"{scope} .los-subsystem-world-hero>img", css)
        self.assertNotIn(
            ".los-fixed-world-backdrop img,.los-subsystem-world-hero>img{",
            css,
        )

    def test_navigation_identity_uses_distinct_shapes_and_keeps_responsive_contract(self) -> None:
        self.assertEqual(len(FEATURE_NAVIGATION_SHAPES), 10)
        self.assertEqual(len(set(FEATURE_NAVIGATION_SHAPES.values())), 10)
        css = living_world_css("calm")
        for feature in ("finance", "health", "vehicle"):
            self.assertIn(f".st-key-world_node_{feature}", css)
        self.assertIn("@media(max-width:760px)", css)
        self.assertIn(".los-user-navigation", css)
        self.assertIn('[data-testid="stMetric"]', css)
        self.assertIn(".stButton>button", css)

    def test_source_has_no_root_asset_fanout_or_cloned_navigation_object(self) -> None:
        world_source = (ROOT / "subsystems/experience/engines/ultra_brain_world.py").read_text(encoding="utf-8")
        design_source = (ROOT / "subsystems/experience/engines/design_system.py").read_text(encoding="utf-8")
        self.assertNotIn('assets.update({f"background.module.', world_source)
        self.assertNotIn('class="los-world-object-clone', design_source)
        self.assertIn("data-main-object", design_source)
        self.assertIn("data-feature-composition", design_source)

    def test_calm_home_and_three_features_render_real_world_definitions(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        for key, value in inherited_query("calm").items():
            app.query_params[key] = value
        app.run()
        self.assertFalse(app.exception)
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn('data-living-world-context="home"', rendered)
        self.assertIn('data-theme-composition="wetland-haven"', rendered)
        self.assertNotIn("OS ECOSYSTEM / LIVING", rendered)

        seen: dict[str, str] = {}
        for page in ("Finance", "Health", "Vehicle"):
            app.sidebar.radio[0].set_value(page).run()
            self.assertFalse(app.exception)
            rendered = "\n".join(str(item.value) for item in app.markdown)
            feature = page.lower()
            self.assertIn(f'data-feature-id="{feature}"', rendered)
            self.assertIn('data-theme-composition="wetland-haven"', rendered)
            self.assertIn('data-feature-asset-state="parent-world-fallback"', rendered)
            marker = next(
                item for item in rendered.split("data-feature-composition=")
                if f'data-feature-id="{feature}"' in rendered
            )
            seen[feature] = marker[:80]
        self.assertEqual(len(seen), 3)

    def test_theme_switch_changes_home_and_feature_world_language(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        for key, value in inherited_query("calm").items():
            app.query_params[key] = value
        app.run()
        calm = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn('data-theme-composition="wetland-haven"', calm)

        for key, value in inherited_query("ocean", revision="0.986").items():
            app.query_params[key] = value
        app.run()
        ocean = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn('data-theme-composition="tidal-domain"', ocean)
        self.assertNotIn('data-theme-composition="wetland-haven"', ocean)
        app.sidebar.radio[0].set_value("Finance").run()
        feature = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn('data-theme-composition="tidal-domain"', feature)
        self.assertIn('data-feature-id="finance"', feature)

    def test_lock_keeps_active_theme_during_incoming_revision(self) -> None:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        for key, value in inherited_query("calm").items():
            app.query_params[key] = value
        app.run()
        locked_query = inherited_query(
            "lava",
            revision="0.986",
            propagationTargets=json.dumps(list(PROPAGATION_TARGETS)),
            propagationLocks=json.dumps({"living-os": list(PROPAGATION_TARGETS)}),
        )
        for key, value in locked_query.items():
            app.query_params[key] = value
        app.run()
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn('data-theme-composition="wetland-haven"', rendered)
        self.assertNotIn('data-theme-composition="forged-domain"', rendered)


if __name__ == "__main__":
    unittest.main()
