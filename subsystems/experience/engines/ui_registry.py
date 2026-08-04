from __future__ import annotations

from typing import Iterable

from subsystems.experience.engines.ui_contracts import (
    ComponentContract,
    DesignTokenSet,
    ModuleUIContract,
    ThemeContract,
)


REQUIRED_UI_COMPONENTS = {
    "background",
    "layout",
    "navigation",
    "dashboard",
    "screen",
    "header",
    "card",
    "button",
    "dialog",
    "widget",
    "icon",
    "font",
    "color",
    "animation",
    "module_surface",
}


OFFICIAL_DARK_TOKENS = DesignTokenSet(
    {
        "color": {
            "background": "#02070b",
            "background_soft": "#07100f",
            "surface": "rgba(10,17,16,.82)",
            "surface_strong": "rgba(13,22,19,.94)",
            "glass": "rgba(15,24,21,.68)",
            "border": "rgba(216,182,109,.18)",
            "border_strong": "rgba(224,190,112,.55)",
            "text": "#f3eddc",
            "text_soft": "#bbb7aa",
            "muted": "#858b84",
            "accent": "#d8b66d",
            "accent_bright": "#f1d58a",
            "secondary": "#a8bf68",
            "success": "#a8c97a",
            "warning": "#d4a95f",
            "danger": "#d98179",
            "background_image": "radial-gradient(circle at 50% -10%,rgba(94,125,78,.13),transparent 34rem),radial-gradient(circle at 92% 22%,rgba(216,182,109,.055),transparent 32rem),linear-gradient(155deg,#07100f 0%,#02070b 52%,#030605 100%)",
        },
        "typography": {
            "font_sans": '"Pretendard Variable","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","Segoe UI",sans-serif',
            "font_serif": '"Noto Serif KR","Batang",serif',
            "base_size": "16px",
            "heading_weight": "650",
        },
        "shape": {
            "radius": "18px",
            "radius_small": "11px",
            "card_radius": "18px",
            "button_radius": "11px",
            "dialog_radius": "18px",
            "widget_radius": "11px",
        },
        "shadow": {
            "card": "0 18px 48px rgba(0,0,0,.32)",
            "button": "0 10px 24px rgba(0,0,0,.20)",
            "dialog": "0 30px 90px rgba(0,0,0,.44)",
            "glow": "0 0 0 1px rgba(216,182,109,.05),0 14px 40px rgba(0,0,0,.28),0 0 36px rgba(216,182,109,.035)",
        },
        "layout": {
            "max_width": "1560px",
            "page_padding": "1.15rem 2.2rem 5rem",
            "gap": "1rem",
            "sidebar_width": "292px",
        },
        "motion": {
            "enabled": True,
            "scale": 1.0,
            "easing": "cubic-bezier(.2,.75,.22,1)",
        },
    }
)


OFFICIAL_LIGHT_TOKENS = DesignTokenSet(
    {
        "color": {
            "background": "#f4f1e8",
            "background_soft": "#ebe5d8",
            "surface": "rgba(255,255,255,.86)",
            "surface_strong": "rgba(255,255,255,.96)",
            "glass": "rgba(255,255,255,.72)",
            "border": "rgba(111,91,50,.22)",
            "border_strong": "rgba(111,91,50,.48)",
            "text": "#211f19",
            "text_soft": "#4f4a3e",
            "muted": "#777164",
            "accent": "#8c6a27",
            "accent_bright": "#a67c2d",
            "secondary": "#657b45",
            "success": "#4f7a43",
            "warning": "#9a6921",
            "danger": "#a04b43",
            "background_image": "radial-gradient(circle at 50% -10%,rgba(101,123,69,.12),transparent 34rem),radial-gradient(circle at 92% 22%,rgba(140,106,39,.08),transparent 32rem),linear-gradient(155deg,#f4f1e8 0%,#ebe5d8 52%,#f7f4ec 100%)",
        },
        "typography": {
            "font_sans": '"Pretendard Variable","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","Segoe UI",sans-serif',
            "font_serif": '"Noto Serif KR","Batang",serif',
            "base_size": "16px",
            "heading_weight": "650",
        },
        "shape": {
            "radius": "18px",
            "radius_small": "11px",
            "card_radius": "18px",
            "button_radius": "11px",
            "dialog_radius": "18px",
            "widget_radius": "11px",
        },
        "shadow": {
            "card": "0 18px 48px rgba(65,53,31,.14)",
            "button": "0 10px 24px rgba(65,53,31,.12)",
            "dialog": "0 30px 90px rgba(65,53,31,.20)",
            "glow": "0 0 0 1px rgba(140,106,39,.06),0 14px 40px rgba(65,53,31,.10)",
        },
        "layout": {
            "max_width": "1560px",
            "page_padding": "1.15rem 2.2rem 5rem",
            "gap": "1rem",
            "sidebar_width": "292px",
        },
        "motion": {
            "enabled": True,
            "scale": 1.0,
            "easing": "cubic-bezier(.2,.75,.22,1)",
        },
    }
)


