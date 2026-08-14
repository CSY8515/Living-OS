from __future__ import annotations

from pathlib import Path
import unittest

from subsystems.experience.engines.ultra_brain_world import (
    build_theme_settings,
    parse_inherited_world,
    resolve_visual_asset,
)


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

    def test_registered_finance_feature_background_resolves_independently(self) -> None:
        world = parse_inherited_world(
            query(
                asset_registry="ui-theme-registry",
                asset_registry_version="1.0.0",
                project_id="living-os",
                feature_id="finance",
                visual_role="FEATURE_BACKGROUND",
                asset_revision="2",
            )
        )
        self.assertIsNotNone(world)
        path, source, fallback = resolve_visual_asset(
            world, "FEATURE_BACKGROUND", "finance"
        )
        self.assertEqual(
            path,
            ROOT / "assets" / "theme-role-assets" / "dark" / "finance-background.png",
        )
        self.assertEqual(source, "theme-project-feature-role")
        self.assertEqual(fallback, "NONE")

    def test_unregistered_feature_still_fails_closed(self) -> None:
        world = parse_inherited_world(
            query(
                asset_registry="ui-theme-registry",
                asset_registry_version="1.0.0",
                project_id="living-os",
                feature_id="vehicle",
                visual_role="FEATURE_BACKGROUND",
                asset_revision="2",
            )
        )
        self.assertIsNotNone(world)
        path, source, fallback = resolve_visual_asset(
            world, "FEATURE_BACKGROUND", "vehicle"
        )
        self.assertIsNone(path)
        self.assertEqual(source, "missing-role-asset")
        self.assertEqual(fallback, "ASSET REQUIRED")


if __name__ == "__main__":
    unittest.main()
