# Living OS v2.097 Theme World Integration Contract

## Objective

Complete the existing Ultra Brain Theme Consumer so Living OS renders a real
Living World hierarchy instead of repeating one Parent Background across Home
and Feature screens. This is a presentation-architecture hotfix, not a new user
feature, editor, domain capability, or runtime redesign.

## Authorized recovery

- Connect the inherited `ultra-brain.ui/v1` contract to a canonical
  `LivingWorldDefinition`.
- Define one Theme World language and a distinct Feature identity for every
  current Living screen.
- Restrict the inherited Parent World asset to Living Home.
- Preserve repository-owned Feature art and expose exact asset status instead
  of substituting the Parent Background.
- Integrate functional overlays, shared navigation, Lock/Override, revision,
  adjustments, and responsive behavior with the resolved World.
- Validate representative Calm and Ocean paths through Ultra Brain, OS
  Ecosystem, Living Home, Finance, Health, and Vehicle.

## Architecture boundary

- Runtime changes remain under `subsystems/experience/engines/`.
- Ultra Brain remains the Theme source and customization owner.
- OS Ecosystem remains the contract router.
- Living OS remains the Theme consumer and Feature scene owner.
- Universal Learning Engine and the Ultra Brain UI Editor are out of scope.
- Domain behavior, persistence, databases, migrations, deployment topology,
  authentication, and user data are unchanged.

## Presentation contract

- `Home`: consumes the inherited Theme World asset and renders Living identity.
- `Feature`: consumes Theme World language plus a Feature-specific main object,
  navigation object, composition, layout, and owned Feature asset.
- A Feature never receives the Parent Background as a fallback.
- Missing Theme-specific Feature concept art is classified `ASSET REQUIRED`.
- Official Feature art may remain visible as `reused-official-feature` while the
  World language, frame, material, lighting, texture, and functional chrome are
  applied.
- Lock, Override, revision, and active Theme state survive Streamlit reruns and
  navigation according to the incoming contract.

## Release gates

- Current `main` synchronized with `origin/main` before implementation.
- Theme Consumer, World Definition, Home, Feature identity, navigation,
  representative scene, Lock/Override, and state tests PASS.
- Full Living OS automatic test suite PASS.
- Desktop and mobile localhost Downstream verification PASS.
- Browser console/runtime error check PASS.
- Version, architecture, contract, asset-status, and release documents agree.
- Normal commit and push to validated `main`.
- GitHub Release tag: `v2.097`.
- Existing Streamlit deployment and Production smoke check PASS.
