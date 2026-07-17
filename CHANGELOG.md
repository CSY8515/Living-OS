# Changelog

All notable Living OS changes are recorded in this file.

## v1.8 Development

- Added independent Knowledge and Routine Subsystems with dedicated SQLite schemas behind the shared Database Foundation adapter.
- Added Knowledge CRUD, search, classification, archive, validation, health, execution logging, and management metrics.
- Added Routine CRUD, scheduling, due calculation, completion/failure/skip outcomes, streaks, history, validation, health, execution logging, and management metrics.
- Registered both subsystems in the common database registry and Streamlit module catalog.
- Added four Streamlit surfaces and removed obsolete version-specific compatibility notices from active UI.
- Added v1.8 unit, integration, regression, UI, and architecture coverage.

## v1.7 Stable — Database Foundation

### Added

- Added peer `DatabaseSubsystem` and `DatabaseManagementSubsystem` facades with explicit Data Plane and Control Plane separation.
- Added SQLite connection/transaction contracts, Schema v2 Migration Registry, canonical CRUD/Search/Archive Repository, shared Metadata, Integrity checks, Execution records, Backup/Restore history, Health checks, Performance/Capacity observations, and operational reports.
- Added explicit Settings controls for reviewed Migration, recorded Health Check, verified Backup, Restore preflight/approval, warning display, and Database Management Report generation.
- Added the v1.7 Architecture and Database documentation packs and release-preparation evidence.

### Compatibility and safety

- Preserved Finance, Health, Housing, Vehicle, Food, Hub, JSON/JSONL, and compatibility paths.
- Startup does not apply the v1.7 Migration. Real user data has not been migrated or deleted.
- Backup and Restore use checksums, staging, SQLite Integrity checks, a pre-restore safety backup, rollback behavior, and preserved control-plane history.
- User Approval, the final 98-test release gate, official commit, GitHub Release, Streamlit production deployment, Stable Verification, and Archive completed on 2026-07-17.

## v1.6 Stable - Food Subsystem v1.0

### Added

- Added the independently mountable `FoodSubsystem` facade and private Ingredient, Recipe, Cooking, Meal, Nutrition, Report, Storage, and Validation engines.
- Added ingredient and recipe lifecycle, transactional recipe lines, cooking and meal records, explicit deterministic nutrition arithmetic, Food reports, lazy SQLite storage, and one Food page.
- Added the append-only v1.6 manifest, seven focused Food tests, architecture enforcement, and implementation documentation.

### Compatibility and release control

- Preserved v1.5 manifests, imports, behavior, paths, schemas, owner data, and safety contracts.
- Compilation and the complete 88-test suite pass. Official commit, push, GitHub Release, Streamlit deployment, and production verification completed on 2026-07-16. No migration was performed.

## v1.5 Stable - Vehicle Subsystem v1.0

### Added

- Added the independently mountable `VehicleSubsystem` facade and private Vehicle, Odometer, Maintenance, Schedule, Energy, Report, Storage, and Validation engines.
- Added profile lifecycle, monotonic kilometer history, maintenance records/due schedules, fuel/charging costs, deterministic reports, lazy SQLite storage, and the Vehicle page.
- Added the v1.5 manifest, seven isolated Vehicle tests, architecture enforcement, and release-readiness documentation.

### Compatibility and release control

- Preserved v1.4 manifests, imports, behavior, paths, schemas, owner data, and safety contracts.
- Compilation and the complete 81-test suite pass. Official commit, push, GitHub Release, Streamlit deployment, and production verification completed on 2026-07-16. No Vehicle migration exists or ran.

## v1.4 Stable - Housing Subsystem v1.0

### Added

- Added the independently mountable `HousingSubsystem` facade and private Candidate, Scoring, Comparison, Housing Report, Migration, Storage, and Validation engines.
- Added candidate CRUD, deterministic ranking, cost and status summaries, and attributable scoring deductions.
- Added lazy transactional sensitive SQLite storage and explicit dry-run-first, checksum-guarded legacy JSON migration.
- Added the v1.4 manifest and Housing page integration.

### Compatibility and release control

- Preserved all v1.3 manifests, behavior, imports, data contracts, release workflows, and the legacy Housing API and JSON source.
- Official commit, push, GitHub Release, Streamlit deployment, and production verification completed on 2026-07-16. No real Housing migration was performed.

## v1.3 Stable - Health Subsystem v1.0

### Added

- Added the independently mountable `HealthSubsystem` facade and nine approved domain engines.
- Added weight CRUD/baseline, InBody, checkup follow-up, sleep, exercise, nutrition, trends, goals, and daily/weekly/monthly reports.
- Added lazy transactional sensitive SQLite storage and explicit checksum-guarded JSON migration with read-only dry run.
- Added v1.3 manifest and Health page integration.

### Verification

