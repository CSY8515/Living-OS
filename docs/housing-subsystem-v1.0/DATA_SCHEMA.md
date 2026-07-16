# Housing Subsystem v1.0 Data Schema

Schema version: 1

## `housing_candidates`

Primary key: `candidate_id`. Records contain name, deposit, monthly rent, maintenance fee and known flag, computed total monthly cost, commute minutes, parking flag, option and special-note text, score, grade, serialized deductions, lifecycle status, and UTC creation/update timestamps.

Money uses non-negative integer units. Commute is 0-1440 minutes. Boolean values are constrained to 0/1. Score is 0-100; grade is A-D; status is active, shortlisted, rejected, or selected.

## Supporting tables

- `housing_meta`: schema and subsystem version metadata.
- `housing_migration_ledger`: source path, SHA-256 checksum, deterministic result, and import timestamp.

SQLite foreign keys are enabled, writes use immediate transactions, and the database path is sensitive and excluded from Git.
