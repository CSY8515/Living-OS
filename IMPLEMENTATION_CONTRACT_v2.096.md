# Living OS v2.096 UI Foundation Compatibility Contract

## Objective

Recover the missing UI Foundation contracts required for future Ultra Brain UI
settings while preserving the current official Living OS design and behavior.
This is a compatibility hotfix, not a new user feature or visual redesign.

## Allowed change

- Add a versioned Theme Contract and validated Design Tokens.
- Add a Theme Adapter, Component Contracts, UI Registry, and public UI Interface.
- Add registered module scopes and named background, asset, and icon integration
  points across the existing Experience layer.
- Add architecture documentation and automated compatibility regression tests.

## Architecture boundary

- All new runtime code remains under `subsystems/experience/engines/`.
- Ultra Brain owns customization; Living OS only validates and applies supplied
  settings.
- Component selectors and permitted properties are registered by Living OS.
- No persistence, domain logic, navigation, page, widget workflow, or core
  runtime composition changes are authorized.
- No arbitrary external CSS, selector, script, or secret is accepted.

## Default compatibility

- `OFFICIAL_UI_CSS` must remain byte-for-byte unchanged.
- Existing assets, icons, page order, labels, and interaction behavior remain the
  fallback when no Ultra Brain contract is installed.
- Existing screens and modules inherit the global contract and expose a hidden,
  registered module scope for targeted theme tokens.

## Release gates

- Repository and remote `main` synchronized before implementation.
- UI contract, registry, adapter, interface, module scope, and safety tests PASS.
- Existing official UI and every-page Streamlit regression tests PASS.
- Full Living OS automatic test suite PASS.
- Compilation, diff integrity, secret scan, and working-tree review PASS.
- Normal commit and push to the validated `main` branch.
- GitHub Release tag: `v2.096`.
