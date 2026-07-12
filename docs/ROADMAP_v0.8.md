# Living OS v0.8 Roadmap

## Version

- Target version: Living OS v0.8
- Baseline: Living OS v0.7 Stable
- Release theme: Core Reliability and Consistency
- Status: Approved for implementation

## Objectives

- Correct existing dashboard and version-label inconsistencies.
- Consolidate duplicated read-only date handling without changing filter behavior.
- Improve resilience when existing data or report files are unavailable or malformed.
- Add focused regression tests for the existing core behavior.
- Preserve the local, single-user, Streamlit, JSON/JSONL architecture.

## Scope

### Dashboard consistency

- Display the actual count of decisions with `draft`, `active`, or `review` status.
- Display the v0.8 version caption.

### Shared date handling

- Use one internal date utility for Analytics and Review.
- Preserve All time, Last 7 days, Last 30 days, and This month filters.
- Keep date-window boundaries inclusive.
- Support existing ISO dates and timestamps.
- Exclude missing or malformed dates safely from bounded ranges.

### Read-path resilience

- Preserve safe fallbacks for missing, empty, malformed, and incorrectly shaped JSON/JSONL data.
- Ignore inaccessible or disappearing report files during report discovery.
- Do not rewrite, migrate, or repair source records automatically.

### Version consistency

- Update the sidebar, dashboard, generated reports, default settings, and current settings value to v0.8.
- Do not add, remove, or rename settings keys.

### Regression tests

- Cover storage fallbacks, dashboard counts, date parsing and filtering, Review selection and ordering, Analytics counters, and report generation.
- Keep tests isolated from real workspace data.

## Architecture and Compatibility

- No architecture or project-structure change.
- No page or feature removal.
- No JSON or JSONL schema change.
- No data migration.
- No new runtime dependency.
- Existing module interfaces and navigation remain available.

## Files Expected to Change

- `app.py`
- `modules/dashboard.py`
- `modules/storage.py`
- `modules/analytics.py`
- `modules/review.py`
- `modules/report_system.py`
- `modules/date_utils.py`
- `tests/`
- `state/settings.json` (version value only)
- `README.md`
- `ROADMAP.md`
- `KNOWN_ISSUES.md`
- `CHANGELOG.md`
- `docs/ROADMAP_v0.8.md`

## Acceptance Criteria

- All nine existing pages remain available.
- Dashboard reviewable count includes only `draft`, `active`, and `review` decisions.
- Analytics and Review use consistent inclusive date-window rules.
- Missing and malformed data does not crash read-only operations.
- Existing JSON and JSONL shapes remain unchanged.
- No data migration or real user-data write occurs during tests.
- All visible and generated version labels identify v0.8.
- Automated regression tests and manual all-page smoke checks pass.

## Out of Scope

- New pages or major features.
- Database storage or data migration.
- JSON or JSONL schema changes.
- AI, authentication, notifications, reminders, scheduling, or automation.
- Editing from Analytics or Review.
- Expansion-module implementation.
- Cloud deployment, external services, or unrelated dependency upgrades.
- Architecture or repository restructuring.
- Commit, push, tag, or release actions.
