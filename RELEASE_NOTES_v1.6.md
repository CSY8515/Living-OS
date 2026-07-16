# Living OS v1.6 Stable Release Notes

Release date: 2026-07-16

Living OS v1.6 adds Food Subsystem v1.0 behind one `FoodSubsystem` facade. Approved capabilities are ingredient lifecycle, recipes with ordered instructions and ingredient lines, cooking records, meal records, explicit owner-entered nutrition arithmetic, deterministic Food reports, isolated lazy SQLite storage, and one Food page.

Food never imports or synchronizes Health or Finance. Nutrition is deterministic owner-entered arithmetic, not medical guidance. Unsupported unit conversions and incomplete nutrition inputs are disclosed instead of estimated.

Verification: seven focused Food tests pass; the complete 88-test regression passes; compilation, architecture boundaries, SQLite integrity and foreign keys, every-page no-write smoke coverage, and headless Streamlit startup pass.

All v1.5 manifests, imports, behavior, schemas, data paths, owner data, migration rules, and safety guarantees remain compatible. No Food migration exists or ran. No owner data changed.

Excluded: Inventory, Calendar, Health/Finance coupling, AI, external integrations, automation, unit conversion, nutrition estimation, legacy migration, and unrelated refactoring.
