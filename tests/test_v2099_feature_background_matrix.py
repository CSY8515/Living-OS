from __future__ import annotations

from pathlib import Path
import unittest

from subsystems.experience.engines.design_system import SUBSYSTEM_WORLD_ASSETS
from subsystems.experience.engines.living_world import build_living_world_definition
from subsystems.experience.engines.ultra_brain_world import (
    build_theme_settings,
    parse_inherited_world,
    resolve_visual_asset,
)


ROOT = Path(__file__).resolve().parents[1]
FEATURES = (
    "finance",
    "investment",
    "job",
    "health",
    "vehicle",
    "housing",
    "food",
    "knowledge",
    "routine",
    "growth",
)
DEDICATED_DARK = {
    feature: ROOT / "assets" / "theme-role-assets" / "dark" / f"{feature}-background.png"
    for feature in FEATURES
}


def query(**extra: object) -> dict[str, object]:
    return {
        "source": "ultra-brain",
        "contract": "ultra-brain.ui/v1",
        "interface": "1.0",
        "theme": "dark",
        "world": "quiet-canopy-world",
        "revision": "2",
        "target": "living-os",
        "asset_registry": "ui-theme-registry",
        "asset_registry_version": "1.0.0",
        "project_id": "living-os",
        "visual_role": "HOME_BACKGROUND",
        "asset_revision": "2",
        **extra,
    }


def dark_definition():
    inherited = parse_inherited_world(query())
    assert inherited is not None
    settings = build_theme_settings(inherited)
    assets = settings["assets"]
    overrides = {
        feature: str(assets[f"background.module.{feature}"])
        for feature in FEATURES
        if f"background.module.{feature}" in assets
    }
    return build_living_world_definition(
        theme_id="dark",
        world_id="quiet-canopy-world",
        home_asset=str(assets["background.home"]),
        feature_assets=SUBSYSTEM_WORLD_ASSETS,
        feature_overrides=overrides,
    )


class LivingFeatureBackgroundMatrixTests(unittest.TestCase):
    def test_dark_matrix_uses_only_dedicated_assets(self) -> None:
        definition = dark_definition()
        self.assertTrue(set(FEATURES).issubset(definition.features))
        for feature in FEATURES:
            with self.subTest(feature=feature):
                resolved = definition.feature(feature)
                self.assertEqual(Path(resolved.asset), DEDICATED_DARK[feature])
                self.assertEqual(resolved.asset_state, "theme-asset")
                self.assertFalse(resolved.theme_asset_required)
                self.assertTrue(Path(resolved.asset).is_file())

    def test_dark_a_to_b_to_a_resolution_is_deterministic(self) -> None:
        first = dark_definition()
        official = build_living_world_definition(
            theme_id="official",
            world_id="living-os-official-world",
            home_asset=str(ROOT / "assets" / "living-os-official-world.png"),
            feature_assets=SUBSYSTEM_WORLD_ASSETS,
        )
        second = dark_definition()
        self.assertEqual(first, second)
        for feature in FEATURES:
            with self.subTest(feature=feature):
                resolved = official.feature(feature)
                self.assertEqual(Path(resolved.asset), Path(SUBSYSTEM_WORLD_ASSETS[feature]))
                self.assertEqual(resolved.asset_state, "official")
                self.assertFalse(resolved.theme_asset_required)

    def test_registered_feature_context_is_exact_and_unregistered_context_fails_closed(self) -> None:
        for feature in DEDICATED_DARK:
            with self.subTest(feature=feature):
                inherited = parse_inherited_world(
                    query(visual_role="FEATURE_BACKGROUND", feature_id=feature)
                )
                self.assertIsNotNone(inherited)
                path, source, fallback = resolve_visual_asset(
                    inherited, "FEATURE_BACKGROUND", feature
                )
                self.assertEqual(path, DEDICATED_DARK[feature])
                self.assertEqual(source, "theme-project-feature-role")
                self.assertEqual(fallback, "NONE")

        inherited = parse_inherited_world(
            query(visual_role="FEATURE_BACKGROUND", feature_id="collaboration")
        )
        self.assertIsNotNone(inherited)
        path, source, fallback = resolve_visual_asset(
            inherited, "FEATURE_BACKGROUND", "collaboration"
        )
        self.assertIsNone(path)
        self.assertEqual(source, "missing-role-asset")
        self.assertEqual(fallback, "ASSET REQUIRED")


if __name__ == "__main__":
    unittest.main()
