# Living OS v1.5 Implementation Plan

Status: **IMPLEMENTED AND VERIFIED — RELEASE APPROVAL PENDING**

Planning date: 2026-07-16
Baseline: Living OS v1.4 Stable, commit `2e4d1fa`

The baseline compiled and its complete 74-test suite passed. The owner approved this exact implementation scope on 2026-07-16. Data migration, commit, push, release, and deployment remain unauthorized.

Final result: compilation passed, all seven Vehicle tests passed, the complete 81-test suite passed, every page rendered without page-load writes, SQLite integrity and foreign keys passed, and headless Streamlit startup succeeded. No Vehicle database or owner-data migration was created in the repository.

## Release decision

Living OS v1.5 will add **Vehicle Subsystem v1.0** as a new independently replaceable sensitive-data subsystem. Vehicle is already planned in `config/module_registry.json` and the archived expansion sequence; Finance, Health, and Housing are complete. There is no legacy Vehicle implementation or data source, so this is a greenfield subsystem with no legacy migration.

## Objectives

1. Add one supported public `VehicleSubsystem` facade with private engines.
2. Record vehicle profiles, odometer history, maintenance history/due criteria, and fuel/charging costs.
3. Produce deterministic, attributable status and operating-cost summaries without AI.
4. Keep Vehicle data isolated, lazy, transactional, injectable for tests, and excluded from Git.
5. Add Vehicle through a new v1.5 manifest and one page without changing v1.4 manifests.
6. Preserve every v1.4 import, page, behavior, data path, schema, and safety contract.

## Included features

The only supported external import will be `from subsystems.vehicle import VehicleSubsystem`.

| Private engine | Responsibility |
|---|---|
| Vehicle | Create, read, list, update, and archive vehicle profiles |
| Odometer | Record/list kilometer readings with chronological monotonicity checks |
| Maintenance | Record and list service history |
| Schedule | Create, list, complete, and evaluate date/odometer maintenance schedules |
| Energy | Record and list fuel or charging quantities and costs |
| Report | Per-vehicle status, due-maintenance, distance, and cost summaries |
| Storage | Lazy SQLite schema, transactions, integrity health, export snapshot |
| Validation | Identifiers, dates, text, enums, and non-negative numbers |

The facade will expose only:

- `health()`, `interface_manifest()`, `export_snapshot()`;
- `create_vehicle()`, `get_vehicle()`, `list_vehicles()`, `update_vehicle()`, `archive_vehicle()`;
- `record_odometer()`, `list_odometer_readings()`;
- `record_maintenance()`, `list_maintenance_records()`;
- `create_maintenance_schedule()`, `list_maintenance_schedules()`, `complete_maintenance_schedule()`, `due_maintenance()`;
- `record_energy()`, `list_energy_logs()`, `vehicle_report()`.

One Vehicle page will be added to canonical and compatibility-mode navigation. It will create/select vehicles, show current odometer/due maintenance/recent maintenance/period costs, record the included events, and explicitly archive a vehicle. Page load and reports must not create storage.

Add `V15_STABLE_MANIFESTS = V14_STABLE_MANIFESTS + (vehicle manifest,)`. Older manifest constants remain unchanged. Vehicle manifest: version `1.0.0`, Living OS `>=1.5,<2.0`, privacy `sensitive`, capabilities `vehicle-profile`, `odometer`, `maintenance`, `maintenance-schedule`, `energy-cost`, `vehicle-report`. Visible labels change to `v1.5 Stable` only after implementation verification passes.

## Excluded features

- GPS, routes, trips, driver behavior, or location tracking.
- Reminders, notifications, calendar jobs, schedulers, or automation.
- Predictive maintenance, AI recommendations, autonomous writes, or model calls.
- Insurance, registration renewal, tax, loan/lease, depreciation, resale, or documents.
- Repair-shop, manufacturer, telematics, OBD, maps, pricing, charger, or other integrations.
- Finance posting, cross-subsystem joins, or domain-subsystem imports.
- Units other than kilometers; attachments; images; CSV; bulk import/export.
- Legacy Vehicle migration or a legacy Vehicle compatibility module/data file.
- Changes to v1.4 records, schemas, migrations, backups, dependencies, authentication, hosted storage, or deployment.
- Unrelated refactoring, commit, push, tag, release, publication, deployment, or destructive work.

## Affected modules and files

New after approval:

```text
subsystems/vehicle/__init__.py
subsystems/vehicle/subsystem.py
subsystems/vehicle/engines/{__init__,vehicle,odometer,maintenance,schedule,energy,report,storage,validation}.py
tests/test_vehicle_subsystem_v10.py
docs/vehicle-subsystem-v1.0/{ARCHITECTURE_REVIEW,DATA_SCHEMA,ENGINE_MAP,MIGRATION_ROLLBACK_PLAN}.md
```

Existing runtime/configuration files after approval:

- `subsystems/operations/engines/catalog.py`: append v1.5 manifest only.
- `subsystems/experience/engines/pages.py`: add Vehicle page only.
- `subsystems/experience/engines/shell.py`: compose/register Vehicle, use v1.5 manifest, update visible version.
- `tests/test_streamlit.py`: add Vehicle to page/no-write checks and expect v1.5.
- `tests/test_v10.py`: update only current-version assertions; retain historical assertions.
- `tests/test_v12_architecture.py`: register Vehicle as self-only and permit Experience to use its public facade.
- `.gitignore`: add `data/vehicle/`.

