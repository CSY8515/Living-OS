# Living OS v2.0 MASTER DESIGN

## Status and authority

- Version: Living OS v2.0 Implementation Candidate
- Status: Implementation Complete — Release Review Pending
- Implementation: Complete for the approved v2.0 Stable scope

This document is the single source of truth for Living OS v2.0 product philosophy, architecture, boundaries, module responsibilities, compatibility rules, and permanent design decisions. Specialized documents may reference but must not contradict it.

## Mission

Living OS is not another application. It is the central operating system of the OS Ecosystem. Its purpose is to manage, organize, connect, analyze, and recommend across personal operating data while preserving user ownership and decision authority.

## Permanent philosophy

- Single Source of Truth
- Practical Use First
- Decision Log Driven
- Report Driven
- Casebook Driven
- Rule Driven
- Real Data First
- Living Update
- Core Stability First
- Cross Platform First
- Human Authority
- Explicit and Reversible Change

Single Source of Truth means one canonical owner for each domain record, not one universal table. Living Update means governed revisions and rebuildable projections, not silent mutation. Rules are versioned, explainable, reviewable artifacts. AI and automation never acquire hidden authority.

## System definition

Living OS v2.0 is a single-owner modular personal operating Hub. One Hub owns canonical state and exposes the same domain capabilities to desktop, notebook, tablet, and mobile clients. Device interfaces may adapt layout and native integrations, but domain behavior and data meaning remain identical.

The architecture is a modular Hub, not microservices.

## Core design

Core provides the stable platform kernel:

- Identity and typed references
- Schema registry and migration ledger
- Explicit commands and read-only queries
- Audit journal and reliable event outbox
- Typed relationships across module-owned records
- Policy, consent, privacy, retention, and approval enforcement
- Module manifests, lifecycle, capabilities, health, and feature flags
- Owner security, device pairing, sessions, secrets, and encrypted transport boundaries
- Storage, document, backup, import, export, and integration ports

Core contains no domain-specific financial, housing, vehicle, health, inventory, or other personal-domain calculations.

## Hub design

The Hub hosts Core, official modules, approved expansions, projections, integrations, and audit. Desktop or notebook may host it locally. Connected devices operate against the same Hub authority. Alternate hosting profiles may be introduced through adapters without changing Core or module contracts.

## Canonical data model

Core owns shared identity, relationships, policies, schemas, and audit. Each module owns its domain records and invariants.

Required shared contracts include stable record and module identifiers, record version checks, actor/source/reason/timestamp metadata, typed links, domain events, projection checkpoints, document references, privacy classification, retention policy, and migration version.

There is no universal mutable record type. Cross-domain duplication cannot be presented as canonical truth.

## Mutation and review model

Every state change is an explicit validated command. Commands are idempotent, version-aware, policy-checked, and audited. Cross-module changes are coordinated by an application workflow; no module writes another module's records.

Recommendations, AI output, rule results, scheduled work, and external events first create proposals or drafts. Promotion into canonical state requires an approved command unless a narrowly scoped automation rule was explicitly authorized, remains revocable, and produces a complete audit trail.

## Projection model

Dashboard, Analytics, Review, search indexes, notifications, and AI contexts are derived from published queries or events. They are rebuildable and never become alternate authorities.

## Document and report model

Documents are governed artifacts with content integrity, metadata, versions, retention, privacy class, and stable references. Reports are immutable versions with explicit sources; editing produces a new version. The report catalog is canonical, and file storage is an implementation adapter rather than a second index.

## Decision, casebook, and rule model

Decision is a versioned lifecycle containing context, alternatives, evidence, rationale, status transitions, reviews, expected outcomes, actual outcomes, and linked artifacts.

Knowledge governs notes, references, cases, and living-rule candidates. The governed promotion path is:

```text
real record → reviewed evidence → casebook case → rule candidate → approved Living Rule
```

Living Rules are explainable, versioned, testable, reversible, and scoped. They generate proposals or approved commands; they do not bypass module ownership.

## Module responsibilities

| Module | Authority | Primary outputs | Required dependencies |
|---|---|---|---|
| Journal | Daily operating capture | Journal records and events | Core |
| Decision | Decision lifecycle and review | Versioned decisions | Core, document links |
| Reports | Deterministic attributable reporting | Versioned report artifacts | Core, published queries |
| Knowledge | Notes, cases, archive, and rules | Knowledge items and cases | Core, Documents |
| Documents | File lifecycle and references | Versioned document references | Core document port |
| Dashboard | Current operating picture | Read-only projections | Query API |
| Analytics | Pattern explanation | Metrics and trends | Projection API |
| Review | Human review queues | Review decisions and approved commands | Query and command APIs |
| Calendar | Events and commitments | Calendar events and occurrences | Core |
| Routine | Repeatable plans and completion | Routine instances and events | Core, Calendar contracts |
| Notification | Approved reminders and delivery | Inbox items and delivery receipts | Core delivery port |
| Inventory | Consumable ownership and quantity | Inventory state | Core, Documents |
| Assets | Durable-item lifecycle | Asset state and lifecycle events | Core, Documents |
| Finance | Budget, obligations, goals, and financial decisions | Financial state and risks | Core, Documents |
| Housing | Property, occupancy, costs, and comparisons | Housing state | Core, Documents; typed optional links |
| Vehicle | Vehicle, mobility, maintenance, and costs | Vehicle state | Core, Assets, Documents |
| Health | User-controlled health observations and trends | Health records and cautions | Core, Documents, strict policy |
| AI Briefing | Source-attributed analysis and recommendations | Unsaved drafts and proposals | AI gateway, policy, projections |
| Module Manager | Module lifecycle and diagnostics | Validated lifecycle state | Core module runtime |
| Settings/Admin | Owner, device, policy, integration, and backup configuration | Versioned configuration | Core administration ports |