- Added 7 Health tests covering engines, interface, validation, migration, trends, goals, reports, and privacy.
- Passed compile and the complete 67-test Living OS regression suite.

### Release control

- Official commit, push, GitHub Release, Streamlit deployment, and production verification completed on 2026-07-16. No real owner Health migration was performed.

## Finance Subsystem v1.0

### Added

- Added the independently mountable FinanceSubsystem facade and private Ledger, Budget, Cash Flow, Savings, Report, Migration, Storage, and Validation Engines.
- Added lazy transactional SQLite storage, health checks, export snapshots, immutable monthly closings, and deterministic money/rate handling.
- Registered Finance v1.0.0 in the Living OS catalog and added its canonical and compatibility-mode page.
- Added explicit checksum-guarded, idempotent, transactional migration from finance_budget.json while preserving the legacy API and file.

### Verification

- Added 11 isolated Finance tests and extended architecture and Streamlit coverage.
- Passed the complete 60-test Living OS suite.

## v1.2 Stable

### Changed

- Migrated the internal runtime to Foundation, Operations, Insight, Experience, and Compatibility subsystems.
- Relocated all runtime functions and classes below subsystem engine packages.
- Converted previous public module paths into exact canonical module aliases.
- Rewrote canonical imports to follow subsystem ownership.
- Aligned application, catalog, storage, settings, reports, migration, tests, and docs with v1.2.

### Compatibility

- Preserved existing features, entry points, imports, monkeypatch targets, schemas, data paths, backup behavior, explicit migration, and AI safety.
- Preserved V2_STABLE_MANIFESTS as a pre-release compatibility alias.

### Verification

- Preserved the 44-test baseline and expanded it to 49 passing tests.
- Added runtime-placement, forbidden-import, module-identity, and catalog-alias checks.
- Passed compile, unit, integration, security, migration, and Streamlit page smoke verification.

## v1.0 Stable

### Stabilized

- Centralized runtime version labeling and updated current labels to `v1.0 Stable`.
- Added atomic, flushed JSON and text writes with temporary-file cleanup on failure.
- Prevented malformed Daily Log, Archive, Settings, and Module Registry sources from being silently overwritten by later saves.
- Added collision-resistant report and backup filenames.
- Made report file creation and report-index updates consistent by removing a newly created report when its index update fails.
- Reused resilient report discovery on the Reports page.
- Validated all recognized backup content before restore and added best-effort rollback for write failures.
- Added safe user-facing errors for core save, report, settings, backup, and restore actions.
- Verified and preserved the v0.9 GPT-5.6 Luna, Terra, and Sol model identifiers and manual model selection.

### Verification

- Expanded isolated regression and Streamlit smoke coverage from 17 to 31 tests.
- Added v0.9 backup fixtures, schema-field assertions, version checks, atomic-write tests, malformed-source protection, report consistency checks, and AI non-save tests.
- Preserved all ten v0.9 pages, storage interfaces, and JSON/JSONL schemas.

### Compatibility

- No data migration is required.
- No database, authentication, notifications, background automation, autonomous AI writes, agents, embeddings, vector database, or fine-tuning was added.

## v0.9

### Added

- Secure session, environment, and operating-system credential-store OpenAI API-key configuration.
- Manual OpenAI connection testing with sanitized errors.
- Read-only AI Analysis page for explicitly selected Daily Logs and Decisions.
- Optional AI report-draft generation with a separate explicit save action.

### Compatibility

- All v0.8 pages, features, deterministic reports, and storage interfaces are preserved.
- Existing JSON and JSONL schemas are unchanged.
- No authentication, notifications, background tasks, automation, or autonomous AI actions were added.

## v0.8

### Added

- Shared internal date handling for Analytics and Review.
- Isolated regression tests for storage, dashboard, dates, Review, Analytics, and reports.

### Fixed

- Dashboard reviewable-decision count now uses only `draft`, `active`, and `review` records.
- Report discovery safely ignores files that become inaccessible.
- Current application, dashboard, settings, and generated-report version labels are consistent.

### Compatibility

- All existing pages and storage interfaces are preserved.
- Existing JSON and JSONL schemas are unchanged.
- No database, AI, authentication, notifications, or automation were added.

## v0.7

### Added

- Read-only Review Workspace.
- Consolidated review metrics for Daily Logs, Decisions, Archive items, and Reports.
- Manual decision-review queue for `draft`, `active`, and `review` records.
- Date-range and decision-status filters.
- Combined recent-activity view with safe empty and malformed-date handling.

### Changed

- Added Review to the existing sidebar navigation.
- Updated approved application and generated-report version labels to v0.7.
- Updated release documentation for the v0.7 scope.

### Compatibility

- Existing pages and storage interfaces are preserved.
- Existing JSON and JSONL schemas are unchanged.
- No database, AI, authentication, notifications, or automation were added.
