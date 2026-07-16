# Living OS v1.4 Master Design

Mission: implement the official Skeleton Architecture without adding features or removing behavior.

Living OS is one Module. Its implementation unit is the Subsystem; Subsystems contain Engines; behavior is expressed by Functions and methods.

Contracts: preserve features, public imports, JSON/JSONL/report/settings/registry/Finance/Housing structures, explicit writes, draft-only AI, verified migration/restore, matching docs, and runtime placement below subsystems/.

Foundation owns platform policy; Operations owns life operations; Insight owns derived views; Experience owns presentation; Compatibility owns historical workflows and public-path continuity.

Release requires compilation, full regression, architecture boundaries, every-page smoke checks, data-path preservation, and docs review.

## Official reference subsystem

Finance Subsystem v1.0 is the production reference for future Living OS subsystems. A reference subsystem must expose one facade, keep engines private, inject its storage boundary, avoid write-on-read behavior, validate at its boundary, use transactions for multi-record changes, publish a compatibility range and version, support isolated testing, and document migration and rollback behavior.

## Health Subsystem v1.0 implementation

Health applies the Finance reference architecture to sensitive Health data. It provides the nine approved domain engines through `HealthSubsystem`, stores owner data separately from fixtures, prevents automatic migration, and exposes deterministic baseline, trend, goal, and report behavior. Cross-domain access is prohibited below the facade.

## Housing Subsystem v1.0 implementation

Housing applies the reference architecture to the preserved Housing candidate workflow. It exposes one `HousingSubsystem` facade, preserves the legacy scoring contract, provides candidate CRUD, deterministic comparison and reports, isolates sensitive owner state, and requires explicit dry-run-first migration. The legacy Housing API and JSON source remain unchanged.
