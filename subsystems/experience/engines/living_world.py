from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class ThemeWorldLanguage:
    theme_id: str
    composition: str
    frame: str
    lighting: str
    texture: str
    material: str
    effects: str


@dataclass(frozen=True)
class FeatureWorldDefinition:
    feature_id: str
    scene: str
    asset: str
    asset_state: str
    main_object: str
    navigation_object: str
    composition: str
    visual_focus: str
    layout: str
    lighting: str
    texture: str
    material: str
    effects: str
    theme_asset_required: bool


@dataclass(frozen=True)
class LivingWorldDefinition:
    theme_id: str
    world_id: str
    hierarchy_level: str
    identity: str
    home_asset: str
    language: ThemeWorldLanguage
    features: Mapping[str, FeatureWorldDefinition]

    def feature(self, scene: str) -> FeatureWorldDefinition:
        return self.features.get(scene, self.features["living"])


THEME_WORLD_LANGUAGE: dict[str, ThemeWorldLanguage] = {
    "official": ThemeWorldLanguage("official", "living-sanctuary", "gilded-arch", "lantern-lit", "botanical-stone", "brass-glass", "seed-glow"),
    "light": ThemeWorldLanguage("light", "sunlit-courtyard", "open-arch", "high-key-daylight", "linen-stone", "ivory-glass", "soft-bloom"),
    "dark": ThemeWorldLanguage("dark", "night-sanctuary", "deep-arch", "low-key-canopy", "charcoal-moss", "smoked-glass", "quiet-pulse"),
    "calm": ThemeWorldLanguage("calm", "wetland-haven", "soft-oval", "diffused-dawn", "mist-water", "frosted-glass", "water-ripple"),
    "universe": ThemeWorldLanguage("universe", "orbital-habitat", "orbital-ring", "stellar-rim", "cosmic-dust", "violet-glass", "star-drift"),
    "ecosystem": ThemeWorldLanguage("ecosystem", "forest-network", "branch-frame", "leaf-filtered", "bark-canopy", "living-glass", "spore-glow"),
    "ocean": ThemeWorldLanguage("ocean", "tidal-domain", "wave-cut", "caustic-deep", "water-current", "pearl-glass", "current-trace"),
    "grassland": ThemeWorldLanguage("grassland", "open-meadow", "horizon-frame", "wide-sun", "grass-wind", "woven-glass", "pollen-drift"),
    "lava": ThemeWorldLanguage("lava", "forged-domain", "forged-edge", "ember-lit", "volcanic-crust", "obsidian-glass", "ember-flow"),
    "galaxy": ThemeWorldLanguage("galaxy", "nebula-garden", "nebula-cut", "magenta-rim", "nebula-cloud", "prismatic-glass", "constellation-flow"),
    "minimal": ThemeWorldLanguage("minimal", "quiet-grid", "linear-frame", "neutral-studio", "matte-grid", "clear-glass", "measured-pulse"),
    "paper": ThemeWorldLanguage("paper", "folio-world", "folio-frame", "library-daylight", "paper-fiber", "vellum-glass", "ink-bloom"),
    "archive": ThemeWorldLanguage("archive", "memory-vault", "vault-frame", "amber-lamp", "aged-leather", "smoked-crystal", "dust-trace"),
}


# These are semantic scene identities, not UI labels. The renderer composes
# them with the selected ThemeWorldLanguage while the feature facade and data
# flow remain unchanged.
FEATURE_WORLD_IDENTITY: dict[str, tuple[str, str, str, str, str]] = {
    "living": ("living-hearth", "central-threshold", "living-concourse", "whole-life", "radial"),
    "finance": ("ledger-vault", "vault-gate", "flow-ledger", "asset-flow", "split-ledger"),
    "investment": ("value-observatory", "signal-prism", "rising-orbit", "value-change", "ascending"),
    "job": ("career-station", "route-ticket", "opportunity-platform", "next-action", "directional"),
    "health": ("biometric-garden", "pulse-gate", "recovery-ring", "body-signal", "organic"),
    "vehicle": ("mobility-bay", "route-compass", "transit-lane", "movement-energy", "panoramic"),
    "housing": ("home-habitat", "dwelling-door", "shelter-court", "living-base", "architectural"),
    "food": ("nourishment-kitchen", "table-emblem", "ingredient-table", "meal-cycle", "atelier"),
    "knowledge": ("memory-library", "open-volume", "archive-aisle", "learning-link", "layered"),
    "routine": ("rhythm-orbit", "cycle-dial", "repeating-path", "continuity", "circular"),
    "growth": ("growth-greenhouse", "sprout-marker", "vertical-garden", "progress-reflection", "vertical"),
    "collaboration": ("connection-atrium", "linked-nodes", "shared-table", "commitment-flow", "networked"),
    "timeline": ("time-orbit", "chronicle-ring", "event-stream", "sequence", "linear"),
    "reports": ("record-atlas", "report-seal", "map-table", "summary", "editorial"),
    "analytics": ("life-observatory", "signal-lens", "comparison-deck", "trend", "analytical"),
    "search": ("living-index", "search-lens", "index-corridor", "discovery", "focused"),
    "today": ("today-garden", "day-marker", "daily-clearing", "present-flow", "immediate"),
    "decision": ("decision-chamber", "choice-prism", "branching-path", "evidence-outcome", "branched"),
    "assistant": ("insight-observatory", "guidance-orb", "reading-desk", "supporting-insight", "concentric"),
}


