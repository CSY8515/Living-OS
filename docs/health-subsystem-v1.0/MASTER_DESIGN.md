# Health Subsystem v1.0 Master Design

Health is an independently replaceable Living OS v1.3 subsystem. Its only public boundary is `HealthSubsystem`; all engines and storage stay private.

## Placement

    Ultra Brain -> Meta OS Ecosystem -> OS Ecosystem -> Capability
      -> Living OS -> Health Subsystem -> Engine -> Function

## Boundary rules

- External code imports `HealthSubsystem` only.
- Health engines import only Health engines and the Python standard library.
- Health never imports Finance, Vehicle, Housing, Investment, Job, or Personal Growth.
- Experience may call the Health facade; no caller imports Health engines.
- Reads do not create storage. Writes are transactional.
- Owner data lives below ignored `data/health/`; tests use isolated fixtures.
- Migration is explicit and never automatic.

## Engines

- Weight: record, update, delete, baseline, change.
- Body Composition: InBody measurements, muscle mass, body fat, BMI, timeline.
- Health Checkup: assessment, follow-up, metrics, baseline comparison.
- Sleep: bedtime, wake time, duration, fatigue.
- Exercise: activity, duration, count, statistics.
- Nutrition: meal, note, optional Health goal linkage.
- Trend: weight, InBody, sleep, and exercise series.
- Goal: target weight/body-fat and latest-measurement progress.
- Health Report: daily, weekly, monthly, baseline, and next actions.
- Storage, Validation, and Migration: private supporting engines.

## Data, privacy, and rollback

SQLite schema version 1 separates all Health record types and migration receipts. UUID identifiers, ISO-8601 dates, bounded decimal measurements, integer durations/counts, and finite numeric checkup metrics form the stable contract. The database is sensitive, ignored by Git, and never created by reads or dry runs.

Storage paths are injectable, so replacement versions can run against a copy. Schema changes require explicit transactional migration. Rollback restores the previous code and database snapshot; v1.3 does not mutate any v1.2 data contract.
