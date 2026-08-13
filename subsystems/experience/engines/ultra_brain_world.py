from __future__ import annotations

from dataclasses import dataclass, replace
import json
import math
from pathlib import Path
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
INHERITED_WORLD_ROOT = ROOT / "assets" / "inherited-worlds"
OFFICIAL_WORLD_ASSET = ROOT / "assets" / "living-os-v2092-official-style-clean.png"
INHERITED_SESSION_KEY = "living_os_ultra_brain_world"
INHERITED_OBJECT_SESSION_KEY = "living_os_ultra_brain_world_object"
TARGET_NODE = "living-os"
JSON_QUERY_MAX_CHARS = 4096
TRUSTED_SOURCES = frozenset({"ultra-brain", "os-ecosystem"})
TRUSTED_CONTRACT = "ultra-brain.ui/v1"
TRUSTED_INTERFACE = "1.0"

ADJUSTMENT_RANGES = {
    "brightness": (0.7, 1.3, 1.0),
    "contrast": (0.7, 1.4, 1.0),
    "saturation": (0.5, 1.5, 1.0),
    "hue": (-30.0, 30.0, 0.0),
    "lighting": (0.0, 1.5, 1.0),
    "shadow": (0.4, 1.6, 1.0),
    "glow": (0.0, 1.8, 1.0),
    "texture": (0.0, 1.5, 1.0),
    "blur": (0.0, 8.0, 0.0),
    "transparency": (0.45, 1.0, 1.0),
}

PROPAGATION_TARGETS = (
    "theme", "background", "color", "brightness", "contrast", "saturation",
    "hue", "texture", "lighting", "shadow", "glow", "transparency", "blur",
    "layout", "componentPosition", "componentSize", "visibility", "animation",
)

# Every scene used by the current Living OS page registry has a semantic World
# Definition. The inherited root asset belongs to Living Home only; it must not
# be copied into every Feature scene.
THEMED_SCENES = (
    "living", "finance", "investment", "job", "health", "vehicle", "housing",
    "food", "knowledge", "routine", "growth", "collaboration", "timeline",
    "reports", "analytics", "search", "today", "decision", "assistant",
)

_SAFE_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_SAFE_CONTRACT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,63}$")
_SAFE_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def _colors(
    *,
    mode: str,
    background: str,
    background_soft: str,
    surface: str,
    surface_strong: str,
    text: str,
    text_soft: str,
    muted: str,
    accent: str,
    accent_bright: str,
    secondary: str,
) -> dict[str, str]:
    light = mode == "light"
    return {
        "background": background,
        "background_soft": background_soft,
        "surface": surface,
        "surface_strong": surface_strong,
        "glass": surface,
        "border": f"color-mix(in srgb,{accent} 34%,transparent)",
        "border_strong": f"color-mix(in srgb,{accent_bright} 62%,transparent)",
        "text": text,
        "text_soft": text_soft,
        "muted": muted,
        "accent": accent,
        "accent_bright": accent_bright,
        "secondary": secondary,
        "success": "#4f7a43" if light else "#a8c97a",
        "warning": "#9a6921" if light else "#d4a95f",
        "danger": "#a04b43" if light else "#d98179",
        "background_image": (
            f"radial-gradient(circle at 50% -10%,color-mix(in srgb,{accent} 18%,transparent),transparent 34rem),"
            f"linear-gradient(155deg,{background_soft} 0%,{background} 58%,{background_soft} 100%)"
        ),
    }