FEATURE_NAVIGATION_SHAPES = {
    "finance": "vault",
    "job": "ticket",
    "investment": "prism",
    "knowledge": "folio",
    "routine": "cycle",
    "growth": "leaf",
    "food": "table",
    "housing": "house",
    "health": "pulse",
    "vehicle": "route",
}


def normalize_theme_id(theme_id: str) -> str:
    value = str(theme_id).strip().lower()
    if value.startswith("ultra-brain-"):
        value = value.removeprefix("ultra-brain-")
    if value in {"living-os-dark", "living-os-light"}:
        value = "official" if value.endswith("dark") else "light"
    return value if value in THEME_WORLD_LANGUAGE else "official"


def build_living_world_definition(
    *,
    theme_id: str,
    world_id: str,
    home_asset: str,
    feature_assets: Mapping[str, Path | str],
    feature_overrides: Mapping[str, str] | None = None,
) -> LivingWorldDefinition:
    normalized_theme = normalize_theme_id(theme_id)
    language = THEME_WORLD_LANGUAGE[normalized_theme]
    overrides = dict(feature_overrides or {})
    features: dict[str, FeatureWorldDefinition] = {}
    for scene, identity in FEATURE_WORLD_IDENTITY.items():
        main_object, navigation_object, composition, visual_focus, layout = identity
        default_asset = str(feature_assets.get(scene, ""))
        override = str(overrides.get(scene, "")).strip()
        if override and override != default_asset:
            asset = override
            asset_state = "theme-asset"
            required = False
        elif default_asset:
            asset = default_asset
            asset_state = "official" if normalized_theme == "official" else "reused-official-feature"
            required = normalized_theme != "official"
        else:
            asset = ""
            asset_state = "css-scene" if normalized_theme == "official" else "asset-required"
            required = normalized_theme != "official"
        features[scene] = FeatureWorldDefinition(
            feature_id=scene,
            scene=scene,
            asset=asset,
            asset_state=asset_state,
            main_object=main_object,
            navigation_object=navigation_object,
            composition=composition,
            visual_focus=visual_focus,
            layout=layout,
            lighting=language.lighting,
            texture=language.texture,
            material=language.material,
            effects=language.effects,
            theme_asset_required=required,
        )
    return LivingWorldDefinition(
        theme_id=normalized_theme,
        world_id=str(world_id).strip() or f"{normalized_theme}-living-world",
        hierarchy_level="living-os",
        identity="living-world",
        home_asset=str(home_asset),
        language=language,
        features=features,
    )


