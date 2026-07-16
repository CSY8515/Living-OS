# Health Subsystem v1.0 Data Schema

Schema version: 1. Privacy class: sensitive.

| Table | Core fields |
|---|---|
| `weight_records` | UUID, measured date, weight kg, note, created/updated timestamps |
| `body_compositions` | UUID, measured date, skeletal muscle kg, body-fat %, BMI, note |
| `health_checkups` | UUID, checked date, title, assessment, follow-up date, finite numeric metrics JSON, note |
| `sleep_records` | UUID, sleep date, timezone-aware bed/wake timestamps, computed minutes, fatigue 1-5, note |
| `exercise_records` | UUID, exercise date, activity, minutes, optional repetitions, note |
| `nutrition_records` | UUID, meal date/type, note, optional Health goal foreign key |
| `health_goals` | UUID, name, optional target weight/body-fat, dates, lifecycle status |
| `health_migration_ledger` | resolved source path, SHA-256, result receipt, imported timestamp |
| `health_meta` | schema and subsystem versions |

Measurements are stored as bounded two-decimal strings to avoid binary floating-point persistence drift. Public results expose numeric floats. Reads do not initialize the schema.

