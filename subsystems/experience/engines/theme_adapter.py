from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Mapping

from subsystems.experience.engines.ui_contracts import (
    DesignTokenSet,
    ThemeContract,
    UI_CONTRACT_ID,
    UI_CONTRACT_VERSION,
)
from subsystems.experience.engines.ui_registry import DEFAULT_UI_REGISTRY, UIRegistry


ALLOWED_THEME_FIELDS = {
    "contract_id",
    "contract_version",
    "theme_id",
    "mode",
    "source",
    "design_tokens",
    "component_overrides",
    "module_overrides",
    "assets",
    "icons",
}

TOKEN_TO_VARIABLE = {
    "accent": "--los-gold",
    "accent_bright": "--los-gold-bright",
    "background": "--los-space",
    "background_soft": "--los-space-soft",
    "surface": "--los-surface",
    "surface_strong": "--los-surface-strong",
    "text": "--los-paper",
    "text_soft": "--los-paper-soft",
    "font_sans": "--los-font-sans",
    "font_serif": "--los-font-serif",
    "background_image": "--los-background-image",
    "icon_color": "--los-icon-color",
}


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(base))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _hex_rgb(value: str, fallback: str) -> str:
    text = value.strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", text):
        text = "#" + "".join(char * 2 for char in text[1:])
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        return ",".join(str(int(text[index:index + 2], 16)) for index in (1, 3, 5))
    return fallback


def _css_value(value: Any) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


