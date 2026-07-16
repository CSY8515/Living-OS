# Living OS v1.5 Stable Release Notes

Release date: 2026-07-16

Release state: published and production verified.

Living OS v1.5 adds Vehicle Subsystem v1.0 behind one `VehicleSubsystem` facade. Approved capabilities are vehicle profiles, kilometer odometer history, maintenance records and schedules, fuel/charging costs, deterministic vehicle reports, isolated lazy SQLite storage, and one Vehicle page.

All v1.4 imports, manifests, pages, data paths, schemas, and safety contracts remain compatible. Vehicle has no legacy migration and no dependency on another domain subsystem. GPS/trips, reminders, AI, integrations, Finance posting, release, and deployment are excluded.

## Verification

- Vehicle isolated tests: 7/7 passed.
- Complete Living OS regression: 81/81 passed.
- Compilation, architecture boundaries, SQLite integrity/foreign keys, every-page no-write smoke, and headless Streamlit startup passed.
- No repository Vehicle database, owner-data change, or migration occurred.

## Release controls

Official commit `ba3510254c4323181d032aaddd2e85f9178980f6`, push, GitHub Release publication, Streamlit reboot, and production verification completed. Production serves Living OS v1.5 Stable.
