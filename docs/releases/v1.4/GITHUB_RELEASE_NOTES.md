# GitHub Release: Living OS v1.4 Stable

Suggested tag: `v1.4`

Living OS v1.4 introduces Housing Subsystem v1.0 as a first-class independently replaceable subsystem.

## Highlights

- Validated Housing candidate CRUD and lifecycle status
- Legacy-compatible scoring with attributable deductions
- Deterministic ranking, cost summaries, distributions, and next actions
- Lazy transactional sensitive SQLite storage
- Explicit dry-run-first, checksum-guarded, idempotent migration

## Compatibility and verification

All v1.3 manifests, imports, features, data contracts, Finance, Health, and legacy Housing behavior remain intact. The legacy Housing JSON is not changed. Housing tests pass 7/7; the complete Living OS suite passes 74/74; compilation, SQLite integrity, architecture/privacy checks, page smoke, and headless startup pass.

No real Housing migration is included. Streamlit Community Cloud storage remains non-durable for long-lived Housing data.
