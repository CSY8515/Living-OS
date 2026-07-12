# Living OS v0.7 Roadmap

## Version

- Target version: Living OS v0.7
- Baseline: Living OS v0.6 Stable
- Release theme: Review Workspace
- Status: Approved for implementation planning

## Objectives

- Add a focused review workflow for existing Living OS records.
- Turn the read-only summaries introduced in v0.6 into a practical review view.
- Help users identify recent activity and decisions that need manual attention.
- Preserve the current modular, local-first, JSON/JSONL architecture.
- Deliver the smallest backward-compatible increment after v0.6 Analytics.

## Scope

v0.7 adds a read-only Review Workspace to the existing Streamlit application. The workspace combines data already available from Daily Log, Decision Log, Archive, Reports, and Analytics without changing how those modules store data.

The release includes:

- A new Review page in the existing application navigation.
- A consolidated overview of recent records.
- A manual decision-review queue derived from existing decision statuses.
- Date-range and status filters using existing record fields.
- Clear empty, invalid-date, and no-match states.
- Version and documentation updates required for the v0.7 release.

## New Modules

### Review Module

Planned file: `modules/review.py`

Responsibilities:

- Load existing records through current module and storage interfaces.
- Build read-only review summaries.
- Identify reviewable decisions using existing status values.
- Filter review data without modifying source records.
- Render the Review Workspace UI.

The module must remain independent and must not introduce direct writes to JSON or JSONL files.

## Features

### Review Overview

- Display counts for Daily Logs, Decisions, Archive items, and Reports.
- Display recent activity across existing record types.
- Reuse existing timestamps and dates when ordering records.

### Decision Review Queue

- List decisions whose existing status is `draft`, `active`, or `review`.
- Allow filtering by existing decision status.
- Show the decision title, identifier, status, and latest available timestamp.
- Link the workflow conceptually to Decision Log without duplicating or rewriting records.

### Review Filters

- Support All time, Last 7 days, Last 30 days, and This month ranges.
- Apply date filters only when a valid existing date or timestamp is available.
- Handle missing or malformed values safely.

### Recent Activity

- Show recent Daily Logs, Decisions, Archive items, and saved Report files.
- Keep the view read-only.
- Present useful empty states when a source contains no records.

### Navigation and Version Display

- Add Review to the existing sidebar navigation.
- Update visible application and generated-report version labels to v0.7.
- Preserve every existing page and route.

## Files Expected to Change

### New file

- `modules/review.py`

### Existing application files

- `app.py` — register the Review page and update the displayed version.
- `modules/storage.py` — update the default version label only if needed; no storage-format changes.
- `modules/report_system.py` — update the generated report version label only.

### Documentation files

- `README.md` — document the v0.7 version and Review Workspace.
- `ROADMAP.md` — record v0.7 completion without replacing historical roadmap content.
- `KNOWN_ISSUES.md` — update the current-version references and v0.7 limitations.
- `CHANGELOG.md` — create or update the release history as required by the release architecture.

### Verification files

- Existing tests, if present when implementation begins.
- A narrowly scoped review-module test file may be added if the repository adopts a test directory before or during the approved implementation.

### Data files

- No existing data file or JSON/JSONL schema is expected to change.
- `state/settings.json` may receive a version-value update only if explicitly approved during implementation; its keys and structure must remain unchanged.

## Architecture Impact

- No architecture change.
- The existing Streamlit entry point remains the application shell.
- The current module-per-feature structure remains unchanged.
- The Review module is a read-only consumer of existing module interfaces.
- JSON and JSONL remain the only persistence formats.
- No database, service layer, background process, or external integration is introduced.
- Existing data flow remains Raw Data → Project Data → Decision Report → Living Rule → Living OS.

## Compatibility

- Full backward compatibility with v0.6 data and behavior is required.
- Existing JSON object shapes, field names, and nesting must not change.
- Existing JSONL decision records must remain readable without migration.
- Existing navigation pages and features must continue to work.
- Missing optional fields and malformed dates must fail safely in the Review view.
- Existing Finance and Housing source assets must remain untouched and available for future migration.
- The application must continue to run locally with the current dependency range.

## Out of Scope

- Database storage or data migration.
- AI analysis, recommendation, classification, or summarization.
- Authentication, accounts, roles, or permissions.
- Notifications, reminders, scheduling, or automation.
- Background tasks or external services.
- Changes to existing JSON or JSONL schemas.
- Editing records from the Review Workspace.
- New Finance, Housing, Vehicle, Food, Health, Learning, or other expansion-module functionality.
- Changes to the approved architecture or project structure.
- Cloud deployment and release automation.

## Acceptance Criteria

- The Review page is available from the existing sidebar.
- All v0.6 pages remain available and function as before.
- Review metrics are derived from existing Daily Log, Decision Log, Archive, and Report data.
- The decision-review queue includes only records with `draft`, `active`, or `review` status.
- Date-range and status filters produce consistent results.
- Missing files, empty datasets, missing optional fields, and malformed dates do not crash the application.
- The Review Workspace does not write to any data file.
- Existing JSON and JSONL schemas are unchanged.
- No database, AI, authentication, notification, or automation capability is added.
- Visible version references are consistent with Living OS v0.7.
- The application starts successfully using the existing requirements.
- Relevant tests and manual smoke checks pass.
- Documentation accurately describes the implemented v0.7 scope.

## Release Checklist

- Confirm the approved v0.7 roadmap before application changes begin.
- Re-read Master Blueprint, Architecture, Module Specs, Release Plan, and Design Principles.
- Verify the working tree and preserve unrelated user changes.
- Implement only the Review Workspace scope defined here.
- Confirm no existing JSON or JSONL schema changed.
- Run syntax and import checks.
- Run available automated tests.
- Start the Streamlit application and smoke-test every existing page.
- Verify Review filters, empty states, malformed-date handling, and decision-status selection.
- Verify the Review page performs no data writes.
- Confirm version labels and documentation are consistent.
- Update `CHANGELOG.md` for v0.7.
- Review the final diff for architecture and scope compliance.
- Obtain user approval before any commit, push, tag, or release action.
