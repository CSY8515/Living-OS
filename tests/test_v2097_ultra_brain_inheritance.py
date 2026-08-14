from __future__ import annotations

import json
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

from subsystems.experience.engines.design_system import SCENE_LABELS
from subsystems.experience.engines.ultra_brain_world import (
    ADJUSTMENT_RANGES,
    PROPAGATION_TARGETS,
    THEMED_SCENES,
    THEME_PROFILES,
    WORLD_ASSETS,
    build_theme_settings,
    inherited_world_css,
    parse_inherited_world,
)
from subsystems.experience.engines.theme_adapter import ThemeAdapter
from subsystems.experience.engines.theme import OFFICIAL_UI_CSS
from subsystems.experience.engines.ui_registry import DEFAULT_UI_REGISTRY


def inherited_query(**values: object) -> dict[str, object]:
    return {
        "source": "ultra-brain",
        "contract": "ultra-brain.ui/v1",
        "interface": "1.0",
        "revision": "0.985",
        **values,
    }


class UltraBrainWorldInheritanceTests(unittest.TestCase):
    def test_no_propagation_query_keeps_existing_living_os_default(self) -> None:
        self.assertIsNone(parse_inherited_world({}))
        self.assertIsNone(parse_inherited_world({"nav_page": "Finance"}))
        css = inherited_world_css(None)
        self.assertIn('data-living-world-integration="v2.097"', css)
        self.assertNotIn('data-ultra-brain-inheritance="v0.985"', css)

    def test_every_registered_world_has_a_real_repository_asset(self) -> None:
        self.assertEqual(set(WORLD_ASSETS), set(THEME_PROFILES))
        for theme, asset in WORLD_ASSETS.items():
            with self.subTest(theme=theme):
                self.assertTrue(asset.is_file(), asset)
                self.assertGreater(asset.stat().st_size, 100_000)
                self.assertEqual(asset.suffix.lower(), ".png")

    def test_every_world_package_resolves_as_a_valid_living_os_contract(self) -> None:
        adapter = ThemeAdapter()
        for theme in THEME_PROFILES:
            with self.subTest(theme=theme):
                state = parse_inherited_world(
                    inherited_query(theme=theme, accent="#447788")
                )
                assert state is not None
                contract = adapter.resolve(build_theme_settings(state))
                if theme == "official":
                    self.assertEqual(
                        contract.to_payload(),
                        DEFAULT_UI_REGISTRY.theme("living-os-dark").to_payload(),
                    )
                    continue
                self.assertEqual(contract.source, "ultra-brain")
                self.assertEqual(
                    contract.assets["background.home"], str(WORLD_ASSETS[theme])
                )
                self.assertEqual(
                    contract.design_tokens.values["color"]["accent"], "#447788"
                )

    def test_root_world_asset_is_not_repeated_into_feature_scenes(self) -> None:
        self.assertEqual(set(THEMED_SCENES), set(SCENE_LABELS))
        state = parse_inherited_world(
            inherited_query(theme="calm", world="calm-wetland-world")
        )
        assert state is not None
        settings = build_theme_settings(state)
        assets = settings["assets"]
        self.assertEqual(assets["background.home"], str(WORLD_ASSETS["calm"]))
        for scene in SCENE_LABELS:
            self.assertNotIn(f"background.module.{scene}", assets)

    def test_query_is_normalized_and_adjustments_are_clamped(self) -> None:
        state = parse_inherited_world(
            inherited_query(**{
                "theme": "Ocean",
                "world": "deep-tide-world",
                "brightness": "99",
                "contrast": "bad",
                "saturation": "0",
                "hue": "-99",
                "lighting": "1.25",
                "shadow": "1.4",
                "glow": "1.7",
                "texture": "1.2",
                "blur": "4",
                "transparency": "0.7",
                "layout": json.dumps({"center": {"x": 999, "y": -999, "scale": 9}}),
                "uiLocks": json.dumps({"layout": True, "unknown": True}),
            })
        )
        assert state is not None
        self.assertEqual(state.requested_theme, "ocean")
        self.assertEqual(state.world, "deep-tide-world")
        self.assertEqual(state.adjustments["brightness"], 1.3)
        self.assertEqual(state.adjustments["contrast"], 1.0)
        self.assertEqual(state.adjustments["saturation"], 0.5)
        self.assertEqual(state.adjustments["hue"], -30)
        self.assertEqual(state.layout["center"]["x"], 80)
        self.assertEqual(state.layout["center"]["y"], -60)
        self.assertEqual(state.layout["center"]["scale"], 1.32)
        self.assertEqual(state.ui_locks, {"layout": True})

    def test_living_node_lock_is_granular(self) -> None:
        state = parse_inherited_world(
            inherited_query(**{
                "theme": "ocean",
                "brightness": "1.3",
                "saturation": "0.8",
                "accent": "#123456",
                "propagationTargets": json.dumps(["theme", "background", "brightness", "saturation"]),
                "propagationLocks": json.dumps({"living-os": ["background", "brightness"]}),
            })
        )
        assert state is not None
        self.assertEqual(state.palette_theme, "ocean")
        self.assertEqual(state.asset_theme, "official")
        self.assertEqual(state.adjustments["brightness"], ADJUSTMENT_RANGES["brightness"][2])
        self.assertEqual(state.adjustments["saturation"], 0.8)
        self.assertEqual(state.accent, "#123456")

    def test_living_node_override_preserves_local_official_world(self) -> None:
        state = parse_inherited_world(
            inherited_query(**{
                "theme": "lava",
                "accent": "#123456",
                "propagationTargets": json.dumps(["theme", "background", "color"]),
                "propagationOverrides": json.dumps(
                    {"living-os": ["theme", "background", "color"]}
                ),
            })
        )
        assert state is not None
        self.assertEqual(state.palette_theme, "official")
        self.assertEqual(state.asset_theme, "official")
        self.assertEqual(state.overridden_targets, {"theme", "background", "color"})
        self.assertIsNone(state.accent)

    def test_os_ecosystem_lock_does_not_invent_a_living_os_lock(self) -> None:
        state = parse_inherited_world(
            inherited_query(**{
                "theme": "grassland",
                "os_locked": "true",
                "target": "os-ecosystem",
                "propagationLocks": json.dumps(
                    {"os-ecosystem": ["theme", "background"]}
                ),
            })
        )
        assert state is not None
        self.assertEqual(state.palette_theme, "grassland")
        self.assertEqual(state.asset_theme, "grassland")
        self.assertFalse(state.locked_targets)

    def test_legacy_lock_is_honored_only_for_direct_living_target(self) -> None:
        direct = parse_inherited_world(
            inherited_query(target="living-os", theme="galaxy", locks="theme")
        )
        forwarded = parse_inherited_world(
            inherited_query(target="os-ecosystem", theme="galaxy", locks="theme")
        )
        assert direct is not None and forwarded is not None
        self.assertEqual(direct.palette_theme, "official")
        self.assertEqual(direct.asset_theme, "official")
        self.assertEqual(forwarded.palette_theme, "galaxy")
        self.assertEqual(forwarded.asset_theme, "galaxy")

    def test_world_css_applies_real_adjustments_and_removes_official_overlays(self) -> None:
        state = parse_inherited_world(
            inherited_query(**{
                "theme": "calm", "brightness": "0.94",
                "contrast": "0.9", "texture": "0.6", "motion": "false",
            })
        )
        assert state is not None
        css = inherited_world_css(state)
        self.assertIn('data-ultra-brain-inheritance="v0.985"', css)
        self.assertIn("filter:brightness(0.94)", css)
        self.assertIn(".los-fixed-world-backdrop img", css)
        self.assertIn(".los-world-roof", css)
        self.assertIn("animation:none", css)
        self.assertNotIn("UI Studio", css)

    def test_unknown_theme_and_unsafe_world_fall_back_safely(self) -> None:
        state = parse_inherited_world(
            inherited_query(theme="not-real", world="javascript:<bad>")
        )
        assert state is not None
        self.assertEqual(state.requested_theme, "official")
        self.assertEqual(state.world, "official-world")

    def test_source_contract_and_interface_are_one_trust_tuple(self) -> None:
        self.assertIsNone(parse_inherited_world({
            "source": "untrusted", "contract": "ultra-brain.ui/v1",
            "interface": "1.0", "theme": "ocean",
        }))
        self.assertIsNone(parse_inherited_world({
            "source": "ultra-brain", "contract": "wrong/v1",
            "interface": "1.0", "theme": "ocean",
        }))
        self.assertIsNone(parse_inherited_world({
            "source": "ultra-brain", "contract": "ultra-brain.ui/v1",
            "interface": "2.0", "theme": "ocean",
        }))
        self.assertIsNotNone(parse_inherited_world(inherited_query(theme="ocean")))
        forwarded = parse_inherited_world(inherited_query(
            source="os-ecosystem", target="os-ecosystem", theme="ocean"
        ))
        self.assertIsNotNone(forwarded)

    def test_official_url_is_exactly_the_checked_in_visual_contract(self) -> None:
        state = parse_inherited_world(inherited_query(theme="official"))
        assert state is not None
        expected = DEFAULT_UI_REGISTRY.theme("living-os-dark").to_payload()
        self.assertTrue(state.preserves_local_ui)
        self.assertTrue(state.preserves_local_contract)
        self.assertEqual(build_theme_settings(state), expected)
        css = inherited_world_css(state)
        self.assertIn('data-living-world-integration="v2.097"', css)
        self.assertNotIn('data-ultra-brain-inheritance="v0.985"', css)
        adapter = ThemeAdapter()
        self.assertEqual(
            adapter.render(OFFICIAL_UI_CSS, build_theme_settings(state)),
            adapter.render(OFFICIAL_UI_CSS),
        )

    def test_official_adjustments_compose_on_the_existing_filter(self) -> None:
        state = parse_inherited_world(inherited_query(
            theme="official", brightness="1.3", contrast="1.1", texture="1.2"
        ))
        assert state is not None
        self.assertTrue(state.preserves_local_contract)
        self.assertFalse(state.preserves_local_ui)
        self.assertEqual(
            build_theme_settings(state),
            DEFAULT_UI_REGISTRY.theme("living-os-dark").to_payload(),
        )
        css = inherited_world_css(state)
        self.assertIn("filter:brightness(0.858)", css)
        self.assertIn("contrast(1.32)", css)
        self.assertIn("hue-rotate(29deg)", css)
        self.assertNotIn(".los-world-roof,.los-world-symbol", css)

    def test_nonofficial_world_does_not_overlay_official_navigation_symbols(self) -> None:
        state = parse_inherited_world(inherited_query(theme="archive"))
        assert state is not None
        css = inherited_world_css(state)
        self.assertIn(
            ".los-world-central-roof,.los-world-roof,.los-world-object-clone,.los-world-symbol"
            "{display:none!important}",
            css,
        )

    def test_complete_lock_or_override_emits_no_effect_css(self) -> None:
        targets = list(PROPAGATION_TARGETS)
        for key in ("propagationLocks", "propagationOverrides"):
            with self.subTest(key=key):
                state = parse_inherited_world(inherited_query(**{
                    "theme": "lava",
                    "propagationTargets": json.dumps(targets),
                    key: json.dumps({"living-os": targets}),
                }))
                assert state is not None
                self.assertFalse(state.applied_targets)
                self.assertTrue(state.preserves_local_ui)
                css = inherited_world_css(state)
                self.assertIn('data-living-world-integration="v2.097"', css)
                self.assertNotIn('data-ultra-brain-inheritance="v0.985"', css)
                self.assertEqual(
                    build_theme_settings(state),
                    DEFAULT_UI_REGISTRY.theme("living-os-dark").to_payload(),
                )

    def test_layout_position_size_and_visibility_apply_and_honor_locks(self) -> None:
        layout = json.dumps({
            "topbar": {"x": 12, "y": -8, "scale": 1.2, "visible": False},
            "center": {"x": -7, "y": 5, "scale": 0.9, "visible": True},
            "seed": {"x": 3, "y": 4, "scale": 1.1, "visible": True},
            "rail": {"x": -2, "y": 6, "scale": 0.8, "visible": False},
        })
        state = parse_inherited_world(inherited_query(theme="ocean", layout=layout))
        assert state is not None
        css = inherited_world_css(state)
        self.assertIn(".st-key-official_user_navigation,.los-world-threshold", css)
        self.assertIn("translate:12px -8px!important", css)
        self.assertIn("scale:1.2!important", css)
        self.assertIn("visibility:hidden!important", css)
        self.assertIn(".st-key-world_enter", css)
        self.assertIn('[data-testid="stSidebar"]', css)

        field_locked = parse_inherited_world(inherited_query(**{
            "theme": "ocean", "layout": layout,
            "propagationLocks": json.dumps({
                "living-os": ["componentPosition", "componentSize", "visibility"]
            }),
        }))
        ui_locked = parse_inherited_world(inherited_query(
            theme="ocean", layout=layout, uiLocks=json.dumps({"layout": True})
        ))
        assert field_locked is not None and ui_locked is not None
        for locked_state in (field_locked, ui_locked):
            locked_css = inherited_world_css(locked_state)
            self.assertNotIn("translate:12px -8px!important", locked_css)
            self.assertNotIn("scale:1.2!important", locked_css)
            self.assertNotIn("visibility:hidden!important", locked_css)

    def test_shell_installs_inheritance_before_rendering_theme(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "subsystems" / "experience" / "engines" / "shell.py"
        ).read_text(encoding="utf-8")
        sync_position = source.index("sync_inherited_world(st.query_params)")
        theme_position = source.index("apply_responsive_layout()")
        self.assertLess(sync_position, theme_position)
        self.assertIn("inherited_world_css(inherited_world)", source)

    def test_streamlit_applies_calm_world_without_exposing_an_editor(self) -> None:
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=30)
        app.query_params["source"] = "ultra-brain"
        app.query_params["contract"] = "ultra-brain.ui/v1"
        app.query_params["interface"] = "1.0"
        app.query_params["theme"] = "calm"
        app.query_params["world"] = "calm-wetland-world"
        app.query_params["revision"] = "0.985"
        app.run()
        self.assertFalse(app.exception)
        rendered = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn('data-ultra-brain-theme="calm"', rendered)
        self.assertIn('data-effective-world="calm"', rendered)
        self.assertNotIn("UI Studio", rendered)


if __name__ == "__main__":
    unittest.main()
