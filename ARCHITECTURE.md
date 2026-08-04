# Living OS v1.7 Architecture — Stable

## Official placement

User → Ultra Brain → Meta OS Ecosystem → OS Ecosystem → OS System → Capability → Module → Subsystem → Engine Group → Engine → Function

Living OS occupies the Module layer. Internally it implements Living OS → Subsystem → Engine → Function.

## Subsystems

- Foundation: contracts, commands, storage, schemas, audit, relationships, documents, security, backup, migration, integrations, module runtime, time, and Hub composition.
- Operations: Journal, Decision, Knowledge, Reports, Settings, and module catalog.
- Insight: read-only projections and explicitly requested, provider-isolated, draft-only AI processing.
- Experience: Streamlit shell, pages, navigation, and responsive layout; no persistence ownership.
- Compatibility: unchanged v0.8–v1.1 flat-file workflows and public API continuity.
- Database: SQLite Data Plane, Schema, Migration, Transaction, Repository, Metadata, Backup/Restore, Integrity, and Execution records.
- Database Management: Control Plane for Health, Schema Registry, Migration, Backup, Restore, Performance, Capacity, warnings, and operational reports.

## Dependencies

Experience → Foundation, Operations, Insight, Compatibility and public domain facades; Operations → Foundation; Insight → Foundation; Compatibility → Compatibility, Insight; Database → Database, Foundation; Database Management → Database public control contract, Foundation. The Hub composition root wires the two peer Database Subsystems without making either one the child of the other.

Canonical subsystem code may not import app.*, core.*, modules.*, shared.*, or expansion.*. UI cannot own canonical persistence. AI cannot directly mutate records. Database Management cannot directly mutate business records.

## UI Foundation Compatibility v2.096

The Experience layer exposes the versioned `ultra-brain.ui/v1` contract through
`LivingOSUIInterface`. `UIRegistry` owns the official dark/light base themes, 15
shared Component Contracts, and the module scope for every current screen.
`ThemeAdapter` validates and maps Ultra Brain Design Tokens, assets, and icons to
the existing Living OS CSS surface. Callers cannot provide arbitrary selectors
or unregistered component properties.

All modules inherit the global contract; active pages also render a hidden
registered scope for optional module tokens. With no external contract,
`OFFICIAL_UI_CSS`, checked-in assets, icons, page order, and interactions remain
unchanged. Ultra Brain remains the future customization owner. This boundary
adds no Living OS customization page, persistence, feature, domain dependency,
or runtime-composition change.

## Database Foundation v1.7

`DatabaseSubsystem` is the only supported v1.7 canonical Database facade. It owns `SQLiteConnectionLayer`, `MigrationRegistry`, `RecordRepository`, `IntegrityEngine`, `ExecutionRecorder`, and the verified shared Backup adapter.

`DatabaseManagementSubsystem` depends on the `DatabaseControlInterface` protocol. Its Health and Report engines are read-only unless an owner explicitly requests Migration, Backup, Restore, recorded Health Check, or Report generation.

Existing Module databases remain independently owned and unchanged. v1.7 performs no automatic real-data migration and adds no direct cross-domain database access.

### v2.095 Database architecture recovery

The existing canonical `records` and `execution_records` Data Plane now exposes a versioned operational-data contract and registry. Operational facts are preserved under `SUB-DATABASE/operational_data` for Success, Failure, Error, Warning, Incident, Recovery, Rollback, Validation Failure, Execution Failure, Invalid Data, Rejected Decision, and Unresolved Issue. Retention is `PRESERVE`; duplicate handling is a read-only logical projection and never deletes or rewrites source records.

Database Management validates and classifies preserved facts and execution history, detects logical duplicates and repeated patterns, and produces deterministic recommendations, Rule Candidates, Standard Candidates, and Operational Reports. Candidates are advisory and are never applied automatically. The Personal Secretary capability contract accepts safe report envelopes, aggregates and prioritizes reports, and produces a user-facing briefing without receiving secrets or raw business payloads. This recovery adds no UI, new subsystem, schema migration, or runtime-composition change.

Previous public paths alias the same canonical Python module objects, preserving public/private symbols, monkeypatching, and exception identity. V2_STABLE_MANIFESTS remains an alias of V12_STABLE_MANIFESTS. This move performs no data migration.

## Investment and Job Subsystems v1.9

Investment and Job are independent data-owning Subsystems below Living OS. Their only supported external objects are `InvestmentSubsystem` and `JobSubsystem`. Each owns its validation, lifecycle, schema meaning, and management projection while using the shared Database Foundation adapter for connections, transactions, registration, integrity, execution records, backup, and restore.

Investment and Job may depend only on their own code plus Database and Foundation contracts. They do not import one another or Finance, Health, Vehicle, Housing, Food, Knowledge, or Routine. Experience may call their public facades, but UI code owns no persistence. Reads are lazy, writes are transactional, schemas and migrations are additive and idempotent, and no legacy data migration runs automatically.

## Finance Subsystem v1.0 reference architecture

Finance is an independently mountable subsystem below Living OS. Its only supported external object is FinanceSubsystem. Storage, Validation, Ledger, Budget, Cash Flow, Savings, Report, and Migration Engines are composed internally.

Finance depends only on Finance. Experience may depend on the Finance public facade; no other subsystem may import Finance engines. A database path can be injected so the subsystem can be tested, replaced, or rolled back independently. Reads do not create storage; writes are transactional.

## Health Subsystem v1.0

Health is an independently mountable sensitive-data subsystem whose only supported boundary is `HealthSubsystem`. Weight, Body Composition, Health Checkup, Sleep, Exercise, Nutrition, Trend, Goal, Health Report, Migration, Storage, and Validation engines are private.

Health depends only on Health. Experience may call the public facade; Health never directly imports another domain subsystem. Default state is isolated below `data/health/`, reads are lazy, writes are transactional, and migration is explicit.

## Housing Subsystem v1.0

Housing is an independently mountable sensitive-data subsystem whose only supported boundary is `HousingSubsystem`. Candidate, Scoring, Comparison, Housing Report, Migration, Storage, and Validation engines are private.

Housing depends only on Housing. Experience may call the public facade; Housing never imports Finance, Health, Compatibility, or another domain subsystem. Default state is isolated below `data/housing/`, reads are lazy, writes are transactional, and legacy JSON migration is explicit and dry-run-first.

## Vehicle Subsystem v1.0

Vehicle is an independently mountable sensitive-data subsystem whose only supported boundary is `VehicleSubsystem`. Vehicle, Odometer, Maintenance, Schedule, Energy, Report, Storage, and Validation engines are private.

Vehicle depends only on Vehicle and the Python standard library. Experience may call its facade; no subsystem may import Vehicle engines. Default state is isolated below `data/vehicle/`, reads are lazy, and writes transactional. No legacy Vehicle source exists, so v1.5 includes no migration.

## Food Subsystem v1.0

Food is an independently mountable sensitive-data subsystem whose only supported boundary is `FoodSubsystem`. Ingredient, Recipe, Cooking, Meal, Nutrition, Report, Storage, and Validation engines are private.

Food depends only on Food and the Python standard library. Experience may call its facade; no subsystem may import Food engines. Default state is isolated below `data/food/`, reads are lazy, and writes are transactional. Food never imports or synchronizes Health nutrition or another domain. No legacy Food source exists, so v1.6 includes no migration.
