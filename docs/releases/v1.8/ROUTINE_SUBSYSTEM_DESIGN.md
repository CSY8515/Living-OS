# Routine Subsystem Design

Routine is an independent data-owning Subsystem (`SUB-ROUTINE`, v1.0.0). Routine records own frequency, rule, priority, lifecycle, dates, next due time, completion/failure counts, streak, timestamps, and metadata. Execution records own schedule, outcome, note, duration, and metadata.

Supported routine states are `DRAFT`, `ACTIVE`, `PAUSED`, `COMPLETED`, and `ARCHIVED`. Execution states are `PENDING`, `COMPLETED`, `FAILED`, and `SKIPPED`. Daily, weekly, calendar-month, and numeric-day interval scheduling are deterministic; end-of-month dates clamp safely. Completion increments count and streak; failure increments failure count and clears streak; skip preserves both.

The private schema is stored under `data/routine/routine.sqlite3` only after first write or management initialization. Management reports lifecycle totals, due work, outcomes, best streak, history, adapter health, registry state, and control-plane execution results.
