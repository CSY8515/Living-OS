# Interaction Guideline

## Interactive region

An Interactive Region is the complete visible and semantic area that responds
to one user intention. Its boundary must be immediately recognizable.
Decoration, ambient light, orbit lines, and background objects are not
interactive unless they have a visible control treatment and accessible label.

## Required states

Every interactive component defines:

- default;
- hover;
- keyboard focus;
- active/pressed;
- disabled;
- loading when an action is pending;
- success or failure feedback.

Hover is enhancement only. Touch and keyboard users must receive equivalent
information.

## Click and touch targets

- The hit area includes the complete visible control.
- Adjacent destructive and safe actions require separation.
- Touch targets are at least 44 by 44 CSS pixels.
- Icon-only controls require a visible tooltip and an accessible name.
- Disabled controls explain why when the reason is not obvious.

## Keyboard

- All actions are reachable in a logical order.
- Focus remains visible against every material.
- Enter/Space behavior follows native control conventions.
- Dialogs and overlays contain focus and return it to the invoking control.
- No keyboard trap is permitted.

## Screen readers

- Controls use stable names that describe the action.
- Current state is programmatically exposed.
- Dynamic success, failure, and validation feedback is announced.
- Decorative objects are hidden from accessibility APIs.

## Motion

- Motion explains location, state transition, or continuity.
- Ambient motion never blocks input or reading.
- Reduced-motion preference removes orbit, float, parallax, and nonessential
  transition effects.
- Essential state changes remain understandable without animation.
