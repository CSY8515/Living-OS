# GitHub Release: Living OS v1.3 Stable

Suggested tag: `v1.3`

Living OS v1.3 Stable introduces Health Subsystem v1.0 as a first-class, independently replaceable subsystem.

## Highlights

- Weight CRUD, baseline comparison, and change tracking
- InBody skeletal muscle, body fat, BMI, and timeline
- Health checkups, assessments, follow-ups, and metric comparisons
- Sleep, exercise, and nutrition records
- Weight, InBody, sleep, and exercise trends
- Target weight and body-fat goals with progress
- Daily, weekly, and monthly Health reports with next actions

## Architecture and safety

- One public `HealthSubsystem` facade with private engines
- No direct dependency on Finance or another domain subsystem
- Lazy transactional SQLite storage with sensitive privacy classification
- Actual Health data excluded from Git
- Explicit, read-only migration dry run; no automatic migration
- Checksum-guarded, idempotent, transactional migration apply

## Verification

- Health tests: 7/7 passed
- Full Living OS regression: 67/67 passed
- SQLite integrity and foreign-key checks passed
- Compile, architecture, privacy, Streamlit page smoke, and headless server startup passed

Real Health migration is not included in the release action and must be approved separately. Streamlit Community Cloud local storage is not durable for long-lived Health data.

