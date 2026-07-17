# Database Integration Contract — Living OS v1.7.1

## v1.9 contract addendum

`SUB-INVESTMENT` and `SUB-JOB` are active runtime components. Each declares its own database path, schema version 1, unique migration ID, owner, and `record-repository` integration mode. Their adapters attach to the unchanged Database Foundation control contract so Database Management can inspect, initialize, back up, and restore them without reading or changing business rows.

## Purpose

Every data-owning Living OS component uses the Database Foundation from its creation. This contract applies to OS System, Capability, Module, Subsystem, Engine Group, Engine, and Function layers. It does not transfer domain ownership to the Database Subsystem.

## Required contract

Each component declares a unique ID, architecture layer, data owner, database path, schema version, migration ID, integration mode, and Execution/Backup/Restore/Integrity capabilities. The canonical template is `config/templates/database_component.json`; the policy registry is `config/database_integration_registry.json`.

New components use `record-repository`. Existing domain-owned SQLite schemas may use `compatibility-adapter` while preserving their public behavior. Direct `sqlite3.connect` calls in component storage engines are prohibited; connection and transaction boundaries belong to `ComponentDatabaseAdapter` and `SQLiteConnectionLayer`.

## Ownership boundary

- The component owns schema meaning, validation, business rules, and retention decisions for its data.
- Database owns connection, transaction, repository, integrity, migration execution, backup, restore, and execution metadata primitives.
- Database Management is the control plane. It observes and operates registered databases but never writes domain business rows.
- The central `RecordRepository` stores registration and control-plane records, not duplicate domain payloads.

## Registration lifecycle

Bootstrap → Contract validation → Registry registration → Schema/Migration initialization → Integrity validation → Execution activation → Test → Release.

Registration is rejected when the layer is unknown, ownership or migration metadata is missing, the path escapes the repository, or the integration mode is unsupported. Runtime registrations are persisted as `SUB-DATABASE/component_registration` records.

## Required tests

Every component must prove contract validation, no direct SQLite connection, transaction rollback, schema version, idempotent migration, integrity, verified backup/restore, Execution Database recording, data-owner isolation, and Database Management visibility. Architecture tests validate the same rules for future and upper-layer bootstrap assets.