class ThemeAdapter:
    """Validate Ultra Brain settings and adapt them to the Living OS CSS surface."""

    def __init__(self, registry: UIRegistry = DEFAULT_UI_REGISTRY) -> None:
        self.registry = registry

    def resolve(
        self, settings: ThemeContract | Mapping[str, Any] | None = None
    ) -> ThemeContract:
        if isinstance(settings, ThemeContract):
            contract = settings
        else:
            payload = dict(settings or {})
            unknown = set(payload).difference(ALLOWED_THEME_FIELDS)
            if unknown:
                raise ValueError(
                    f"Unknown Ultra Brain UI settings: {', '.join(sorted(unknown))}."
                )
            mode = str(payload.get("mode", "dark"))
            requested_theme = str(payload.get("theme_id", ""))
            try:
                base = self.registry.theme(requested_theme) if requested_theme else self.registry.theme_for_mode(mode)
            except ValueError:
                base = self.registry.theme_for_mode(mode)
            base_payload = base.to_payload()
            design_overrides = payload.get("design_tokens", {})
            if not isinstance(design_overrides, Mapping):
                raise ValueError("design_tokens must be an object.")
            contract = ThemeContract(
                theme_id=requested_theme or str(base_payload["theme_id"]),
                mode=mode,
                design_tokens=DesignTokenSet(
                    _deep_merge(base_payload["design_tokens"], design_overrides)
                ),
                component_overrides=_deep_merge(
                    base_payload["component_overrides"],
                    self._mapping(payload.get("component_overrides", {}), "component_overrides"),
                ),
                module_overrides=_deep_merge(
                    base_payload["module_overrides"],
                    self._mapping(payload.get("module_overrides", {}), "module_overrides"),
                ),
                assets={
                    **base_payload["assets"],
                    **self._string_mapping(payload.get("assets", {}), "assets"),
                },
                icons={
                    **base_payload["icons"],
                    **self._string_mapping(payload.get("icons", {}), "icons"),
                },
                contract_id=str(payload.get("contract_id", UI_CONTRACT_ID)),
                contract_version=int(payload.get("contract_version", UI_CONTRACT_VERSION)),
                source=str(payload.get("source", "ultra-brain" if payload else "living-os")),
            )
        self._validate_registry_references(contract)
        contract.validate()
        return contract

    def render(
        self,
        base_css: str,
        settings: ThemeContract | Mapping[str, Any] | None = None,
    ) -> str:
        contract = self.resolve(settings)
        official_default = self._is_official_default(contract)
        transformed = base_css if official_default else self._adapt_palette(base_css, contract)
        scale = float(contract.design_tokens.values["motion"]["scale"])
        if not official_default and scale != 1.0:
            transformed = self._scale_motion(transformed, scale)
        return transformed + "\n" + self.compatibility_css(contract)

    def compatibility_css(self, contract: ThemeContract) -> str:
        contract.validate()
        if self._is_official_default(contract):
            return '<style data-living-os-ui-contract="v2.096"></style>'
        values = contract.design_tokens.values
        colors = values["color"]
        typography = values["typography"]
        shape = values["shape"]
        shadows = values["shadow"]
        layout = values["layout"]
        motion = values["motion"]
        accent_rgb = _hex_rgb(str(colors["accent"]), "216,182,109")
        secondary_rgb = _hex_rgb(str(colors["secondary"]), "168,191,104")
        variables = {
            "--los-space": colors["background"],
            "--los-space-soft": colors["background_soft"],
            "--los-surface": colors["surface"],
            "--los-surface-strong": colors["surface_strong"],
            "--los-glass": colors["glass"],
            "--los-line": colors["border"],
            "--los-line-strong": colors["border_strong"],
            "--los-paper": colors["text"],
            "--los-paper-soft": colors["text_soft"],
            "--los-muted": colors["muted"],
            "--los-gold": colors["accent"],
            "--los-gold-bright": colors["accent_bright"],
            "--los-seed": colors["secondary"],
            "--los-moss": colors["secondary"],
            "--los-good": colors["success"],
            "--los-warn": colors["warning"],
            "--los-danger": colors["danger"],
            "--los-accent-rgb": accent_rgb,
            "--los-secondary-rgb": secondary_rgb,
            "--los-space-ambient": accent_rgb,
            "--los-font-sans": typography["font_sans"],
            "--los-font-serif": typography["font_serif"],
            "--los-base-size": typography["base_size"],
            "--los-heading-weight": typography["heading_weight"],
            "--los-radius": shape["radius"],
            "--los-radius-sm": shape["radius_small"],
            "--los-card-radius": shape["card_radius"],
            "--los-button-radius": shape["button_radius"],
            "--los-dialog-radius": shape["dialog_radius"],
            "--los-widget-radius": shape["widget_radius"],
            "--los-shadow": shadows["card"],
            "--los-button-shadow": shadows["button"],
            "--los-dialog-shadow": shadows["dialog"],
            "--los-glow": shadows["glow"],
            "--los-layout-max-width": layout["max_width"],
            "--los-layout-padding": layout["page_padding"],
            "--los-layout-gap": layout["gap"],
            "--los-sidebar-width": layout["sidebar_width"],
            "--los-ease": motion["easing"],
            "--los-background-image": colors["background_image"],
            "--los-icon-color": colors["accent_bright"],
        }
        root = ";".join(f"{name}:{_css_value(value)}" for name, value in variables.items())
        color_scheme = "light dark" if contract.mode == "system" else contract.mode
        css = [
            '<style data-living-os-ui-contract="v2.096">',
            f':root{{color-scheme:{color_scheme};{root}}}',
            'html,body,[class*="css"]{font-family:var(--los-font-sans)!important;font-size:var(--los-base-size)}',
            'h1,h2,h3,h4{font-weight:var(--los-heading-weight)!important}',
            '.stApp{color:var(--los-paper)!important;background:var(--los-background-image)!important}',
            '.block-container{max-width:var(--los-layout-max-width)!important;padding:var(--los-layout-padding)!important;gap:var(--los-layout-gap)}',
            '[data-testid="stSidebar"]{width:var(--los-sidebar-width)!important}',
            '.los-world-core h1,.st-key-world_enter:before{font-family:var(--los-font-serif)!important}',
            '.los-orb,.los-page-glyph,.los-rail-icon{color:var(--los-icon-color)}',
        ]
        if contract.source != "living-os" or contract.theme_id != "living-os-dark":
            css.extend(
                (
                    '[data-testid="stMetric"],.los-card,.los-signal-card,.los-data-card,.los-insight-cell{border-radius:var(--los-card-radius)!important;box-shadow:var(--los-shadow)!important}',
                    '.stButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="baseButton-secondary"]{border-radius:var(--los-button-radius)!important;box-shadow:var(--los-button-shadow)!important;font-family:var(--los-font-sans)!important}',
                    '[data-testid="stDialog"]>div,[data-baseweb="popover"]{border-radius:var(--los-dialog-radius)!important;box-shadow:var(--los-dialog-shadow)!important}',
                    '[data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div,[data-baseweb="base-input"]{border-radius:var(--los-widget-radius)!important;font-family:var(--los-font-sans)!important}',
                )
            )
        if not bool(motion["enabled"]):
            css.append('.stApp *{animation:none!important;transition:none!important;scroll-behavior:auto!important}')
        css.extend(self._component_css(contract))
        css.extend(self._module_css(contract))
        css.append("</style>")
        return "\n".join(css)

    def asset(self, key: str, fallback: str, contract: ThemeContract) -> str:
        return str(contract.assets.get(key, fallback))

    def icon(self, key: str, fallback: str, contract: ThemeContract) -> str:
        return str(contract.icons.get(key, fallback))

    def _validate_registry_references(self, contract: ThemeContract) -> None:
        for component_id, properties in contract.component_overrides.items():
            registered = self.registry.component(component_id)
            unknown = set(properties).difference(registered.properties)
            if unknown:
                raise ValueError(
                    f"Unsupported {component_id} properties: {', '.join(sorted(unknown))}."
                )
        for module_id in contract.module_overrides:
            self.registry.module(module_id)

    def _is_official_default(self, contract: ThemeContract) -> bool:
        current = contract.to_payload()
        official = self.registry.theme("living-os-dark").to_payload()
        # Role/background assets may change independently of Living OS chrome.
        # Compare the functional UI contract while deliberately ignoring only
        # asset and icon maps so an asset-only inherited theme cannot restyle
        # metrics, inputs, typography or component geometry.
        current["assets"] = official["assets"]
        current["icons"] = official["icons"]
        return current == official

    def _component_css(self, contract: ThemeContract) -> list[str]:
        result: list[str] = []
        for component_id, properties in contract.component_overrides.items():
            component = self.registry.component(component_id)
            declarations = ";".join(
                f"{name}:{_css_value(value)}!important"
                for name, value in properties.items()
            )
            result.append(f'{",".join(component.selectors)}{{{declarations}}}')
        return result

    def _module_css(self, contract: ThemeContract) -> list[str]:
        result: list[str] = []
        for module_id, tokens in contract.module_overrides.items():
            variables: dict[str, Any] = {}
            for name, value in tokens.items():
                variable = TOKEN_TO_VARIABLE[name]
                variables[variable] = value
                if name == "accent":
                    variables["--los-space-ambient"] = _hex_rgb(str(value), "216,182,109")
                    variables["--los-accent-rgb"] = variables["--los-space-ambient"]
            declarations = ";".join(
                f"{name}:{_css_value(value)}" for name, value in variables.items()
            )
            scope = f'.stApp:has(.los-ui-scope-{module_id})'
            result.append(f"{scope}{{{declarations}}}")
            if "background_image" in tokens:
                result.append(
                    f'{scope} [data-testid="stAppViewContainer"]{{background:var(--los-background-image)!important}}'
                )
        return result

    def _adapt_palette(self, css: str, contract: ThemeContract) -> str:
        colors = contract.design_tokens.values["color"]
        replacements = {
            "#02070b": str(colors["background"]),
            "#07100f": str(colors["background_soft"]),
            "#f3eddc": str(colors["text"]),
            "#bbb7aa": str(colors["text_soft"]),
            "#858b84": str(colors["muted"]),
            "#d8b66d": str(colors["accent"]),
            "#f1d58a": str(colors["accent_bright"]),
            "#a8bf68": str(colors["secondary"]),
            "#a8c97a": str(colors["success"]),
            "#d4a95f": str(colors["warning"]),
            "#d98179": str(colors["danger"]),
            "216,182,109": _hex_rgb(str(colors["accent"]), "216,182,109"),
            "224,190,112": _hex_rgb(str(colors["accent_bright"]), "224,190,112"),
            "241,213,138": _hex_rgb(str(colors["accent_bright"]), "241,213,138"),
            "168,191,104": _hex_rgb(str(colors["secondary"]), "168,191,104"),
            "168,201,122": _hex_rgb(str(colors["success"]), "168,201,122"),
            "217,129,121": _hex_rgb(str(colors["danger"]), "217,129,121"),
        }
        result = css
        for before, after in replacements.items():
            result = result.replace(before, after)
        return result

    @staticmethod
    def _scale_motion(css: str, scale: float) -> str:
        def replace(match: re.Match[str]) -> str:
            value = float(match.group(1)) * scale
            rendered = f"{value:.4f}".rstrip("0").rstrip(".")
            return f"{rendered}{match.group(2)}"

        return re.sub(r"(?<![\w.-])(\d*\.?\d+)(ms|s)\b", replace, css)

    @staticmethod
    def _mapping(value: Any, label: str) -> dict[str, Any]:
        if not isinstance(value, Mapping):
            raise ValueError(f"{label} must be an object.")
        return deepcopy(dict(value))

    @classmethod
    def _string_mapping(cls, value: Any, label: str) -> dict[str, str]:
        mapping = cls._mapping(value, label)
        if any(not isinstance(item, str) for item in mapping.values()):
            raise ValueError(f"{label} values must be strings.")
        return {str(key): str(item) for key, item in mapping.items()}