OFFICIAL_COMPONENT_CONTRACTS = (
    ComponentContract("background", (".stApp",), ("background", "color"), ("color",)),
    ComponentContract("layout", (".block-container",), ("max-width", "padding", "gap"), ("layout",)),
    ComponentContract("navigation", ("[data-testid=\"stSidebar\"]", ".los-user-navigation"), ("background", "border-color", "color", "width"), ("color", "layout")),
    ComponentContract("dashboard", (".los-metric-section", ".los-signal-grid"), ("background", "border-color", "border-radius", "box-shadow"), ("color", "shape", "shadow")),
    ComponentContract("screen", (".los-page-hero", ".los-world-scene-scope"), ("background", "border-color", "border-radius", "box-shadow"), ("color", "shape", "shadow")),
    ComponentContract("header", (".los-page-header", ".los-page-copy", ".los-workspace-rail"), ("background", "border-color", "color", "font-family"), ("color", "typography")),
    ComponentContract("card", ("[data-testid=\"stMetric\"]", ".los-card", ".los-signal-card", ".los-data-card", ".los-insight-cell"), ("background", "border", "border-color", "border-radius", "box-shadow", "color"), ("color", "shape", "shadow")),
    ComponentContract("button", (".stButton>button", "[data-testid=\"stFormSubmitButton\"] button", "[data-testid=\"baseButton-secondary\"]"), ("background", "border", "border-color", "border-radius", "box-shadow", "color", "font-family"), ("color", "typography", "shape", "shadow")),
    ComponentContract("dialog", ("[data-testid=\"stDialog\"]>div", "[data-baseweb=\"popover\"]"), ("background", "border", "border-color", "border-radius", "box-shadow", "color"), ("color", "shape", "shadow")),
    ComponentContract("widget", ("[data-baseweb=\"input\"]>div", "[data-baseweb=\"textarea\"]>div", "[data-baseweb=\"select\"]>div", "[data-baseweb=\"tab-list\"]"), ("background", "border", "border-color", "border-radius", "box-shadow", "color", "font-family"), ("color", "typography", "shape", "shadow")),
    ComponentContract("icon", (".los-orb", ".los-page-glyph", ".los-rail-icon", ".los-world-symbol"), ("background", "color", "filter", "font-family"), ("color", "typography")),
    ComponentContract("font", ("html", "body", "[class*=\"css\"]"), ("font-family", "font-size", "font-weight"), ("typography",)),
    ComponentContract("color", ("h1", "h2", "h3", "h4", "p", "a"), ("color", "background", "border-color"), ("color",)),
    ComponentContract("animation", (".stApp *",), ("animation-duration", "animation-timing-function", "transition-duration", "transition-timing-function"), ("motion",)),
    ComponentContract("module_surface", ("[class*=\"st-key-subsystem_world_hero_\"]", ".los-world-threshold"), ("background", "border-color", "border-radius", "box-shadow", "color"), ("color", "shape", "shadow")),
)


