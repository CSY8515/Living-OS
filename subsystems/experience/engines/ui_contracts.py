from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


UI_CONTRACT_ID = "ultra-brain.ui"
UI_CONTRACT_VERSION = 1
UI_MODES = ("dark", "light", "system")

REQUIRED_DESIGN_TOKENS: dict[str, tuple[str, ...]] = {
    "color": (
        "background",
        "background_soft",
        "surface",
        "surface_strong",
        "glass",
        "border",
        "border_strong",
        "text",
        "text_soft",
        "muted",
        "accent",
        "accent_bright",
        "secondary",
        "success",
        "warning",
        "danger",
        "background_image",
    ),
    "typography": ("font_sans", "font_serif", "base_size", "heading_weight"),
    "shape": (
        "radius",
        "radius_small",
        "card_radius",
        "button_radius",
        "dialog_radius",
        "widget_radius",
    ),
    "shadow": ("card", "button", "dialog", "glow"),
    "layout": ("max_width", "page_padding", "gap", "sidebar_width"),
    "motion": ("enabled", "scale", "easing"),
}

MODULE_OVERRIDE_TOKENS = {
    "accent",
    "accent_bright",
    "background",
    "background_soft",
    "surface",
    "surface_strong",
    "text",
    "text_soft",
    "font_sans",
    "font_serif",
    "background_image",
    "icon_color",
}


def _copy_nested(value: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in value.items():
        result[str(key)] = _copy_nested(item) if isinstance(item, Mapping) else item
    return result


def validate_css_value(value: Any, *, label: str) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty CSS token value.")
    lowered = value.lower()
    if any(marker in value for marker in (";", "{", "}")) or "</style" in lowered:
        raise ValueError(f"{label} contains unsafe CSS syntax.")
    if any(marker in lowered for marker in ("javascript:", "expression(", "@import")):
        raise ValueError(f"{label} contains an unsafe CSS operation.")


def validate_resource_value(value: Any, *, label: str, icon: bool = False) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    lowered = value.lower().strip()
    if any(marker in value for marker in ("\x00", "\r", "\n", "<", ">")):
        raise ValueError(f"{label} contains unsafe markup syntax.")
    if not icon and any(marker in value for marker in ('"', "'")):
        raise ValueError(f"{label} contains unsafe resource delimiters.")
    if "javascript:" in lowered or lowered.startswith("data:text"):
        raise ValueError(f"{label} contains an unsafe resource scheme.")
    if lowered.startswith("data:") and not lowered.startswith(
        ("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/gif;base64,", "data:image/webp;base64,")
    ):
        raise ValueError(f"{label} uses an unsupported inline resource type.")


@dataclass(frozen=True)
class DesignTokenSet:
    values: Mapping[str, Mapping[str, Any]]

    def validate(self) -> None:
        for group, required in REQUIRED_DESIGN_TOKENS.items():
            values = self.values.get(group)
            if not isinstance(values, Mapping):
                raise ValueError(f"Missing design-token group: {group}.")
            missing = set(required).difference(values)
            if missing:
                raise ValueError(
                    f"Missing {group} design tokens: {', '.join(sorted(missing))}."
                )
            for name, value in values.items():
                validate_css_value(value, label=f"{group}.{name}")
        enabled = self.values["motion"]["enabled"]
        scale = self.values["motion"]["scale"]
        if not isinstance(enabled, bool):
            raise ValueError("motion.enabled must be a boolean.")
        if not isinstance(scale, (int, float)) or isinstance(scale, bool) or scale < 0:
            raise ValueError("motion.scale must be a non-negative number.")

    def to_payload(self) -> dict[str, dict[str, Any]]:
        self.validate()
        return {
            group: _copy_nested(values)
            for group, values in self.values.items()
        }


@dataclass(frozen=True)
class ComponentContract:
    component_id: str
    selectors: tuple[str, ...]
    properties: tuple[str, ...]
    token_groups: tuple[str, ...]

    def validate(self) -> None:
        if not self.component_id.strip() or not self.selectors:
            raise ValueError("Component identity and selectors are required.")
        if not self.properties or not self.token_groups:
            raise ValueError("Component properties and token groups are required.")
        if any("{" in selector or "}" in selector for selector in self.selectors):
            raise ValueError("Component selectors must not contain CSS blocks.")


@dataclass(frozen=True)
class ModuleUIContract:
    module_id: str
    pages: tuple[str, ...]
    scene: str = ""

    def validate(self) -> None:
        if not self.module_id.strip() or not self.pages:
            raise ValueError("Module UI identity and page coverage are required.")


@dataclass(frozen=True)
class ThemeContract:
    theme_id: str
    mode: str
    design_tokens: DesignTokenSet
    component_overrides: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    module_overrides: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    assets: Mapping[str, str] = field(default_factory=dict)
    icons: Mapping[str, str] = field(default_factory=dict)
    contract_id: str = UI_CONTRACT_ID
    contract_version: int = UI_CONTRACT_VERSION
    source: str = "living-os"

    def validate(self) -> None:
        if self.contract_id != UI_CONTRACT_ID:
            raise ValueError("Unsupported UI contract identity.")
        if self.contract_version != UI_CONTRACT_VERSION:
            raise ValueError("Unsupported UI contract version.")
        if not self.theme_id.strip() or self.mode not in UI_MODES:
            raise ValueError("Theme identity and supported mode are required.")
        if not self.source.strip():
            raise ValueError("Theme source is required.")
        self.design_tokens.validate()
        for component_id, properties in self.component_overrides.items():
            if not component_id.strip() or not isinstance(properties, Mapping):
                raise ValueError("Component overrides must be named objects.")
            for name, value in properties.items():
                validate_css_value(value, label=f"component.{component_id}.{name}")
        for module_id, tokens in self.module_overrides.items():
            if not module_id.strip() or not isinstance(tokens, Mapping):
                raise ValueError("Module overrides must be named objects.")
            unknown = set(tokens).difference(MODULE_OVERRIDE_TOKENS)
            if unknown:
                raise ValueError(
                    f"Unknown module override tokens: {', '.join(sorted(unknown))}."
                )
            for name, value in tokens.items():
                validate_css_value(value, label=f"module.{module_id}.{name}")
        for group_name, group in (("assets", self.assets), ("icons", self.icons)):
            for name, value in group.items():
                if not str(name).strip():
                    raise ValueError(f"{group_name} entries require names and values.")
                validate_resource_value(
                    value,
                    label=f"{group_name}.{name}",
                    icon=group_name == "icons",
                )

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        return {
            "contract_id": self.contract_id,
            "contract_version": self.contract_version,
            "theme_id": self.theme_id,
            "mode": self.mode,
            "source": self.source,
            "design_tokens": self.design_tokens.to_payload(),
            "component_overrides": _copy_nested(self.component_overrides),
            "module_overrides": _copy_nested(self.module_overrides),
            "assets": dict(self.assets),
            "icons": dict(self.icons),
        }
