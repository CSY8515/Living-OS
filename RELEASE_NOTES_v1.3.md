# Living OS v1.3 Stable Release Notes

Release date: 2026-07-16

Living OS v1.3 introduces Health Subsystem v1.0 as an independently replaceable subsystem behind the `HealthSubsystem` facade.

## Added

- Weight record, update, delete, baseline comparison, and change calculation.
- InBody skeletal muscle, body fat, BMI, and timeline.
- Health checkups with assessment, follow-up, numeric metrics, and baseline comparison.
- Sleep duration and fatigue, exercise statistics, nutrition notes, and Health goal linkage.
- Weight, InBody, sleep, and exercise trends.
- Target weight and body-fat goals with progress.
- Daily, weekly, and monthly reports with baseline comparison and deterministic next actions.
- Lazy sensitive SQLite storage, health/interface manifests, export snapshot, and explicit legacy JSON migration.
- Health page and Living OS v1.3 module catalog integration.

## Safety and compatibility

No v1.2 data contract is changed. Health reads and reports do not create storage. Real Health data is separated from fixtures and excluded from Git. Migration never runs automatically. Health has no direct dependency on another domain subsystem.

## Verification

- Health subsystem tests: 7/7 passed.
- Living OS regression: 67/67 passed.
- SQLite integrity: `ok`; foreign-key violations: 0.
- Compile and Streamlit page smoke tests passed.
- Headless Streamlit server startup passed.

Commit, push, GitHub Release publication, real Health migration, and production deployment remain explicit owner actions.
