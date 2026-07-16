# Living OS v1.6 — Food Subsystem v1.0

Living OS v1.6 adds an isolated Food subsystem for ingredients, recipes, cooking records, meals, explicit owner-entered nutrition arithmetic, and deterministic reports.

## Highlights

- One supported `FoodSubsystem` facade with private engines.
- Lazy transactional sensitive SQLite storage; reads and page load do not create it.
- Exact decimal quantities with explicit unit matching and no automatic conversion.
- Incomplete nutrition is disclosed and never estimated.
- New Food page and append-only v1.6 manifest.
- Full backward compatibility with Living OS v1.5 Stable.

## Verification

- Food tests: 7/7 passed.
- Full regression: 88/88 passed.
- Compilation, architecture, SQLite integrity, foreign keys, every-page no-write smoke checks, and headless Streamlit startup passed.

No owner-data migration was performed. Food does not access Health or Finance.