Modules communicate through Core contracts. Direct module-to-module persistence access is prohibited.

## Boundary classification

### Core

Permanent domain-neutral identity, schema, command, query, event, relationship, policy, audit, security, lifecycle, persistence, document, backup, and integration contracts.

### Official module

A first-party bounded personal domain with owned records and declared capabilities.

### Expansion

An optional package installed through the same public contracts. It cannot modify Core, access undeclared capabilities, or bypass policy.

### Future candidate

Food, offline multi-device editing, collaborative or multi-user operation, additional provider integrations, and other unapproved capabilities. Future candidates are not implied v2.0 commitments. Learning OS is represented by Knowledge plus later learning expansions.

## Module lifecycle

Every module declares a stable ID, semantic version, Core compatibility, permissions, schemas, migrations, commands, queries, events, projections, UI contributions, privacy class, backup/export participation, health checks, and removal behavior.

Lifecycle states are Registered, Installed, Enabled, Degraded, Disabled, and Removed. Disabling a module preserves its data. Removal follows explicit retention and export policy.

## Cross-platform contract

The official strategy is one Hub with responsive clients:

- One Core and application contract for every device.
- Same released domain operations on connected desktop, notebook, tablet, and mobile clients.
- Device-specific layout and native capability adapters only.
- In-app fallbacks when native delivery or file capabilities are unavailable.
- Encrypted transport, owner authentication, device pairing, session revocation, and secure secret handling for remote access.
- No Core dependency on Streamlit or another presentation framework.
- Offline concurrent editing is outside v2.0 until conflict-resolution semantics are approved.

## AI design

The AI Integration Layer isolates models, providers, credentials, limits, safe errors, and request policy. AI receives an explicit, visible, minimized context package. Output identifies sources and uncertainty and remains a draft.

AI cannot directly edit, append, delete, restore, archive, notify, schedule, or overwrite canonical records. A separate approved command is required to promote output. Provider failure cannot block local Core functionality.

## Notification and automation design

Calendar owns events. Routine owns repeatable plans. Notification owns inbox and delivery state. Core supplies scheduling and reliable-delivery ports without owning domain meaning.

Automation must be explicitly configured, narrowly scoped, auditable, cancellable, failure-visible, and reversible where possible. Background behavior cannot broaden its authority from the triggering record.

## Compatibility and migration

Living OS v1 JSON, JSONL, Markdown, settings, registry, Finance, and Housing assets are compatibility inputs. Internal v2 persistence is transactional and versioned behind a storage port. JSON/JSONL remains an import/export compatibility format, not the permanent internal contract.

Migration requires an immutable pre-migration backup, dry-run report, encoding and schema inspection, deterministic ID mapping, record-count and checksum reconciliation, explicit quarantine reasons, rollback before adoption, and no silent record loss.

## Security and privacy

Living OS remains single-owner by default. Remote access introduces authentication but not multi-user roles. High-sensitivity modules use stricter minimization, encryption, retention, export, deletion, and AI-context policies.

Private runtime data, credentials, backups, and generated documents are excluded from release artifacts. Repository data is limited to sanitized fixtures and non-user assets.

## Future ecosystem compatibility

The Ecosystem Gateway is the only approved boundary for Ultra Brain and Neural Ecosystem communication. It exchanges versioned, consented, minimized, attributable envelopes and events.

Initial Ultra Brain compatibility is read-only. Later proposed commands remain subject to Living OS validation, explicit approval, policy, and audit. Neural Ecosystem participants cannot access module storage, secrets, or Core internals.

## Release design

v2.0 Stable delivers the permanent Hub foundation and complete v1 parity. Operational and domain expansions ship in later independently governed versions. Core operation never requires AI or an external integration.

Every release requires compatibility, migration, rollback, boundary, privacy, security, cross-device, deterministic behavior, dependency, documentation, and artifact review followed by explicit user approval.

## Permanent architectural decisions

1. Living OS uses a modular Hub, not microservices.
2. One Hub owns canonical state.
3. Transactional, versioned persistence sits behind Core ports.
4. Each module owns its domain records; Core owns shared governance.
5. Modules connect through typed links, events, queries, and approved workflows.
6. Every mutation is an explicit, validated, audited command.
7. Derived views are rebuildable projections.
8. Documents and reports use governed versioned artifacts.
9. Decisions preserve evidence, revisions, review, and outcomes.
10. Casebook evidence precedes Living Rule promotion.
11. Module installation and enablement are real runtime lifecycle states.
12. Expansion modules cannot modify or bypass Core.
13. AI returns drafts and has no direct write authority.
14. Automation is explicit, bounded, revocable, and auditable.
15. Connected clients share one behavior contract; UI alone adapts by device.
16. v1 data is imported, quarantined, or explicitly rejected—never silently lost.
17. Ultra Brain and Neural Ecosystem use only the Ecosystem Gateway.
18. Core contracts change only through approved decisions, migrations, compatibility periods, and deprecation policy.
19. v2.0 Stable is Core plus v1 parity, not every expansion module.
20. Implementation requires separate explicit approval.

## Approval boundary

The Master Design is approved and its v2.0 Stable scope is implemented. This document does not authorize commit, push, tag, release, or deployment. Those actions require separate explicit approval.