OFFICIAL_MODULE_UI_CONTRACTS = (
    ModuleUIContract("dashboard", ("Command Center",), "living"),
    ModuleUIContract("journal", ("Daily Log",), "today"),
    ModuleUIContract("decision", ("Decision Log",), "decision"),
    ModuleUIContract("reports", ("Reports",), "reports"),
    ModuleUIContract("knowledge", ("Archive",), "knowledge"),
    ModuleUIContract("analytics", ("Analytics", "Timeline", "Search"), "analytics"),
    ModuleUIContract("review", ("Review",), "decision"),
    ModuleUIContract("ai_briefing", ("AI Analysis",), "assistant"),
    ModuleUIContract("documents", ("Documents",), "knowledge"),
    ModuleUIContract("finance", ("Finance",), "finance"),
    ModuleUIContract("food", ("Food",), "food"),
    ModuleUIContract("health", ("Health",), "health"),
    ModuleUIContract("housing", ("Housing",), "housing"),
    ModuleUIContract("vehicle", ("Vehicle",), "vehicle"),
    ModuleUIContract("knowledge_subsystem", ("Knowledge", "Knowledge Management"), "knowledge"),
    ModuleUIContract("routine", ("Routine", "Routine Management"), "routine"),
    ModuleUIContract("investment", ("Investment", "Investment Management"), "investment"),
    ModuleUIContract("job", ("Job", "Job Management"), "job"),
    ModuleUIContract("personal_growth", ("Personal Growth", "Personal Growth Management"), "growth"),
    ModuleUIContract("collaboration", ("Collaboration", "Collaboration Management"), "collaboration"),
    ModuleUIContract("database", ("Database",), "living"),
    ModuleUIContract("database_management", ("Database Management",), "living"),
    ModuleUIContract("module_manager", ("Module Manager",), "living"),
    ModuleUIContract("settings", ("Settings",), "living"),
)


class UIRegistry:
    """Versioned registry for themes, shared components, and module UI scopes."""

    def __init__(
        self,
        *,
        themes: Iterable[ThemeContract] = (),
        components: Iterable[ComponentContract] = (),
        modules: Iterable[ModuleUIContract] = (),
    ) -> None:
        self._themes: dict[str, ThemeContract] = {}
        self._components: dict[str, ComponentContract] = {}
        self._modules: dict[str, ModuleUIContract] = {}
        for theme in themes:
            self.register_theme(theme)
        for component in components:
            self.register_component(component)
        for module in modules:
            self.register_module(module)

    def register_theme(self, theme: ThemeContract) -> None:
        theme.validate()
        self._themes[theme.theme_id] = theme

    def register_component(self, component: ComponentContract) -> None:
        component.validate()
        self._components[component.component_id] = component

    def register_module(self, module: ModuleUIContract) -> None:
        module.validate()
        self._modules[module.module_id] = module

    def theme(self, theme_id: str) -> ThemeContract:
        if theme_id not in self._themes:
            raise ValueError(f"Unknown UI theme: {theme_id}.")
        return self._themes[theme_id]

    def theme_for_mode(self, mode: str) -> ThemeContract:
        preferred = "living-os-light" if mode == "light" else "living-os-dark"
        return self.theme(preferred)

    def component(self, component_id: str) -> ComponentContract:
        if component_id not in self._components:
            raise ValueError(f"Unknown UI component: {component_id}.")
        return self._components[component_id]

    def module(self, module_id: str) -> ModuleUIContract:
        if module_id not in self._modules:
            raise ValueError(f"Unknown UI module: {module_id}.")
        return self._modules[module_id]

    def component_ids(self) -> tuple[str, ...]:
        return tuple(self._components)

    def module_ids(self) -> tuple[str, ...]:
        return tuple(self._modules)

    def audit(self) -> dict[str, object]:
        missing = sorted(REQUIRED_UI_COMPONENTS.difference(self._components))
        return {
            "status": "PASS" if not missing else "FAIL",
            "themes": len(self._themes),
            "components": len(self._components),
            "modules": len(self._modules),
            "missing_components": missing,
        }


DEFAULT_UI_REGISTRY = UIRegistry(
    themes=(
        ThemeContract("living-os-dark", "dark", OFFICIAL_DARK_TOKENS),
        ThemeContract("living-os-light", "light", OFFICIAL_LIGHT_TOKENS),
    ),
    components=OFFICIAL_COMPONENT_CONTRACTS,
    modules=OFFICIAL_MODULE_UI_CONTRACTS,
)
