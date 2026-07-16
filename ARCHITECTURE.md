# Living OS v1.3 Architecture

## Official placement

Ultra Brain → Meta OS Ecosystem → OS Ecosystem → Capability → Module → Subsystem → Engine → Function

Living OS occupies the Module layer. Internally it implements Living OS → Subsystem → Engine → Function.

## Subsystems

- Foundation: contracts, commands, storage, schemas, audit, relationships, documents, security, backup, migration, integrations, module runtime, time, and Hub composition.
- Operations: Journal, Decision, Knowledge, Reports, Settings, and module catalog.
- Insight: read-only projections and explicitly requested, provider-isolated, draft-only AI processing.
- Experience: Streamlit shell, pages, navigation, and responsive layout; no persistence ownership.
- Compatibility: unchanged v0.8–v1.1 flat-file workflows and public API continuity.

## Dependencies

Experience → Foundation, Operations, Insight, Compatibility; Operations → Foundation; Insight → Foundation; Compatibility → Compatibility, Insight; Foundation → Foundation.

Canonical subsystem code may not import app.*, core.*, modules.*, shared.*, or expansion.*. Foundation may not import another subsystem. UI cannot own canonical persistence. AI cannot directly mutate records.

Previous public paths alias the same canonical Python module objects, preserving public/private symbols, monkeypatching, and exception identity. V2_STABLE_MANIFESTS remains an alias of V12_STABLE_MANIFESTS. This move performs no data migration.

## Finance Subsystem v1.0 reference architecture

Finance is an independently mountable subsystem below Living OS. Its only supported external object is FinanceSubsystem. Storage, Validation, Ledger, Budget, Cash Flow, Savings, Report, and Migration Engines are composed internally.

## Health Subsystem v1.0

Health is an independently mountable sensitive-data subsystem whose only supported boundary is `HealthSubsystem`. Weight, Body Composition, Health Checkup, Sleep, Exercise, Nutrition, Trend, Goal, Health Report, Migration, Storage, and Validation engines are private.

Health depends only on Health. Experience may call the public facade; Health never directly imports another domain subsystem. Default state is isolated below `data/health/`, reads are lazy, writes are transactional, and migration is explicit.

Finance → Finance only. Experience may depend on the Finance public facade; no other subsystem may import Finance engines. A database path can be injected so the subsystem can be tested, replaced, or rolled back independently. Reads do not create storage; writes are transactional.
