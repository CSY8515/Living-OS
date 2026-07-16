# Living OS v1.4 Stable Release Notes

Release date: 2026-07-16

Living OS v1.4 introduces Housing Subsystem v1.0 as an independently replaceable subsystem behind the `HousingSubsystem` facade.

## Added

- Housing candidate create, read, update, and delete operations.
- Legacy-compatible cost, commute, parking, missing-fee, score, grade, and deduction calculations.
- Deterministic candidate ranking and Housing status reports.
- Lazy sensitive SQLite storage, export snapshot, health check, and schema metadata.
- Explicit dry-run-first, transactional, checksum-guarded, idempotent legacy JSON migration.
- Housing page and Living OS v1.4 module catalog integration.

## Safety and compatibility

No v1.3 data contract or public path is changed. `V13_STABLE_MANIFESTS` remains intact. The existing `modules.housing` compatibility alias, legacy implementation, and `data/housing_candidates.json` source remain unchanged. Housing reads and reports do not create storage. Housing imports no other domain subsystem. No real Housing migration was performed.

## Release controls

The approved commit, push, GitHub Release publication, Streamlit deployment, and production verification completed on 2026-07-16. Real Housing migration remains a separate explicit owner action and was not performed.
