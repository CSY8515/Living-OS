# Living OS v2.0 Official Roadmap

## Document authority

This document owns implementation sequence, version planning, module delivery order, release gates, and long-term direction. Architecture is governed by `MASTER_DESIGN.md` and `ARCHITECTURE.md`. Current lifecycle status is governed by `VERSION.md`.

## Vision

Living OS is the single-owner, modular personal operating hub for managing, organizing, connecting, analyzing, and recommending across personal operating data.

The permanent direction is one stable Core, one canonical Hub, module-owned domains, typed relationships, explicit commands, rebuildable projections, and no hidden authority. Desktop, notebook, tablet, and mobile use the same Hub capabilities; only presentation and device adapters differ.

## Development phases

Implementation status: Phases 0–4 for the approved v2.0 Stable scope are complete and awaiting release review. Phases 5–8 remain future roadmap items and are not implemented.

### Phase 0 — Documentation and approval

- Synchronize the approved v2.0 Master Design.
- Reconcile repository terminology and document authority.
- Obtain explicit approval before implementation.

### Phase 1 — Repository truth and compatibility baseline

- Reconcile v1.0 release state, tags, encoding, and tracked-data classification.
- Inventory every v1 schema, command, query, report, and safety boundary.
- Freeze representative v1 compatibility fixtures.

### Phase 2 — Permanent Core

- Define stable identity, schema, command, query, event, relationship, policy, audit, and module contracts.
- Establish transactional persistence behind a storage port.
- Establish migration, backup, import, export, and rollback governance.
- Establish owner security and device-pairing boundaries.

### Phase 3 — v1 parity migration

- Daily Log becomes Journal.
- Decision Log becomes versioned Decision.
- Archive becomes Knowledge and Casebook.
- Reports become canonical versioned artifacts.
- Dashboard, Analytics, Review, Settings, and approved AI safety behavior are preserved.
- Every accepted v1 record is imported, quarantined with a reason, or explicitly rejected.

### Phase 4 — Hub and cross-platform experience

- Deliver a responsive Hub shell.
- Replace fixed navigation with validated module contributions.
- Validate the same domain commands and data behavior across desktop, notebook, tablet, and mobile.
- Complete security, recovery, and cross-device release matrices.

### Phase 5 — Operational modules

- Documents
- Calendar
- Routine
- Notification
- Inventory
- Assets

### Phase 6 — Domain expansion

- Finance
- Housing
- Vehicle
- Health, after high-sensitivity policy approval

### Phase 7 — Intelligence

- Provider-neutral AI Integration Layer
- Source-attributed AI Briefing
- Explicit promotion of approved drafts into decisions, reports, cases, rules, or commands

### Phase 8 — Ecosystem compatibility

- Versioned Ecosystem Gateway
- Ultra Brain compatibility validation
- Neural Ecosystem compatibility validation

## Version roadmap

| Version | Scope |
|---|---|
| v2.0 Alpha 1 | Repository truth audit, v1 compatibility baseline, Core contracts |
| v2.0 Alpha 2 | Transactional Core, schemas, audit, migrations, backup, owner security |
| v2.0 Beta 1 | Journal, Decision, Reports, Knowledge, and Settings parity |
| v2.0 Beta 2 | Dashboard, Analytics, Review, Documents, and real Module Manager lifecycle |
| v2.0 RC | Responsive Hub, cross-device matrix, security review, migration rehearsal |
| v2.0 Stable | Permanent Hub foundation with complete v1 parity; no mandatory expansion module |
| v2.1 | Calendar, Routine, and Notification |
| v2.2 | Inventory, Assets, Documents, and Knowledge expansion |
| v2.3 | Finance, Housing, and Vehicle |
| v2.4 | Health and high-sensitivity policy profile |
| v2.5 | Governed AI Briefing and recommendation workflows |
| v3.x candidate | Ultra Brain and Neural Ecosystem integration through the Ecosystem Gateway |

## Module roadmap and dependency order

1. Core contracts, persistence, migration, audit, policy, security, and module runtime.
2. Journal, Decision, Reports, Knowledge, Settings, and v1 compatibility.
3. Dashboard, Analytics, Review, and Documents.
4. Responsive Hub shell and connected-device parity.
5. Calendar, followed by Routine, followed by Notification.
6. Inventory and Assets.
7. Finance, followed by Housing and Vehicle.
8. Health after privacy and retention controls are approved.
9. AI Integration Layer, followed by AI Briefing after mature projections exist.
10. Ecosystem Gateway after Core and module contracts are stable.

Food remains a future candidate. Learning OS is represented by Knowledge plus later learning expansions.

## Release strategy

Every release requires:

1. Approved roadmap and decision record.
2. Exact schema and compatibility declaration.
3. Migration dry run against representative fixtures.
4. Verified backup and rollback path.
5. Module boundary review.
6. Security and privacy review.
7. Cross-device capability review.
8. Deterministic behavior and failure-path verification.
9. AI and automation safety verification where applicable.
10. Documentation, version, tag, and release-state reconciliation.
11. Dependency lock and release-artifact review.
12. Explicit user approval before commit, push, tag, release, or deployment.

Release channels are Alpha, Beta, Release Candidate, Stable, and independently versioned Expansion releases. No stable release may require AI or an external integration for basic Core operation.

## Long-term direction

- Preserve a stable modular Core rather than dividing Living OS into microservices.
- Keep each domain authoritative over its own records.
- Expand through versioned manifests and public contracts.
- Treat dashboards, analytics, reviews, and AI contexts as rebuildable projections.
- Keep AI and automation bounded, attributable, revocable, and human-approved.
- Support future native clients without changing domain behavior.
- Permit Ultra Brain and Neural Ecosystem communication only through the policy-governed Ecosystem Gateway.

## Approval gate

The approved v2.0 Stable implementation is complete. No commit, push, tag, release, or deployment may occur without ChatGPT review and explicit user approval.
