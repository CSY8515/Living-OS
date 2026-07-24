# Responsive and Accessibility Guideline

## Viewport classes

- Desktop: 1440 px and 1920 px reference widths
- Notebook: 1024–1439 px
- Tablet: 768–1023 px, portrait and landscape
- Mobile: 320–767 px, including 320, 360, 390, and 430 px checks

These are validation points, not device detection rules. Components respond to
available space and content.

## Responsive behavior

- Preserve the primary action and current status above secondary detail.
- Recompose spatial worlds into a linear, meaningful order on narrow screens.
- Avoid horizontal page overflow.
- Data tables may use a contained scroll region only when a readable stacked
  representation would lose meaning.
- Navigation and Home return remain reachable without hover.
- Safe-area insets and virtual keyboards must not cover primary actions.

## Accessibility requirements

- Text and essential icons meet WCAG AA contrast.
- Interactive targets are at least 44 by 44 CSS pixels.
- Keyboard focus is visible and ordered.
- Headings follow a meaningful hierarchy.
- Form controls have persistent labels and associated errors.
- Status is communicated with text or icon shape in addition to color.
- Screen-reader labels describe icon-only and spatial controls.
- `prefers-reduced-motion` removes nonessential movement.
- Zoom to 200% must preserve actions and content.

## Required verification

Future UI work is incomplete until it includes:

1. automated page render and no-overflow checks at reference widths;
2. keyboard-only navigation;
3. focus visibility;
4. touch-target measurement;
5. automated contrast/semantic checks where tooling permits;
6. manual screen-reader smoke testing;
7. reduced-motion verification;
8. screenshots for desktop, tablet, and mobile review.
