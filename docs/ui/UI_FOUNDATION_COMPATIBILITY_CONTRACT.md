# Living OS UI Foundation Compatibility Contract

## Purpose

Living OS owns presentation, but Ultra Brain owns future user customization. The
`ultra-brain.ui/v1` contract lets Ultra Brain provide validated theme settings to
Living OS without adding a Living OS customization screen or changing domain
runtime behavior.

## Public boundary

`subsystems.experience.install_ultra_brain_ui_settings()` is the supported input
boundary. It validates a mapping or `ThemeContract` and installs the normalized
contract for the current Streamlit session. `LivingOSUIInterface` is the public
read boundary for theme rendering, assets, icons, module scopes, and registry
audit.

Living OS accepts these contract fields:

- `contract_id`, fixed to `ultra-brain.ui`.
- `contract_version`, fixed to `1`.
- `theme_id`, `mode`, and `source`.
- `design_tokens` for color, typography, shape, shadow, layout, and motion.
- registered `component_overrides` and `module_overrides`.
- named `assets` and `icons`.

Unknown fields, components, modules, properties, and unsafe CSS token syntax are
rejected before rendering.

## Registry and adapter

`UIRegistry` contains two compatible base themes, 15 shared component contracts,
and all 24 current UI module scopes. The checked-in registry projection is
`config/ui_integration_registry.json`.

`ThemeAdapter` merges a valid external contract onto an official base theme,
maps tokens to the existing Living OS CSS surface, resolves named assets and
icons, and scopes module overrides to the active page. It does not execute
arbitrary selectors supplied by the caller. Component selectors and allowed CSS
properties are owned by the Living OS registry.

## Compatibility guarantees

- With no external contract, the official v2.095 visual CSS and assets remain
  unchanged.
- Dark, light, accent, palette, font, icon, card, button, dialog, widget,
  dashboard, animation, radius, shadow, layout, and background settings can be
  applied through the same contract.
- Finance, Food, Health (including Sleep), Housing, Vehicle, Knowledge, Routine,
  Investment, Job, Personal Growth, Collaboration, Database, and every current
  Living OS screen inherit global tokens and may receive registered module
  overrides.
- The adapter remains entirely inside the Experience layer. It does not own
  persistence, modify business data, add navigation, or depend on domain-private
  engines.
- Living OS provides no separate customization UI. Ultra Brain remains the
  customization owner.

## Asset keys

Supported named integration points are documented in the registry. Unspecified
keys always fall back to the existing checked-in Living OS asset or icon.

## Scope and lifecycle

The contract is session-scoped. Ultra Brain supplies the canonical contract
through OS Ecosystem, and Living OS validates it before rendering. v2.097 maps
that active contract to `LivingWorldDefinition`; see
`THEME_WORLD_INTEGRATION_CONTRACT.md`. No database, migration, deployment
setting, durable user preference store, or Living OS editor is added.
