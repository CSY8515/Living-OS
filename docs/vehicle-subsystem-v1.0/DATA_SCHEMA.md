# Vehicle Subsystem v1.0 Data Schema

Schema version: 1. Default sensitive store: `data/vehicle/vehicle.sqlite3`.

- `vehicle_vehicles`: identity, display name, manufacturer, model, optional model year, powertrain, active/archive status, timestamps.
- `vehicle_odometer_readings`: vehicle, date, integer kilometers, note, timestamp; neighbor readings enforce chronological monotonicity.
- `vehicle_maintenance_records`: vehicle, service type, date, optional kilometers, integer cost, provider, note, timestamp.
- `vehicle_maintenance_schedules`: vehicle, service type, date and/or kilometer due criterion, lifecycle status, optional completion record, timestamps.
- `vehicle_energy_logs`: vehicle, fuel/charge type, date, optional kilometers, positive thousandths-of-unit quantity, integer cost, note, timestamp.
- `vehicle_meta`: schema and subsystem versions.

Foreign keys are enabled. Writes are transactional. Reads do not create storage. Money is stored in integer owner-currency units; distance is kilometers. No migration ledger exists because there is no legacy source.

Status: implemented and verified. SQLite integrity is `ok`; foreign-key violations are zero.
