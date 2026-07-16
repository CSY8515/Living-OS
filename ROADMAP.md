# Living OS Roadmap

## v1.5 - Vehicle Subsystem v1.0

Implementation, isolated verification, full 81-test regression, documentation synchronization, and deployment-readiness review are complete. No migration exists or ran. Commit, GitHub Release, and deployment remain separate owner-approved actions. Current status: release approval pending.

Exact scope: vehicle profiles, kilometer odometer history, maintenance records and date/odometer schedules, fuel/charging cost logs, deterministic vehicle reports, isolated lazy SQLite storage, a v1.5 manifest, one Vehicle page, tests, and documentation. GPS/trips, reminders, AI, external integrations, Finance coupling, legacy migration, release, and deployment are excluded.

The governing plan is `docs/v1.5/IMPLEMENTATION_PLAN.md`. Only that exact scope is authorized.

## v1.4 - Housing Subsystem v1.0

Implementation, isolated verification, full regression, documentation synchronization, release publication, Streamlit deployment, and production verification are complete. Real Housing migration remains a separate owner-approved action and was not performed. Current status: Stable, production.

## v1.3 - Health Subsystem v1.0

Implementation, isolated verification, full regression, documentation sync, release publication, Streamlit deployment, and production verification are complete. Real Health migration remains a separate owner-approved operation. Current status: Stable, production.

## v1.2 — Subsystem Architecture Migration

Implementation and verification complete; repository release action pending.

Completed: baseline inventory, subsystem classification, engine relocation, exact legacy import aliases, data-path preservation, v1.2 label alignment, architecture tests, docs synchronization, and regression verification.

No later feature is approved here. Future capabilities require separate approval and an explicit Subsystem → Engine → Function boundary.

## Finance Subsystem v1.0

Implemented: independent facade and storage, Ledger, Budget, Cash Flow, Savings, Report, explicit Migration, Living OS catalog/page integration, isolated tests, docs, and release draft. Live legacy migration and release publication remain owner actions.
