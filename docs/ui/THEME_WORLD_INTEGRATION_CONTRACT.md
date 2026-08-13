# Living OS Theme World Integration Contract

## Hierarchy

The supported presentation flow is:

`Ultra Brain Theme Source -> OS Ecosystem Router -> Living Theme Consumer -> Living World Definition -> Living Home or Feature Scene`

Ultra Brain owns Theme selection and editing. Living OS only validates the
received contract and renders its own World and Feature definitions. Living OS
does not expose a second customization UI.

## Living World Definition

`LivingWorldDefinition` combines:

- the inherited Theme World id and Home asset;
- Theme language: composition, frame, lighting, texture, material, and effect;
- a registry of Feature World definitions;
- the inherited revision, Lock, Override, and adjustment state.

Each `FeatureWorldDefinition` owns a main object, navigation object,
composition, visual focus, layout, material, lighting, texture, asset path, and
asset status. These fields describe a Feature scene, not a renamed copy of the
Living Home World.

## Asset ownership and fallback

- Living Home may render the inherited Parent Theme asset.
- A Feature may render an explicit Theme-specific Feature asset when one is
  registered.
- Otherwise it may preserve its repository-owned official Feature art while
  consuming the selected Theme language. This is recorded as
  `reused-official-feature`.
- If no Feature asset exists, the renderer records `asset-required` and renders
  the structural scene without copying the Parent Background.
- The Parent Theme asset is never fanned out to `background.module.*` keys.

## Identity requirements

Living Home, Finance, Health, and Vehicle must not share their principal scene
identity. The current representative identities are:

| Scene | Main object | Navigation object | Composition |
| --- | --- | --- | --- |
| Living Home | living-world | living-threshold | selected Theme composition |
| Finance | ledger-vault | vault-gate | flow-ledger |
| Health | biometric-garden | pulse-gate | recovery-ring |
| Vehicle | mobility-bay | route-compass | transit-lane |

All other registered Features follow the same identity contract.

## Functional integration

Theme language applies to the Feature frame, shared user navigation, metrics,
tables, inputs, selects, buttons, and overlays. Feature actions and public
Subsystem facades remain unchanged. Responsive behavior must retain the Living
Home nodes, Feature entry, bottom navigation, and functional controls.

## State and control

- A valid newer Theme revision becomes the active session World.
- No-query reruns and page navigation retain the active World.
- An invalid explicit propagation contract fails closed.
- Locked or non-targeted visual fields preserve the active World value.
- Override and target decisions are honored without mutating the source Theme.

## Boundary

This contract changes only Living OS Experience-layer presentation. It does not
authorize edits to Universal Learning Engine, the Ultra Brain editor, domain
logic, storage, user data, databases, migrations, authentication, deployment,
or the official downstream routing hierarchy.
