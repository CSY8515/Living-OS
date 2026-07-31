# Living OS v2.0.9.4 — UI Privacy Hotfix

Living OS v2.0.9.4 is a focused Stable hotfix. It does not add features or change storage, migration, authentication, backup, BYOK, or subsystem architecture contracts.

## Fixed

- Prevented long subsystem names, including 자기계발, from being clipped inside the world identity plaque.
- Replaced the report source editor with a readable period and life-area summary.
- Kept deterministic Markdown and JSON report payloads inside the existing storage and processing boundary.
- Removed report IDs and internal lifecycle wording from ordinary success messages.
- Hid Streamlit developer toolbar options and detailed runtime exception information from the user surface.

## Preserved

- Existing v2.0.9.3 user data and repository contracts.
- Dummy-free production behavior.
- Owner deletion and verified reset behavior.
- Session-only production BYOK behavior.
- Existing Streamlit deployment and data-storage model.
