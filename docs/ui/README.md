# Living OS Official UI Documentation

This directory is the design contract for future official Living OS UI work.
v2.0.5 stores the contract only; it does not authorize a full visual redesign.

Every implementation tool and contributor must read the documents in this order:

1. `OFFICIAL_DESIGN_BIBLE.md`
2. `VISUAL_LANGUAGE.md`
3. `INTERACTION_GUIDELINE.md`
4. `KOREAN_UI_GUIDELINE.md`
5. `RESPONSIVE_ACCESSIBILITY_GUIDELINE.md`
6. `CONCEPT_ART/README.md` and the registered original concept files
7. `UI_FOUNDATION_COMPATIBILITY_CONTRACT.md`
8. `THEME_WORLD_INTEGRATION_CONTRACT.md`

The official Concept Art is the visual source of truth. Documentation translates
that source into implementation constraints; it is not permission to invent a
different aesthetic.

When design guidance conflicts with data integrity, privacy, accessibility, or
domain behavior, the safety and domain contracts win. UI code must remain in the
Experience layer and must not bypass Subsystem facades.