THEME_PROFILES: dict[str, dict[str, Any]] = {
    "official": {
        "mode": "dark", "radius": "18px", "font": "sans",
        "colors": _colors(mode="dark", background="#02070b", background_soft="#07100f",
                          surface="rgba(10,17,16,.82)", surface_strong="rgba(13,22,19,.94)",
                          text="#f3eddc", text_soft="#bbb7aa", muted="#858b84",
                          accent="#d8b66d", accent_bright="#f1d58a", secondary="#a8bf68"),
    },
    "light": {
        "mode": "light", "radius": "18px", "font": "sans",
        "colors": _colors(mode="light", background="#f4f1e8", background_soft="#ebe5d8",
                          surface="rgba(255,255,255,.86)", surface_strong="rgba(255,255,255,.96)",
                          text="#211f19", text_soft="#4f4a3e", muted="#777164",
                          accent="#7a5b25", accent_bright="#a47a2f", secondary="#657b45"),
    },
    "dark": {
        "mode": "dark", "radius": "14px", "font": "sans",
        "colors": _colors(mode="dark", background="#050d10", background_soft="#081317",
                          surface="rgba(5,13,16,.84)", surface_strong="rgba(8,19,23,.96)",
                          text="#eef2ed", text_soft="#9eaaa5", muted="#718079",
                          accent="#83aa8c", accent_bright="#bcd3af", secondary="#739486"),
    },
    "universe": {
        "mode": "dark", "radius": "7px", "font": "sans",
        "colors": _colors(mode="dark", background="#08081b", background_soft="#0e0c27",
                          surface="rgba(8,8,27,.84)", surface_strong="rgba(14,12,39,.96)",
                          text="#f0efff", text_soft="#aaa8c7", muted="#77758f",
                          accent="#9d91e8", accent_bright="#d5ceff", secondary="#7e8ac7"),
    },
    "galaxy": {
        "mode": "dark", "radius": "9px", "font": "sans",
        "colors": _colors(mode="dark", background="#180819", background_soft="#230a21",
                          surface="rgba(24,8,25,.84)", surface_strong="rgba(35,10,33,.96)",
                          text="#fff0f8", text_soft="#c9a7bc", muted="#97778b",
                          accent="#df86b8", accent_bright="#ffc7e5", secondary="#aa75c9"),
    },
    "ecosystem": {
        "mode": "dark", "radius": "6px", "font": "sans",
        "colors": _colors(mode="dark", background="#05130c", background_soft="#081c11",
                          surface="rgba(5,19,12,.84)", surface_strong="rgba(8,28,17,.96)",
                          text="#eff8e9", text_soft="#a8c3aa", muted="#77947a",
                          accent="#79b67b", accent_bright="#c4e6af", secondary="#9abe63"),
    },
    "ocean": {
        "mode": "dark", "radius": "5px", "font": "sans",
        "colors": _colors(mode="dark", background="#031018", background_soft="#041924",
                          surface="rgba(3,16,24,.86)", surface_strong="rgba(4,25,36,.97)",
                          text="#edfaff", text_soft="#9bc1cc", muted="#668f9b",
                          accent="#56b8cf", accent_bright="#b8f0fa", secondary="#4c9eb3"),
    },
    "grassland": {
        "mode": "light", "radius": "10px", "font": "sans",
        "colors": _colors(mode="light", background="#e2e8c5", background_soft="#f3f6de",
                          surface="rgba(226,232,197,.86)", surface_strong="rgba(243,246,222,.97)",
                          text="#26321f", text_soft="#66735b", muted="#788069",
                          accent="#668744", accent_bright="#7ca34f", secondary="#8dae5a"),
    },
    "lava": {
        "mode": "dark", "radius": "3px", "font": "sans",
        "colors": _colors(mode="dark", background="#1c0805", background_soft="#2b0c07",
                          surface="rgba(28,8,5,.86)", surface_strong="rgba(43,12,7,.97)",
                          text="#fff1e7", text_soft="#d2a897", muted="#9f7765",
                          accent="#e87943", accent_bright="#ffc08e", secondary="#c9542f"),
    },
    "minimal": {
        "mode": "dark", "radius": "2px", "font": "minimal",
        "colors": _colors(mode="dark", background="#0e1111", background_soft="#161a19",
                          surface="rgba(14,17,17,.84)", surface_strong="rgba(22,26,25,.97)",
                          text="#f5f7f3", text_soft="#a7afaa", muted="#767e79",
                          accent="#d2d7d0", accent_bright="#ffffff", secondary="#929a94"),
    },
    "paper": {
        "mode": "light", "radius": "1px", "font": "serif",
        "colors": _colors(mode="light", background="#f6f0de", background_soft="#fffaf0",
                          surface="rgba(246,240,222,.9)", surface_strong="rgba(255,252,242,.98)",
                          text="#33281e", text_soft="#756454", muted="#8a7968",
                          accent="#8b5e34", accent_bright="#a96f3d", secondary="#7e7452"),
    },
    "archive": {
        "mode": "dark", "radius": "2px", "font": "serif",
        "colors": _colors(mode="dark", background="#16110c", background_soft="#1f1811",
                          surface="rgba(22,17,12,.86)", surface_strong="rgba(31,24,17,.97)",
                          text="#f2e9da", text_soft="#b7a994", muted="#827867",
                          accent="#b49b78", accent_bright="#e6d7b8", secondary="#8f8769"),
    },
    "calm": {
        "mode": "light", "radius": "8px", "font": "sans",
        "colors": _colors(mode="light", background="#dbe5e9", background_soft="#eef3f4",
                          surface="rgba(218,228,232,.88)", surface_strong="rgba(238,243,244,.98)",
                          text="#17262e", text_soft="#435c67", muted="#637a84",
                          accent="#547b8c", accent_bright="#365f72", secondary="#7899a3"),
    },
}