Implementation documentation: synchronize the governing top-level documents and `docs/README.md`; add `RELEASE_NOTES_v1.5.md`, subsystem verification evidence, and `docs/releases/v1.5/` readiness evidence.

The executable-manifest pointer in `config/modules/README.md` is also synchronized to v1.5; `config/module_registry.json` remains unchanged.

No change is planned for `app.py`, compatibility aliases, Core/Foundation/Operations/Insight implementations, existing domain subsystems, `config/module_registry.json`, owner-data files, requirements, or deployment configuration.

## Data model changes

Add isolated `data/vehicle/vehicle.sqlite3`, created only on the first explicit Vehicle write. Schema version is 1.

- `vehicle_vehicles`: `vehicle_id` PK; `display_name`; `manufacturer`; `model`; nullable `model_year` (`1886..current_year+1`); `powertrain` (`gasoline|diesel|hybrid|electric|other`); `status` (`active|archived`); UTC timestamps.
- `vehicle_odometer_readings`: `reading_id` PK; vehicle FK; ISO `recorded_on`; non-negative integer `odometer_km`; note; created timestamp; unique `(vehicle_id, recorded_on, odometer_km)`. A reading cannot be lower than the nearest earlier reading or higher than the nearest later reading; equal readings on different dates are allowed.
- `vehicle_maintenance_records`: `maintenance_id` PK; vehicle FK; non-empty `service_type`; ISO `serviced_on`; nullable non-negative `odometer_km`; non-negative integer `cost`; provider; note; created timestamp.
- `vehicle_maintenance_schedules`: `schedule_id` PK; vehicle FK; service type; nullable `due_on`; nullable non-negative `due_odometer_km`; `status` (`active|completed|dismissed`); nullable completed-maintenance FK; UTC timestamps. At least one due criterion is required; due state is calculated.
- `vehicle_energy_logs`: `energy_id` PK; vehicle FK; `energy_type` (`fuel|charge`); ISO date; nullable odometer; positive integer `quantity_milliunits` (thousandths of liter or kWh); non-negative integer cost; note; created timestamp.
- `vehicle_meta`: schema/subsystem version. No migration ledger.

Foreign keys are enabled. Multi-record changes are transactional. IDs are subsystem-generated. Money uses integer owner-currency units; no conversion is included.

## Backward compatibility

- Verified baseline: v1.4 commit `2e4d1fa`, 74 tests passing.
- All v1.4 imports, exact module aliases, pages, behavior, schemas, paths, and data remain unchanged.
- `V14_STABLE_MANIFESTS` and older manifests remain unchanged; Vehicle exists only in `V15_STABLE_MANIFESTS`.
- Existing Finance, Health, Housing, Hub, settings, registry, report, backup, AI, and migration contracts remain unchanged.
- `config/module_registry.json` remains unchanged; its planned record is legacy configuration, not the executable manifest.
- Vehicle imports only Vehicle engines/standard library; Experience imports only its facade.
- An absent Vehicle database is valid. Reverting code leaves v1.4 data usable and Vehicle data dormant.

## Migration and rollback

There is no owner-data migration. The repository has no legacy Vehicle source, and implementation must not invent, scan for, or import one. Schema v1 initialization occurs transactionally on the first explicit Vehicle write—not planning, tests against repository data, startup, page load, release, or deployment.

Code rollback is to v1.4. `data/vehicle/vehicle.sqlite3` may remain dormant; rollback never deletes it. Any later removal/restoration is a separate approved operation preceded by a verified copy and limited to `data/vehicle/`. Existing v1.4 stores are never Vehicle rollback targets.

## Test plan

All tests use temporary/injected storage and never repository owner data. Add seven isolated tests:

1. Public export/manifest, independent storage, and read-without-create.
2. Vehicle create/get/list/update/archive validation and filtering.
3. Odometer chronology, backfill-neighbor monotonicity, and rejection.
4. Maintenance records, schedule validation, due evaluation, completion linkage.
5. Fuel/charge quantity scaling, filtering, totals, deterministic reports.
6. Transaction rollback, SQLite integrity/FKs, health, export snapshot.
7. Privacy ignore, manifest separation, import boundaries, private engines.

Acceptance verification: existing 74 plus 7 new tests = 81 passing; compilation/import check; every canonical and compatibility page renders; reads/pages do not create Vehicle storage; architecture checks pass; labels/catalog change only after full pass; diff contains no data, dependency, unrelated, release, or deployment change.

## Completed implementation sequence

1. Reconfirm clean v1.4 baseline and 74 tests.
2. Before code, mark the approved scope in every governing document and create the Vehicle architecture, schema, engine-map, migration/rollback, and release-note drafts.
3. Add storage/validation, domain engines, and facade.
4. Add v1.5 manifest while proving older manifests unchanged.
5. Add Vehicle page and shell wiring.
6. Add isolated and regression/no-write tests.
7. Run compilation, 81 tests, architecture, SQLite integrity, and Streamlit smoke checks.
8. Synchronize verification/readiness results, confirm every document matches the implementation, and inspect the complete diff.
9. Stop for separate release approval; do not migrate, commit, push, tag, release, or deploy.

## Acceptance and approval gate

Exactly the included facade/capabilities must be implemented; excluded capabilities remain absent; all verification passes; v1.4 remains compatible; no owner data or repository Vehicle DB changes; docs match results; final diff is limited to approved files.

**STOP — RELEASE APPROVAL REQUIRED.** Implementation and verification are complete. Commit, push, GitHub Release, Streamlit deployment, and migration remain unauthorized.
