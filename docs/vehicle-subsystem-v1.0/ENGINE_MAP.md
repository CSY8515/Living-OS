# Vehicle Subsystem v1.0 Engine Map

| Engine | Responsibility |
|---|---|
| Vehicle | Validated profile create, get, list, update, archive |
| Odometer | Kilometer history and monotonic neighbor validation |
| Maintenance | Service history |
| Schedule | Due criteria, evaluation, and completion linkage |
| Energy | Fuel/charge quantities and costs |
| Report | Deterministic status, distance, maintenance, and cost summaries |
| Storage | Lazy SQLite schema, transactions, integrity, export |
| Validation | Text, identifiers, dates, enums, and numeric boundaries |

No engine is a supported external import. Experience uses only `VehicleSubsystem`.

Status: implemented and verified through the public facade and isolated tests.