WORLD_ASSETS = {
    "official": OFFICIAL_WORLD_ASSET,
    **{
        theme: INHERITED_WORLD_ROOT / f"{theme}.png"
        for theme in THEME_PROFILES
        if theme != "official"
    },
}


@dataclass(frozen=True)
class InheritedWorld:
    requested_theme: str
    style_theme: str
    palette_theme: str
    asset_theme: str
    world: str
    revision: str
    source: str
    contract: str
    adjustments: Mapping[str, float]
    propagation_targets: tuple[str, ...]
    locked_targets: frozenset[str]
    overridden_targets: frozenset[str]
    layout: Mapping[str, Mapping[str, object]]
    ui_locks: Mapping[str, bool]
    motion: bool
    accent: str | None

    @property
    def asset_path(self) -> Path:
        path = WORLD_ASSETS[self.asset_theme]
        return path if path.is_file() else OFFICIAL_WORLD_ASSET

    def target_enabled(self, target: str) -> bool:
        """Return whether one visual field may cross the Living OS boundary."""
        if target not in self.propagation_targets:
            return False
        if target in self.locked_targets or target in self.overridden_targets:
            return False
        locks = self.ui_locks
        if target == "background":
            return not locks.get("background", False)
        if target == "color":
            return not locks.get("color", False)
        if target == "texture":
            return not locks.get("texture", False)
        if target == "lighting":
            return not locks.get("lighting", False)
        if target == "layout":
            return not locks.get("layout", False)
        if target == "componentPosition":
            return not any(locks.get(key, False) for key in ("layout", "position", "component"))
        if target == "componentSize":
            return not any(locks.get(key, False) for key in ("layout", "size", "component"))
        if target == "visibility":
            return not any(locks.get(key, False) for key in ("layout", "component", "layer"))
        return True

    @property
    def applied_targets(self) -> frozenset[str]:
        return frozenset(
            target for target in self.propagation_targets if self.target_enabled(target)
        )

    @property
    def preserves_local_contract(self) -> bool:
        # Official always keeps the checked-in Living OS contract.  Independent
        # adjustment controls are composed later as a small effect layer.
        return self.requested_theme == "official" or not self.applied_targets

    @property
    def preserves_local_ui(self) -> bool:
        if not self.applied_targets:
            return True
        if self.requested_theme != "official":
            return False
        for key, (_, _, default) in ADJUSTMENT_RANGES.items():
            if self.target_enabled(key) and not math.isclose(self.adjustments[key], default):
                return False
        official_accent = str(THEME_PROFILES["official"]["colors"]["accent"]).lower()
        if self.accent and self.accent.lower() != official_accent:
            return False
        if self.target_enabled("animation") and not self.motion:
            return False
        return not _layout_css(self)


