from __future__ import annotations

from pathlib import Path
import unittest

from subsystems.experience.engines.ultra_brain_world import (
    build_theme_settings,
    parse_inherited_world,
    resolve_visual_asset,
)
from subsystems.experience.engines.theme_adapter import ThemeAdapter
from subsystems.experience.engines.ui_registry import DEFAULT_UI_REGISTRY


ROOT = Path(__file__).resolve().parents[1]


def query(**extra: object) -> dict[str, object]:
    return {
        "source": "ultra-brain",
        "contract": "ultra-brain.ui/v1",
        "interface": "1.0",
        "theme": "dark",
        "world": "quiet-canopy-world",
        "revision": "2",
        "target": "living-os",
        **extra,
    }


class LivingRoleThemeAssetPathTests(unittest.TestCase):
    def test_asset_only_contract_preserves_original_functional_ui(self) -> None:
        adapter = ThemeAdapter()
        official = DEFAULT_UI_REGISTRY.theme("living-os-dark").to_payload()
        official["assets"]["background.module.finance"] = "assets/theme-role-assets/dark/finance-background.png"
        rendered = adapter.render(".original-functional-ui{color:#f3eddc}", official)
        self.assertIn(".original-functional-ui{color:#f3eddc}", rendered)
        self.assertIn('data-living-os-ui-contract="v2.096"', rendered)
        self.assertNotIn("--los-font-sans", rendered)
        self.assertNotIn("--los-card-radius", rendered)
        self.assertNotIn('[data-testid="stMetric"]', rendered)
        self.assertNotIn('[data-baseweb="input"]', rendered)

    def test_explicit_full_dark_contract_keeps_ui_contract_active(self) -> None:
        adapter = ThemeAdapter()
        explicit = DEFAULT_UI_REGISTRY.theme("living-os-dark").to_payload()
        explicit["source"] = "ultra-brain"
        rendered = adapter.render(".original-functional-ui{color:#f3eddc}", explicit)
        self.assertIn("--los-font-sans", rendered)
        self.assertIn("--los-card-radius", rendered)
        self.assertIn('[data-testid="stMetric"]', rendered)
        self.assertIn('[data-baseweb="input"]', rendered)

    def test_registered_dark_home_resolves_into_existing_background_slot(self) -> None:
        world = parse_inherited_world(
            query(
                asset_registry="ui-theme-registry",
                asset_registry_version="1.0.0",
                project_id="living-os",
                visual_role="HOME_BACKGROUND",
                asset_revision="2",
            )
        )
        self.assertIsNotNone(world)
        path, source, fallback = resolve_visual_asset(world, "HOME_BACKGROUND")
        self.assertEqual(path, ROOT / "assets" / "inherited-worlds" / "dark.png")
        self.assertEqual(source, "theme-project-role")
        self.assertEqual(fallback, "NONE")
        settings = build_theme_settings(world)
        self.assertEqual(Path(settings["assets"]["background.home"]), path)
        self.assertEqual(
            Path(settings["assets"]["navigation.object.skin"]),
            ROOT / "assets" / "theme-role-assets" / "dark" / "navigation-object-skin.png",
        )
        self.assertEqual(
            Path(settings["assets"]["background.module.finance"]),
            ROOT / "assets" / "theme-role-assets" / "dark" / "finance-background.png",
        )
        self.assertEqual(
            Path(settings["assets"]["background.module.health"]),
            ROOT / "assets" / "theme-role-assets" / "dark" / "health-background.png",
        )
        for feature_id in (
            "job", "housing", "investment", "knowledge", "routine",
            "vehicle", "growth", "food",
        ):
            self.assertEqual(
                Path(settings["assets"][f"background.module.{feature_id}"]),
                ROOT / "assets" / "theme-role-assets" / "dark" / f"{feature_id}-background.png",
            )

    def test_revision_one_cannot_claim_revision_two_registration(self) -> None:
        world = parse_inherited_world(
            query(
                asset_registry="ui-theme-registry",
                asset_registry_version="1.0.0",
                project_id="living-os",
                visual_role="HOME_BACKGROUND",
                asset_revision="1",
            )
        )
        self.assertIsNotNone(world)
        _path, source, fallback = resolve_visual_asset(world, "HOME_BACKGROUND")
        self.assertEqual(source, "legacy-theme-asset")
        self.assertEqual(fallback, "FALLBACK USED")

    def test_legacy_dark_home_still_works_without_role_metadata(self) -> None:
        world = parse_inherited_world(query())
        self.assertIsNotNone(world)
        path, source, fallback = resolve_visual_asset(world, "HOME_BACKGROUND")
        self.assertTrue(path.is_file())
        self.assertEqual(source, "legacy-theme-asset")
        self.assertEqual(fallback, "FALLBACK USED")

    def test_registered_calm_home_uses_existing_asset_without_faking_features(self) -> None:
        world = parse_inherited_world(
            query(
                theme="calm",
                world="calm-wetland-world",
                asset_registry="ui-theme-registry",
                asset_registry_version="1.0.0",
                project_id="living-os",
                visual_role="HOME_BACKGROUND",
                asset_revision="2",
            )
        )
        self.assertIsNotNone(world)
        path, source, fallback = resolve_visual_asset(world, "HOME_BACKGROUND")
        self.assertEqual(path, ROOT / "assets" / "inherited-worlds" / "calm.png")
        self.assertEqual(source, "theme-project-role")
        self.assertEqual(fallback, "NONE")
        settings = build_theme_settings(world)
        self.assertEqual(Path(settings["assets"]["background.home"]), path)
        self.assertNotIn("background.module.finance", settings["assets"])
        feature_path, feature_source, feature_fallback = resolve_visual_asset(
            world, "FEATURE_BACKGROUND", "finance"
        )
        self.assertIsNone(feature_path)
        self.assertEqual(feature_source, "missing-role-asset")
        self.assertEqual(feature_fallback, "ASSET REQUIRED")

    def test_all_ten_registered_feature_backgrounds_resolve_independently(self) -> None:
        for feature_id in (
            "finance", "health", "job", "housing", "investment",
            "knowledge", "routine", "vehicle", "growth", "food",
        ):
            world = parse_inherited_world(
                query(
                    asset_registry="ui-theme-registry",
                    asset_registry_version="1.0.0",
                    project_id="living-os",
                    feature_id=feature_id,
                    visual_role="FEATURE_BACKGROUND",
                    asset_revision="2",
                )
            )
            self.assertIsNotNone(world)
            path, source, fallback = resolve_visual_asset(
                world, "FEATURE_BACKGROUND", feature_id
            )
            self.assertEqual(
                path,
                ROOT / "assets" / "theme-role-assets" / "dark" / f"{feature_id}-background.png",
            )
            self.assertEqual(source, "theme-project-feature-role")
            self.assertEqual(fallback, "NONE")

    def test_unregistered_feature_still_fails_closed(self) -> None:
        world = parse_inherited_world(
            query(
                asset_registry="ui-theme-registry",
                asset_registry_version="1.0.0",
                project_id="living-os",
                feature_id="collaboration",
                visual_role="FEATURE_BACKGROUND",
                asset_revision="2",
            )
        )
        self.assertIsNotNone(world)
        path, source, fallback = resolve_visual_asset(
            world, "FEATURE_BACKGROUND", "collaboration"
        )
        self.assertIsNone(path)
        self.assertEqual(source, "missing-role-asset")
        self.assertEqual(fallback, "ASSET REQUIRED")


if __name__ == "__main__":
    unittest.main()
