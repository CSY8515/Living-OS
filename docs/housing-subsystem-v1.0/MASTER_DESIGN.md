# Housing Subsystem v1.0 Master Design

Housing is an independently replaceable Living OS v1.4 subsystem. Its only public boundary is `HousingSubsystem`; engines and storage stay private.

## Boundary rules

- External code imports `HousingSubsystem` only.
- Housing engines import only Housing engines and the Python standard library.
- Housing never imports Finance, Health, Compatibility, or another domain subsystem.
- Experience may call the Housing facade; no caller imports Housing engines.
- Reads and reports do not create storage; writes are transactional.
- Owner data lives below ignored `data/housing/`; tests use isolated temporary stores.
- Migration is dry-run-first, explicit, and never automatic.

## Stable behavior

The v1.0 scoring contract exactly retains the legacy monthly-cost, commute, parking, and missing-maintenance-fee deductions and A-D grade thresholds. New functionality adds validated CRUD, status tracking, deterministic ranking, reports, health metadata, and export snapshots without changing the legacy API.
