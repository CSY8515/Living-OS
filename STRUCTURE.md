# Living OS v2.0 Official Repository Structure

## Authority and timing

This document defines the implemented v2.0 repository structure. Legacy v1 modules remain as compatibility facades until owner-approved migration and deprecation; new authority resides in the Hub, Core, and canonical module services.

```text
Living-OS/
├── docs/
├── app/
├── core/
├── modules/
├── expansion/
├── shared/
├── assets/
├── tests/
├── scripts/
├── config/
└── data/
```

## Directory ownership

### `docs/`

Historical roadmaps, compatibility notes, governance records, and specialized supporting documentation. Root-level official documents remain the canonical entry points.

### `app/`

Device-responsive UI shells, navigation composition, presentation models, and application startup. It may call application contracts but contains no domain persistence or provider logic.

Suggested boundaries:

```text
app/
├── shell/
├── pages/
├── components/
└── presenters/
```

### `core/`

Permanent Hub contracts and platform services.

```text
core/
├── identity/
├── commands/
├── queries/
├── events/
├── relationships/
├── schemas/
├── policies/
├── audit/
├── modules/
├── storage/
├── documents/
├── security/
├── backup/
└── integrations/
```

Core cannot import from `modules/`, `expansion/`, or `app/`.

### `modules/`

First-party bounded domains. Each module owns its contracts, domain behavior, application handlers, projections, manifest, and migrations.

```text
modules/<module_id>/
├── manifest
├── domain/
├── application/
├── projections/
├── migrations/
└── ui/
```

Initial module IDs are `journal`, `decision`, `reports`, `knowledge`, `documents`, `dashboard`, `analytics`, `review`, `calendar`, `routine`, `notification`, `inventory`, `assets`, `finance`, `housing`, `vehicle`, `health`, `ai_briefing`, `module_manager`, and `settings`.

### `expansion/`

Optional first-party or approved third-party expansion packages. Expansion packages use public Core contracts and cannot import Core internals.

### `shared/`

Small, domain-neutral types and deterministic helpers that do not belong to Core services. This directory must not become a general dumping ground or an indirect module-coupling layer.

### `assets/`

Version-controlled, non-user runtime assets such as icons, templates, static styles, and safe example material. Private records and generated user documents are prohibited.

### `tests/`

Contract, unit, integration, migration, security, cross-platform, UI, and release verification. Tests use fixtures or isolated temporary data, never live user data.

```text
tests/
├── contracts/
├── core/
├── modules/
├── migrations/
├── integration/
├── security/
├── ui/
└── fixtures/
```

### `scripts/`

Explicit development, migration, verification, packaging, and recovery utilities. Scripts are not runtime features and require documented safety boundaries.

### `config/`

Non-secret defaults, schema catalogs, supported capability declarations, and environment profiles. Credentials and private owner settings are prohibited.

### `data/`

Local Hub state, module-owned canonical data, documents, projections, audit data, migration state, and backups according to deployment profile. Runtime data is excluded from release artifacts except sanitized fixtures.

## Dependency enforcement

```text
app → core public application contracts
modules → core public contracts + shared
expansion → core public contracts + shared
core → shared
tests → any approved public or test surface
scripts → explicit administrative contracts
```

Direct module-to-module storage access and reverse dependencies into `app/` are prohibited.

## Current-to-target mapping

| Current v1 location | Target ownership |
|---|---|
| `app.py` | `app/` shell |
| `modules/storage.py` | Split across Core storage, schema, backup, and query ports |
| `modules/daily_log.py` | `modules/journal/` |
| `modules/decision_log.py` | `modules/decision/` |
| `modules/archive.py` | `modules/knowledge/` |
| `modules/report_system.py` | `modules/reports/` |
| `modules/analytics.py` | `modules/analytics/` |
| `modules/review.py` | `modules/review/` |
| `modules/ai_analysis.py` | `modules/ai_briefing/` |
| `modules/ai_service.py` | Core AI integration adapter |
| `modules/ai_credentials.py` | Core secret adapter |
| `modules/settings.py` | `modules/settings/` plus Core administration ports |
| `modules/module_manager.py` | `modules/module_manager/` plus Core module runtime |
| `modules/finance.py` | `modules/finance/` after compatibility normalization |
| `modules/housing.py` | `modules/housing/` after compatibility normalization |

This mapping is implemented incrementally. Legacy flat modules remain only where required for v1 compatibility mode and existing compatibility contracts.
