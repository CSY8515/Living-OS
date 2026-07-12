# Changelog

All notable Living OS changes are recorded in this file.

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
