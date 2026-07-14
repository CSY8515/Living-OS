# Living OS v2.0 Architecture

## Authority

`MASTER_DESIGN.md` is the architectural source of truth. This document is the official structural view of that design. Repository layout is defined by `STRUCTURE.md`; delivery order is defined by `ROADMAP.md`.

## Architecture style

Living OS v2.0 is a single-owner modular Hub, not a collection of microservices.

```text
Responsive clients
        ↓
Hub application services and explicit commands
        ↓
Official modules and expansion modules
        ↓
Core contracts and policies
        ↓
Canonical storage, documents, audit journal, and event outbox
        ↓
Projections and governed integration adapters
```

## Core

Core owns only permanent platform capabilities:

- Stable identities and typed record references
- Schema registry and migration ledger
- Command validation and query contracts
- Audit journal and event outbox
- Typed relationships between module-owned records
- Module manifests, lifecycle, health, capabilities, and feature flags
- Owner security, device pairing, sessions, secrets, and policy enforcement
- Storage, document, backup, import, export, and integration ports

Core does not own Finance, Housing, Vehicle, Health, or other domain calculations.

## Hub

The Hub is the one running authority for canonical state. It hosts Core, module execution, projections, policies, integrations, and audit.

Desktop and notebook may host the Hub. Desktop, notebook, tablet, and mobile clients connect to the same Hub and invoke the same application contracts. A managed or self-hosted deployment profile may be added later without changing module behavior.

## Modules

A module is a bounded personal domain that:

- Owns its records and validation.
- Uses Core commands, queries, identities, links, events, and policies.
- Publishes declared capabilities and projections.
- Never reads or writes another module's storage directly.
- Never depends on device-specific UI code.

Official modules are Journal, Decision, Reports, Knowledge, Documents, Dashboard, Analytics, Review, Calendar, Routine, Notification, Inventory, Assets, Finance, Housing, Vehicle, Health, AI Briefing, Module Manager, and Settings/Admin.

Dashboard, Analytics, Review, and AI Briefing consume projections. They are never authorities for operational records.

## Expansion

Expansion modules use the same public contracts as official modules. Each expansion declares its ID, version, Core compatibility, permissions, schemas, migrations, commands, queries, events, projections, UI contributions, privacy class, backup behavior, and removal behavior.

Expansion lifecycle states are Registered, Installed, Enabled, Degraded, Disabled, and Removed. Disabling or removing executable capability does not silently delete owned data.

## Dependency direction

Allowed dependency direction:

```text
UI shell → application services → module contracts → Core ports → adapters
module → Core contracts
projection → published queries/events
integration adapter → declared Core integration port
```

Forbidden dependency direction:

- Core to a domain module
- Module to another module's persistence
- Operational module to Dashboard, Analytics, Review, or AI Briefing
- Domain behavior to Streamlit or another UI framework
- Integration provider to canonical storage
- Expansion module to Core internals

Cross-module workflows use typed links, published queries, domain events, or an application-level orchestrator with explicit approval.

## Cross-platform strategy

The v2.0 strategy is one Hub with responsive clients:

- One Core and one domain behavior contract serve every device.
- UI layout, density, file selection, and native delivery adapters may differ.
- Unsupported native delivery falls back to the in-app Notification inbox.
- Connected devices have functional parity for all released domain operations.
- Remote access requires encrypted transport, owner authentication, pairing, revocation, and secure sessions.
- Streamlit may serve as a transition UI, but Core contracts cannot depend on Streamlit session state.
- Offline multi-device editing is a future candidate and is not promised by v2.0.

## AI Integration Layer

AI providers are isolated behind a provider-neutral gateway. AI receives only explicitly approved context packages and returns source-attributed drafts. It cannot directly mutate canonical records. Promotion of a draft requires a separate validated command and audit entry.

## Ultra Brain compatibility

Ultra Brain may consume consented, versioned context envelopes and return recommendations or proposed commands through the Ecosystem Gateway. Initial compatibility is read-only. Any later command proposal remains subject to Living OS policy, validation, explicit approval, and audit.

## Neural Ecosystem compatibility

Neural Ecosystem communication uses versioned events and import/export envelopes through the same Ecosystem Gateway. It cannot access module storage, credentials, or Core internals. Consent, provenance, minimization, revocation, and audit are mandatory.

## Canonical data rules

- Each module owns one authoritative representation of its domain records.
- Core owns common identity, relationships, policy, schema history, and audit.
- Reports and documents are versioned artifacts with stable references.
- Derived views are rebuildable projections.
- Every mutation is an explicit, validated, idempotent command with actor, source, reason, and expected version.
- Every v1 migration result is imported, quarantined with a reason, or explicitly rejected; nothing is silently discarded.
