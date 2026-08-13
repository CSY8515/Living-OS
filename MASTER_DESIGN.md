# Living OS v1.8 Master Design — Stable

## v1.8 development increment

Living OS v1.8 adds Knowledge and Routine as independent Subsystems. Each owns its domain model, business rules, repository, schema, migration ledger, health response, execution outcomes, and management projection. Neither subsystem accesses another domain's private storage.

Both depend downward on the public Database Foundation adapter. Database owns shared connection and transaction mechanics; Database Management owns registry, integrity, migration visibility, backup, restore, and common operational status. Domain data ownership remains with Knowledge and Routine.

The Streamlit shell adds Knowledge, Routine, Knowledge Management, and Routine Management while retaining all existing pages and contracts. This increment is additive and backward compatible.

Mission: extend the shared Architecture foundation with Knowledge and Routine without removing stable behavior.

Release status: Living OS v1.8 Stable. Knowledge and Routine are integrated with the v1.7.1 Database Foundation contract; publication and Production deployment were approved on 2026-07-17.

Living OS is one Module. Its implementation unit is the Subsystem; Subsystems contain Engines; behavior is expressed by Functions and methods.

Contracts: preserve features, public imports, JSON/JSONL/report/settings/registry/Finance/Housing structures, explicit writes, draft-only AI, verified migration/restore, matching docs, and runtime placement below subsystems/.

Foundation owns platform policy; Operations owns life operations; Insight owns derived views; Experience owns presentation; Compatibility owns historical workflows and public-path continuity.

Release requires compilation, full regression, architecture boundaries, every-page smoke checks, data-path preservation, verified migration/backup/restore, matching documentation, Codex Review, and User Approval.

## Theme World Integration v2.097

Living OS consumes Ultra Brain Themes as Worlds, not as background names. The
selected Theme contributes composition, frame, lighting, texture, material,
effects, tokens, and the Living Home asset. Living Home remains the parent
World; Feature scenes inherit that language while retaining distinct scene
identity and functional purpose.

The canonical representative mapping is Finance `ledger-vault / vault-gate /
flow-ledger`, Health `biometric-garden / pulse-gate / recovery-ring`, and
Vehicle `mobility-bay / route-compass / transit-lane`. The other registered
screens follow the same contract. Functional cards, inputs, metrics, tables,
buttons, shared navigation, and responsive bottom navigation are visually
integrated without changing their behavior.

The Parent Theme image cannot be used as a Feature fallback. When a native
Theme x Feature concept image is unavailable, the official Feature image may be
declared as reused and the missing native image remains `ASSET REQUIRED`. This
preserves honest asset status and avoids duplicated Worlds.

## UI Foundation Compatibility v2.096

Living OS keeps its official visual design and recovers only the missing
compatibility foundation for future Ultra Brain settings. The Experience layer
owns a versioned Theme Contract, complete Design Tokens, a validated Theme
Adapter, registered Component Contracts, a UI Registry, a public UI Interface,
and module scopes. Ultra Brain owns customization; Living OS validates and
applies the supplied contract.

Global tokens cover theme mode, palette, typography, icons, cards, buttons,
dialogs, widgets, dashboard, animation, radius, shadow, layout, and background.
Every current module inherits the global surface and may receive a registered
module override. Unregistered fields, components, modules, properties, and
unsafe CSS syntax are rejected. The default v2.095 CSS and visuals are preserved
byte-for-byte, and this recovery adds no screen, feature, persistence, data
migration, deployment setting, or core runtime change.

## Database Foundation v1.7

Database and Database Management are independent peer Subsystems owned by the Settings/Admin Module. Database is the Data Plane; Database Management is the Control Plane. Database Management uses only the public Database control contract and never edits business records directly.

The Database Subsystem provides the SQLite connection and transaction boundary, additive versioned migrations, canonical Record Repository, Metadata, Integrity checks, verified Backup/Restore, and Execution records. Schema v2 adds record lifecycle metadata, migration history, execution records, backup history, restore history, and required indexes without deleting existing data.

The Database Management Subsystem provides read-only Health, Schema Registry, Migration state, Backup state, Restore preflight, Performance/Capacity observations, explicit maintenance requests, and operational reports. In v1.7.1, additive Foundation schema migrations run idempotently at bootstrap to keep the Execution Database operational; legacy business-data migration and every Backup/Restore remain explicit reviewed operations.

The v1.7 statement that these stores were independent is retained as historical context; v1.7.1 supersedes it with the integration contract below.

## Database Foundation Integration v1.7.1

Finance, Health, Housing, Vehicle, and Food retain domain-owned schemas and public facades but use the shared `ComponentDatabaseAdapter` for SQLite connections and transactions. Their contracts are persisted through the canonical `RecordRepository`; the Execution Database records component writes. Database Management provides a unified control plane for registration, schema, migration, health, integrity, backup, restore, and execution state without owning business logic.

Schema v3 is the v1.7.1 integration marker retained by v1.8. Knowledge and Routine now satisfy `docs/03_Database/Database_Integration_Contract.md`; future Investment, Job, Personal Growth, and Collaboration components, and every data-owning OS System, Capability, Module, Subsystem, Engine Group, Engine, or Function, must satisfy the same contract at bootstrap. Direct component-level SQLite connections are prohibited.

## Database Architecture Recovery v2.095

The Database Subsystem keeps its existing canonical SQLite storage and adds the missing versioned operational-data Interface, Contract, Registry, and Data Plane on top of `records`. The contract preserves Success, Failure, Error, Warning, Incident, Recovery, Rollback, Validation Failure, Execution Failure, Invalid Data, Rejected Decision, and Unresolved Issue. Retention is permanent by contract until an independently approved retention change; v2.095 performs no delete, merge, archive, migration, or schema change.

The peer Database Management Subsystem validates and classifies operational facts and execution records, detects duplicates logically, identifies repeated patterns, and generates deterministic recommendations, Rule Candidates, Standard Candidates, and Operational Reports. These outputs are advisory and cannot mutate business records or automatically apply rules. Operational Reports cross the Foundation Personal Secretary capability contract as safe summaries and references only: `Database → Database Management → Operational Report → Personal Secretary → User`. Personal Secretary aggregates, prioritizes, recommends, and formats the user report. UI and runtime composition remain unchanged.

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
