from __future__ import annotations

from html import escape
from typing import Any, Mapping

from subsystems.experience.engines.theme_adapter import ThemeAdapter
from subsystems.experience.engines.ui_contracts import ThemeContract
from subsystems.experience.engines.ui_registry import DEFAULT_UI_REGISTRY, UIRegistry


ULTRA_BRAIN_UI_SESSION_KEY = "ultra_brain_ui_contract"


class LivingOSUIInterface:
    """Public Experience-layer boundary for Ultra Brain UI configuration."""

    def __init__(
        self,
        registry: UIRegistry = DEFAULT_UI_REGISTRY,
        adapter: ThemeAdapter | None = None,
    ) -> None:
        self.registry = registry
        self.adapter = adapter or ThemeAdapter(registry)

    def resolve(
        self, settings: ThemeContract | Mapping[str, Any] | None = None
    ) -> ThemeContract:
        return self.adapter.resolve(settings if settings is not None else self.active_settings())

    def render_theme(
        self,
        base_css: str,
        settings: ThemeContract | Mapping[str, Any] | None = None,
    ) -> str:
        return self.adapter.render(base_css, self.resolve(settings))

    def install(self, settings: ThemeContract | Mapping[str, Any]) -> ThemeContract:
        """Validate and install one session-scoped contract supplied by Ultra Brain."""
        contract = self.adapter.resolve(settings)
        import streamlit as st

        st.session_state[ULTRA_BRAIN_UI_SESSION_KEY] = contract.to_payload()
        return contract

    def active_settings(self) -> Mapping[str, Any] | None:
        import streamlit as st

        value = st.session_state.get(ULTRA_BRAIN_UI_SESSION_KEY)
        return value if isinstance(value, Mapping) else None

    def asset(
        self,
        key: str,
        fallback: str,
        settings: ThemeContract | Mapping[str, Any] | None = None,
    ) -> str:
        contract = self.resolve(settings)
        return self.adapter.asset(key, fallback, contract)

    def icon(
        self,
        key: str,
        fallback: str,
        settings: ThemeContract | Mapping[str, Any] | None = None,
    ) -> str:
        contract = self.resolve(settings)
        return self.adapter.icon(key, fallback, contract)

    def scope_marker(self, module_id: str) -> str:
        self.registry.module(module_id)
        return (
            f'<span class="los-ui-scope los-ui-scope-{escape(module_id)}" '
            'aria-hidden="true" hidden></span>'
        )

    def audit(self) -> dict[str, object]:
        return {
            **self.registry.audit(),
            "contract": "ultra-brain.ui/v1",
            "session_key": ULTRA_BRAIN_UI_SESSION_KEY,
        }


LIVING_OS_UI = LivingOSUIInterface()


def render_compatible_theme(
    base_css: str,
    settings: ThemeContract | Mapping[str, Any] | None = None,
) -> str:
    return LIVING_OS_UI.render_theme(base_css, settings)


def install_ultra_brain_ui_settings(
    settings: ThemeContract | Mapping[str, Any],
) -> ThemeContract:
    return LIVING_OS_UI.install(settings)


def resolve_ui_asset(key: str, fallback: str) -> str:
    return LIVING_OS_UI.asset(key, fallback)


def resolve_ui_icon(key: str, fallback: str) -> str:
    return LIVING_OS_UI.icon(key, fallback)


def ui_scope_marker(module_id: str) -> str:
    return LIVING_OS_UI.scope_marker(module_id)
