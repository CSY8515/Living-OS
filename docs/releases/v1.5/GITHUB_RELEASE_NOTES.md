# Living OS v1.5 — Vehicle Subsystem v1.0

Living OS v1.5 adds an isolated Vehicle subsystem for profiles, kilometer odometer history, maintenance records and schedules, fuel/charging costs, and deterministic status reports.

Highlights:

- One supported `VehicleSubsystem` facade with private engines.
- Lazy transactional sensitive SQLite storage and no write-on-read behavior.
- New Vehicle page and v1.5 module manifest.
- Complete v1.4 compatibility; no legacy Vehicle migration.
- 7/7 Vehicle tests and 81/81 full regression tests passing.

No owner-data migration is required or included. Streamlit Community Cloud local storage is ephemeral and should not be treated as durable Vehicle storage.
