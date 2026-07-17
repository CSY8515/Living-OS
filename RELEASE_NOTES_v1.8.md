# Living OS v1.8 Stable Release Notes

Living OS v1.8 adds Knowledge and Routine as independent, data-owning Subsystems while preserving every existing Stable capability and database contract.

## Highlights

- Structured Knowledge records with lifecycle, categories, tags, sources, importance, search, archive, health, and management metrics.
- Recurring Routine records with daily, weekly, calendar-month, and interval schedules.
- Routine execution history with complete, fail, and skip outcomes; counts, due state, and streak tracking.
- Dedicated Knowledge and Routine schemas behind the shared Database Foundation adapter.
- Common registry, Execution Database, integrity, backup, restore, and Database Management support.
- Four Streamlit pages: Knowledge, Routine, Knowledge Management, and Routine Management.
- Active legacy version notices updated without removing necessary compatibility boundaries.

## Compatibility and safety

- Existing Finance, Health, Vehicle, Housing, Food, Dashboard, Analytics, AI Briefing, Decision, Documents, Database, and Database Management behavior remains compatible.
- Existing schemas and user data are unchanged.
- New component schemas are additive, transactional, idempotent, and lazy.
- Shared execution logging is best-effort and cannot invalidate a committed domain write.
- Routine execution outcome and counters update atomically.

## Verification

- Python compilation passed.
- 110 unit, integration, regression, architecture, and Streamlit tests passed.
- Streamlit page smoke testing passed.
- Database registry, integrity, backup/restore, and execution integration passed.
- Critical, major, and minor known release blockers: none.
