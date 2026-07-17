# Living OS v1.7 Master Design — Stable

Mission: synchronize the shared Architecture foundation and complete the Database and Database Management Subsystems without adding v1.8 features or removing stable behavior.

Living OS is one Module. Its implementation unit is the Subsystem; Subsystems contain Engines; behavior is expressed by Functions and methods.

Contracts: preserve features, public imports, JSON/JSONL/report/settings/registry/Finance/Housing structures, explicit writes, draft-only AI, verified migration/restore, matching docs, and runtime placement below subsystems/.

Foundation owns platform policy; Operations owns life operations; Insight owns derived views; Experience owns presentation; Compatibility owns historical workflows and public-path continuity.

Release requires compilation, full regression, architecture boundaries, every-page smoke checks, data-path preservation, verified migration/backup/restore, matching documentation, Codex Review, and User Approval.

## Database Foundation v1.7

Database and Database Management are independent peer Subsystems owned by the Settings/Admin Module. Database is the Data Plane; Database Management is the Control Plane. Database Management uses only the public Database control contract and never edits business records directly.

The Database Subsystem provides the SQLite connection and transaction boundary, additive versioned migrations, canonical Record Repository, Metadata, Integrity checks, verified Backup/Restore, and Execution records. Schema v2 adds record lifecycle metadata, migration history, execution records, backup history, restore history, and required indexes without deleting existing data.

The Database Management Subsystem provides read-only Health, Schema Registry, Migration state, Backup state, Restore preflight, Performance/Capacity observations, explicit maintenance requests, and operational reports. Startup never applies the v1.7 migration automatically. Migration, Backup, Restore, recorded Health Check, and Report generation are explicit owner actions in Settings.

Finance, Health, Housing, Vehicle, and Food retain their independent SQLite stores and public facades in v1.7. Their full conversion to the common Repository is a later, separately approved migration; v1.7 verifies compatibility and preserves all existing data paths.

## Official reference subsystem

Finance Subsystem v1.0 is the production reference for future Living OS subsystems. A reference subsystem must expose one facade, keep engines private, inject its storage boundary, avoid write-on-read behavior, validate at its boundary, use transactions for multi-record changes, publish a compatibility range and version, support isolated testing, and document migration and rollback behavior.

## Health Subsystem v1.0 implementation

Health applies the Finance reference architecture to sensitive Health data. It provides the nine approved domain engines through `HealthSubsystem`, stores owner data separately from fixtures, prevents automatic migration, and exposes deterministic baseline, trend, goal, and report behavior. Cross-domain access is prohibited below the facade.

## Housing Subsystem v1.0 implementation

Housing applies the reference architecture to the preserved Housing candidate workflow. It exposes one `HousingSubsystem` facade, preserves the legacy scoring contract, provides candidate CRUD, deterministic comparison and reports, isolates sensitive owner state, and requires explicit dry-run-first migration. The legacy Housing API and JSON source remain unchanged.

## Vehicle Subsystem v1.0 implementation

Vehicle applies the reference architecture through one `VehicleSubsystem` facade. Its boundary is limited to profiles, kilometer odometer readings, maintenance history/due criteria, fuel/charging costs, and deterministic reports. Vehicle state is isolated and sensitive; reads cannot create storage; engines cannot depend on another domain. GPS, reminders, AI, integrations, Finance posting, and migration are excluded.

## Food Subsystem v1.0 implementation

Food applies the reference architecture through one `FoodSubsystem` facade. Its boundary is limited to ingredients, recipes, cooking records, meal records, explicit owner-entered nutrition values, and deterministic reports. Food state is isolated and sensitive; reads cannot create storage; Food engines depend only on Food. Health synchronization, Finance posting, Inventory, Calendar, AI, integrations, automation, unit conversion, nutrition estimation, and migration are excluded.