def _query_scalar(query: Mapping[str, object], key: str, default: str = "") -> str:
    value = query.get(key, default)
    if isinstance(value, (list, tuple)):
        value = value[-1] if value else default
    return str(value).strip()


def _safe_token(value: str, default: str) -> str:
    normalized = value.strip().lower()
    return normalized if _SAFE_TOKEN.fullmatch(normalized) else default


def _safe_json(query: Mapping[str, object], key: str) -> object | None:
    raw = _query_scalar(query, key)
    if not raw or len(raw) > JSON_QUERY_MAX_CHARS:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def _clamped(value: object, minimum: float, maximum: float, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(number):
        return default
    return min(maximum, max(minimum, number))


def _safe_bool(value: object, default: bool = False) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _normalize_targets(values: object) -> list[str]:
    candidates = values.split(",") if isinstance(values, str) else values
    if not isinstance(candidates, (list, tuple)):
        return []
    aliases = {target.lower(): target for target in PROPAGATION_TARGETS}
    result: list[str] = []
    for value in candidates:
        target = aliases.get(str(value).strip().lower())
        if target and target not in result:
            result.append(target)
    return result


def _node_targets(query: Mapping[str, object], key: str) -> dict[str, list[str]]:
    value = _safe_json(query, key)
    if not isinstance(value, dict):
        return {}
    result: dict[str, list[str]] = {}
    for node, targets in value.items():
        safe_node = _safe_token(str(node), "")
        safe_targets = _normalize_targets(targets)
        if safe_node and safe_targets:
            result[safe_node] = safe_targets
    return result


def _safe_layout(query: Mapping[str, object]) -> dict[str, dict[str, object]]:
    value = _safe_json(query, "layout")
    if not isinstance(value, dict):
        return {}
    result: dict[str, dict[str, object]] = {}
    for name in ("topbar", "center", "seed", "rail"):
        item = value.get(name)
        if not isinstance(item, dict):
            continue
        result[name] = {
            "x": _clamped(item.get("x", 0), -80, 80, 0),
            "y": _clamped(item.get("y", 0), -60, 60, 0),
            "scale": _clamped(item.get("scale", 1), 0.72, 1.32, 1),
            "visible": item.get("visible") is not False,
            "pinned": item.get("pinned") is True,
        }
    return result


def _safe_ui_locks(query: Mapping[str, object]) -> dict[str, bool]:
    value = _safe_json(query, "uiLocks")
    if not isinstance(value, dict):
        return {}
    allowed = {"position", "size", "background", "layout", "color", "texture", "lighting", "component", "layer"}
    return {str(key): item is True for key, item in value.items() if key in allowed}


def parse_inherited_world(query: Mapping[str, object]) -> InheritedWorld | None:
    """Parse an Ultra Brain/OS Ecosystem propagation URL without trusting it."""
    signal_keys = {
        "source", "theme", "world", "contract", "propagationTargets",
        "propagationLocks", "propagationOverrides",
    }
    if not signal_keys.intersection(query):
        return None

    # This URL is a public input boundary.  Source, contract and interface are
    # one trust tuple; a valid value in only one field must never authenticate
    # malformed or unrelated query parameters.
    source = _query_scalar(query, "source").lower()
    contract = _query_scalar(query, "contract")
    interface = _query_scalar(query, "interface")
    if (
        source not in TRUSTED_SOURCES
        or contract != TRUSTED_CONTRACT
        or interface != TRUSTED_INTERFACE
    ):
        return None

    requested = _safe_token(_query_scalar(query, "theme", "official"), "official")
    if requested not in THEME_PROFILES:
        requested = "official"
    world = _safe_token(_query_scalar(query, "world", f"{requested}-world"), f"{requested}-world")
    revision = _safe_token(_query_scalar(query, "revision", "0.985"), "0.985")

    targets = _normalize_targets(_safe_json(query, "propagationTargets"))
    if not targets:
        targets = _normalize_targets(_query_scalar(query, "applied_targets", ""))
    if not targets:
        targets = list(PROPAGATION_TARGETS)

    lock_map = _node_targets(query, "propagationLocks")
    override_map = _node_targets(query, "propagationOverrides")
    locked = set(lock_map.get(TARGET_NODE, ()))
    overridden = set(override_map.get(TARGET_NODE, ()))
    direct_target = _safe_token(_query_scalar(query, "target", "os-ecosystem"), "os-ecosystem")
    if direct_target == TARGET_NODE:
        locked.update(_normalize_targets(_query_scalar(query, "locked_targets", "")))
        overridden.update(_normalize_targets(_query_scalar(query, "overridden_targets", "")))
        if _safe_bool(_query_scalar(query, "livingOSLocked", "false")):
            locked.update(targets)
        if _safe_bool(_query_scalar(query, "livingOSOverride", "false")):
            overridden.update(targets)
        # Legacy direct Living OS links may only carry the old lock list.
        legacy = {_safe_token(item, "") for item in _query_scalar(query, "locks", "").split(",")}
        if "all" in legacy:
            locked.update(targets)
        locked.update(target for target in legacy if target in PROPAGATION_TARGETS)

    locked.intersection_update(targets)
    overridden.intersection_update(targets)
    blocked = locked | overridden
    ui_locks = _safe_ui_locks(query)
    effective = set(targets).difference(blocked)
    theme_blocked = "theme" in blocked
    color_blocked = "color" in blocked or ui_locks.get("color", False)
    background_blocked = "background" in blocked or ui_locks.get("background", False)
    style_applied = "theme" in effective and not theme_blocked
    palette_applied = (
        not theme_blocked
        and not color_blocked
        and bool({"theme", "color"}.intersection(effective))
    )
    asset_applied = (
        not theme_blocked
        and not background_blocked
        and bool({"theme", "background"}.intersection(effective))
    )
    style_theme = requested if style_applied else "official"
    palette_theme = requested if palette_applied else "official"
    asset_theme = requested if asset_applied else "official"

    adjustments: dict[str, float] = {}
    for key, (minimum, maximum, default) in ADJUSTMENT_RANGES.items():
        value = _clamped(_query_scalar(query, key, str(default)), minimum, maximum, default)
        blocked_by_ui = (
            (key == "texture" and ui_locks.get("texture", False))
            or (key == "lighting" and ui_locks.get("lighting", False))
        )
        adjustments[key] = (
            value if key in effective and not blocked_by_ui else default
        )

    accent_value = _query_scalar(query, "accent", "")
    accent = accent_value.lower() if _SAFE_HEX.fullmatch(accent_value) else None
    if not ({"theme", "color"}.intersection(effective)) or ui_locks.get("color", False):
        accent = None

    motion = (
        _safe_bool(_query_scalar(query, "motion", "true"), True)
        if "animation" in effective
        else True
    )

    return InheritedWorld(
        requested_theme=requested,
        style_theme=style_theme,
        palette_theme=palette_theme,
        asset_theme=asset_theme,
        world=world,
        revision=revision,
        source=source,
        contract=contract,
        adjustments=adjustments,
        propagation_targets=tuple(targets),
        locked_targets=frozenset(locked),
        overridden_targets=frozenset(overridden),
        layout=_safe_layout(query),
        ui_locks=ui_locks,
        motion=motion,
        accent=accent,
    )


def build_theme_settings(world: InheritedWorld) -> dict[str, object]:
    if world.preserves_local_contract:
        from subsystems.experience.engines.ui_registry import DEFAULT_UI_REGISTRY

        return DEFAULT_UI_REGISTRY.theme("living-os-dark").to_payload()

    style_profile = THEME_PROFILES[world.style_theme]
    palette_profile = THEME_PROFILES[world.palette_theme]
    colors = dict(palette_profile["colors"])
    if world.accent:
        colors["accent"] = world.accent
    radius = str(style_profile["radius"])
    font_kind = str(style_profile["font"])
    font_sans = (
        '"Noto Serif KR","Batang",serif'
        if font_kind == "serif"
        else '"Inter","Pretendard Variable","Noto Sans KR","Malgun Gothic",sans-serif'
        if font_kind == "minimal"
        else '"Pretendard Variable","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","Segoe UI",sans-serif'
    )
    assets: dict[str, str] = {}
    if world.asset_theme != "official":
        asset = str(world.asset_path)
        assets["background.home"] = asset

    design_tokens: dict[str, object] = {}
    if world.target_enabled("theme") or world.target_enabled("color"):
        design_tokens["color"] = colors
    if world.target_enabled("theme"):
        design_tokens["typography"] = {"font_sans": font_sans}
        design_tokens["shape"] = {
            "radius": radius,
            "radius_small": radius,
            "card_radius": radius,
            "button_radius": radius,
            "dialog_radius": radius,
            "widget_radius": radius,
        }
    if (
        world.target_enabled("theme")
        or world.target_enabled("shadow")
        or world.target_enabled("glow")
    ):
        design_tokens["shadow"] = {
            "card": f"0 18px 48px rgba(0,0,0,{0.18 + 0.14 * world.adjustments['shadow']:.3f})",
            "button": f"0 10px 24px rgba(0,0,0,{0.10 + 0.10 * world.adjustments['shadow']:.3f})",
            "dialog": f"0 30px 90px rgba(0,0,0,{0.22 + 0.16 * world.adjustments['shadow']:.3f})",
            "glow": f"0 0 {18 + 18 * world.adjustments['glow']:.1f}px color-mix(in srgb,{colors['accent']} 22%,transparent)",
        }
    if world.target_enabled("theme") or world.target_enabled("animation"):
        design_tokens["motion"] = {
            "enabled": world.motion,
            "scale": 1.0 if world.motion else 0.0,
        }
    return {
        "contract_id": "ultra-brain.ui",
        "contract_version": 1,
        "theme_id": f"ultra-brain-{world.requested_theme}",
        "mode": palette_profile["mode"],
        "source": "ultra-brain",
        "design_tokens": design_tokens,
        "assets": assets,
    }


_LAYOUT_SELECTORS = {
    # Ultra Brain slots are translated to existing Living OS surfaces; no new
    # child editor or component hierarchy is introduced.
    "topbar": ".st-key-official_user_navigation,.los-world-threshold",
    "center": ".los-subsystem-world-hero>.los-page-hero",
    "seed": ".st-key-world_enter",
    "rail": '[data-testid="stSidebar"]',
}


def _layout_css(world: InheritedWorld) -> str:
    if not world.layout:
        return ""
    blocked = world.locked_targets | world.overridden_targets
    layout_enabled = world.target_enabled("layout")
    position_enabled = (
        (layout_enabled or world.target_enabled("componentPosition"))
        and "componentPosition" not in blocked
        and not any(world.ui_locks.get(key, False) for key in ("layout", "position", "component"))
    )
    size_enabled = (
        (layout_enabled or world.target_enabled("componentSize"))
        and "componentSize" not in blocked
        and not any(world.ui_locks.get(key, False) for key in ("layout", "size", "component"))
    )
    visibility_enabled = (
        (layout_enabled or world.target_enabled("visibility"))
        and "visibility" not in blocked
        and not any(world.ui_locks.get(key, False) for key in ("layout", "component", "layer"))
    )
    if not (position_enabled or size_enabled or visibility_enabled):
        return ""

    rules: list[str] = []
    for name, item in world.layout.items():
        selector = _LAYOUT_SELECTORS.get(name)
        if not selector:
            continue
        declarations: list[str] = []
        x = float(item.get("x", 0))
        y = float(item.get("y", 0))
        scale = float(item.get("scale", 1))
        if position_enabled and (x or y):
            declarations.append(f"translate:{x:g}px {y:g}px!important")
        if size_enabled and not math.isclose(scale, 1.0):
            declarations.append(f"scale:{scale:g}!important")
        if visibility_enabled and item.get("visible") is False:
            declarations.append("visibility:hidden!important")
            declarations.append("pointer-events:none!important")
        if declarations:
            rules.append(f"{selector}{{{';'.join(declarations)}}}")
    return "".join(rules)


def inherited_world_css(world: InheritedWorld | None) -> str:
    from subsystems.experience.engines.living_world import living_world_css

    integration = living_world_css(world.style_theme if world else "official")
    if world is None or world.preserves_local_ui:
        return integration
    values = world.adjustments
    defaults = {key: item[2] for key, item in ADJUSTMENT_RANGES.items()}
    nonofficial_asset = world.asset_theme != "official"
    adjusted = {
        key
        for key, value in values.items()
        if world.target_enabled(key) and not math.isclose(value, defaults[key])
    }
    rules: list[str] = []
    official_accent = str(THEME_PROFILES["official"]["colors"]["accent"]).lower()
    if world.accent and world.accent.lower() != official_accent:
        rules.append(
            f".stApp{{--los-gold:{world.accent}!important;"
            f"--los-gold-bright:{world.accent}!important;--los-icon-color:{world.accent}!important}}"
        )

    # A different world asset needs a neutral image treatment.  For the local
    # Official asset, emit a filter only when the user truly changed an effect;
    # otherwise the checked-in Living OS filters remain authoritative.
    image_adjustments = {
        "brightness", "contrast", "saturation", "hue", "blur", "transparency"
    }
    if nonofficial_asset or adjusted.intersection(image_adjustments):
        if nonofficial_asset:
            home_brightness, home_contrast, home_saturation, home_hue = (
                values["brightness"], values["contrast"], values["saturation"], values["hue"]
            )
        else:
            home_brightness = 0.66 * values["brightness"]
            home_contrast = 1.20 * values["contrast"]
            home_saturation = 0.58 * values["saturation"]
            home_hue = 29 + values["hue"]
        rules.append(
            ".st-key-living_world img{"
            f"filter:brightness({home_brightness:g}) contrast({home_contrast:g}) "
            f"saturate({home_saturation:g}) hue-rotate({home_hue:g}deg) "
            f"blur({values['blur']:g}px)!important;opacity:{values['transparency']:g}!important"
            "}"
        )
        feature_brightness = (1.0 if nonofficial_asset else 0.92) * values["brightness"]
        feature_contrast = (1.0 if nonofficial_asset else 1.04) * values["contrast"]
        feature_saturation = (1.0 if nonofficial_asset else 1.02) * values["saturation"]
        rules.append(
            ".los-fixed-world-backdrop img,.los-subsystem-world-hero>img{"
            f"filter:brightness({feature_brightness:g}) contrast({feature_contrast:g}) "
            f"saturate({feature_saturation:g}) hue-rotate({values['hue']:g}deg) "
            f"blur({values['blur']:g}px)!important;opacity:{values['transparency']:g}!important"
            "}"
        )

    if nonofficial_asset:
        rules.append(
            ".los-world-central-roof,.los-world-roof,.los-world-object-clone"
            "{display:none!important}"
        )
        rules.append(
            ".los-world-style-layer{background:transparent!important;box-shadow:none!important;"
            "mix-blend-mode:normal!important}"
        )
    elif adjusted.intersection({"lighting", "texture"}):
        rules.append(
            ".los-world-style-layer{"
            f"opacity:{min(1.0, 0.34 * values['lighting'] + 0.08 * values['texture']):g}!important"
            "}"
        )

    if nonofficial_asset or adjusted.intersection({"lighting", "texture"}):
        rules.append(
            ".los-subsystem-world-hero:after,.los-fixed-world-backdrop:after{"
            f"opacity:{min(1.0, 0.10 * values['lighting'] + 0.06 * values['texture']):g}!important"
            "}"
        )

    if adjusted.intersection({"shadow", "glow"}) or world.style_theme != "official":
        shadow_blur = 38 * values["shadow"]
        glow_blur = 22 * values["glow"]
        rules.append(
            ".los-page-hero,.los-world-threshold,.los-user-navigation,[data-testid=\"stSidebar\"]{"
            f"box-shadow:0 18px {shadow_blur:.1f}px rgba(0,0,0,.25),"
            f"0 0 {glow_blur:.1f}px color-mix(in srgb,var(--los-gold) 15%,transparent)!important"
            "}"
        )

    layout_rules = _layout_css(world)
    if layout_rules:
        rules.append(layout_rules)
    if world.target_enabled("animation") and not world.motion:
        rules.append(".stApp *{animation:none!important;transition:none!important}")

    return integration + (
        '<style data-ultra-brain-inheritance="v0.985">'
        + "".join(rules)
        + "</style>"
        + f'<span hidden data-ultra-brain-theme="{world.requested_theme}" '
        + f'data-effective-palette="{world.palette_theme}" data-effective-world="{world.asset_theme}" '
        + f'data-world-id="{world.world}" data-revision="{world.revision}"></span>'
    )


def active_inherited_world() -> InheritedWorld | None:
    """Return the effective inherited World kept across Living navigation."""

    import streamlit as st

    value = st.session_state.get(INHERITED_OBJECT_SESSION_KEY)
    return value if isinstance(value, InheritedWorld) else None


def _merge_protected_world(
    incoming: InheritedWorld,
    active: InheritedWorld | None,
) -> InheritedWorld:
    """Preserve active visual fields that the incoming contract cannot change."""

    if active is None:
        return incoming
    updates: dict[str, object] = {}
    theme_enabled = incoming.target_enabled("theme")
    color_enabled = theme_enabled or incoming.target_enabled("color")
    background_enabled = theme_enabled or incoming.target_enabled("background")
    if not theme_enabled:
        updates.update(
            requested_theme=active.requested_theme,
            style_theme=active.style_theme,
            world=active.world,
            revision=active.revision,
        )
    if not color_enabled:
        updates["palette_theme"] = active.palette_theme
        updates["accent"] = active.accent
    if not background_enabled:
        updates["asset_theme"] = active.asset_theme
    adjustments = dict(incoming.adjustments)
    for name in ADJUSTMENT_RANGES:
        if not incoming.target_enabled(name):
            adjustments[name] = active.adjustments.get(
                name, ADJUSTMENT_RANGES[name][2]
            )
    updates["adjustments"] = adjustments
    if not any(
        incoming.target_enabled(name)
        for name in ("layout", "componentPosition", "componentSize", "visibility")
    ):
        updates["layout"] = active.layout
    if not incoming.target_enabled("animation"):
        updates["motion"] = active.motion
    return replace(incoming, **updates)


def sync_inherited_world(query: Mapping[str, object]) -> InheritedWorld | None:
    """Install the effective World and preserve it across Living navigation."""
    import streamlit as st
    from subsystems.experience.engines.ui_interface import (
        ULTRA_BRAIN_UI_SESSION_KEY,
        install_ultra_brain_ui_settings,
    )

    signal_keys = {
        "source", "theme", "world", "contract", "propagationTargets",
        "propagationLocks", "propagationOverrides",
    }
    has_signal = bool(signal_keys.intersection(query))
    active = active_inherited_world()
    incoming = parse_inherited_world(query)
    if incoming is None:
        if not has_signal:
            return active
        st.session_state.pop(ULTRA_BRAIN_UI_SESSION_KEY, None)
        st.session_state.pop(INHERITED_SESSION_KEY, None)
        st.session_state.pop(INHERITED_OBJECT_SESSION_KEY, None)
        return None
    world = _merge_protected_world(incoming, active)
    if world.preserves_local_contract:
        st.session_state.pop(ULTRA_BRAIN_UI_SESSION_KEY, None)
    else:
        install_ultra_brain_ui_settings(build_theme_settings(world))
    st.session_state[INHERITED_OBJECT_SESSION_KEY] = world
    st.session_state[INHERITED_SESSION_KEY] = {
        "theme": world.requested_theme,
        "world": world.world,
        "revision": world.revision,
        "locked_targets": sorted(world.locked_targets),
        "overridden_targets": sorted(world.overridden_targets),
    }
    return world