def living_world_css(theme_id: str) -> str:
    language = THEME_WORLD_LANGUAGE[normalize_theme_id(theme_id)]
    navigation_rules = {
        "vault": "14px 14px 34% 34%/18px 18px 44% 44%",
        "ticket": "8px 28px 8px 28px",
        "prism": "12px 42% 12px 42%",
        "folio": "8px 20px 20px 8px",
        "cycle": "50%",
        "leaf": "50% 12px 50% 12px",
        "table": "34% 34% 12px 12px",
        "house": "44% 44% 10px 10px/30% 30% 12px 12px",
        "pulse": "50% 50% 42% 42%",
        "route": "999px 28px 28px 999px",
    }
    nav_css = "".join(
        f'.st-key-world_node_{feature} .stButton>button{{border-radius:{navigation_rules[shape]}!important}}'
        for feature, shape in FEATURE_NAVIGATION_SHAPES.items()
    )
    feature_positions = {
        "finance": "68% 48%",
        "investment": "58% 40%",
        "job": "65% 50%",
        "health": "52% 46%",
        "vehicle": "72% 52%",
        "housing": "58% 50%",
        "food": "60% 48%",
        "knowledge": "66% 46%",
        "routine": "52% 48%",
        "growth": "55% 42%",
    }
    position_css = "".join(
        f'.los-world-scene-{feature} .los-subsystem-world-hero>img{{object-position:{position}!important}}'
        for feature, position in feature_positions.items()
    )
    frame_css = {
        "soft-oval": "border-radius:42px 42px 16px 42px!important",
        "wave-cut": "clip-path:polygon(0 5%,96% 0,100% 92%,5% 100%)",
        "forged-edge": "clip-path:polygon(2% 0,100% 4%,97% 100%,0 94%)",
        "orbital-ring": "border-radius:50% 50% 24px 24px/18% 18% 24px 24px!important",
        "nebula-cut": "clip-path:polygon(0 0,94% 3%,100% 88%,8% 100%)",
        "branch-frame": "border-radius:28px 8px 36px 12px!important",
        "horizon-frame": "border-radius:48px 48px 10px 10px!important",
        "linear-frame": "border-radius:2px!important",
        "folio-frame": "border-radius:4px 24px 24px 4px!important",
        "vault-frame": "border-radius:10px 10px 36px 36px!important",
        "open-arch": "border-radius:52px 52px 16px 16px!important",
        "deep-arch": "border-radius:18px 18px 44px 44px!important",
        "gilded-arch": "border-radius:30px!important",
    }[language.frame]
    return (
        '<style data-living-world-integration="v2.097">'
        f':root{{--los-world-composition:"{language.composition}";--los-world-lighting:"{language.lighting}";'
        f'--los-world-texture:"{language.texture}";--los-world-material:"{language.material}"}}'
        '.los-world-stage,.los-world-scene-scope{isolation:isolate}'
        '.los-world-identity{position:absolute;z-index:28;left:3%;top:3%;display:flex;flex-direction:column;gap:2px;'
        'padding:9px 13px;border:1px solid var(--los-line);border-radius:var(--los-radius-sm);'
        'background:color-mix(in srgb,var(--los-surface-strong) 72%,transparent);backdrop-filter:blur(14px);'
        'color:var(--los-paper);pointer-events:none}'
        '.los-world-identity small{font-size:.56rem;letter-spacing:.13em;color:var(--los-muted)}'
        '.los-world-identity strong{font-family:var(--los-font-serif);font-size:.9rem;color:var(--los-gold-bright)}'
        '.los-world-identity span{font-size:.56rem;color:var(--los-paper-soft)}'
        '.los-world-style-layer:after,.los-world-scene-scope:after{content:"";position:absolute;z-index:2;inset:0;pointer-events:none;'
        'background:radial-gradient(circle at 18% 22%,color-mix(in srgb,var(--los-gold) 16%,transparent),transparent 32%),'
        'linear-gradient(135deg,transparent 40%,color-mix(in srgb,var(--los-seed) 8%,transparent));mix-blend-mode:screen}'
        f'.los-world-frame-{language.frame} .los-subsystem-world-hero{{{frame_css}}}'
        '.stApp:has([data-living-world-context]) .los-user-navigation{background:linear-gradient(135deg,'
        'color-mix(in srgb,var(--los-surface-strong) 88%,transparent),color-mix(in srgb,var(--los-gold) 10%,transparent))!important;'
        'border-color:var(--los-line-strong)!important;box-shadow:var(--los-glow)!important}'
        '.stApp:has(.los-world-scene-scope) [data-testid="stMetric"],'
        '.stApp:has(.los-world-scene-scope) [data-testid="stDataFrame"],'
        '.stApp:has(.los-world-scene-scope) [data-baseweb="tab-list"],'
        '.stApp:has(.los-world-scene-scope) [data-baseweb="input"]>div,'
        '.stApp:has(.los-world-scene-scope) [data-baseweb="select"]>div{'
        'background:color-mix(in srgb,var(--los-surface-strong) 86%,transparent)!important;'
        'border-color:var(--los-line)!important;box-shadow:var(--los-shadow)!important}'
        '.stApp:has(.los-world-scene-scope) .stButton>button{background:linear-gradient(180deg,'
        'color-mix(in srgb,var(--los-gold) 18%,transparent),color-mix(in srgb,var(--los-surface) 92%,transparent))!important;'
        'border-color:var(--los-line-strong)!important;color:var(--los-paper)!important}'
        + nav_css
        + position_css
        + '@media(max-width:760px){.los-world-identity{left:2%;top:2%;padding:6px 9px}.los-world-identity span{display:none}'
        '[class*="st-key-world_node_"] .stButton>button{min-height:48px!important}}'
        '</style>'
    )
