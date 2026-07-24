# Living OS v2.0.5 Known Issues

## Persistence and deployment

- Living OS remains a single-owner SQLite application. Horizontal multi-instance
  writes and offline concurrent editing are unsupported.
- Production startup now requires explicit durable data and independent backup
  roots. Streamlit Community Cloud's application-local filesystem does not meet
  that contract by itself.
- A v2.0.5 production deployment must not accept owner data until its durable
  data path, independent backup path, and authentication state pass
  `scripts/release_gate.py`.
- Living OS validates configuration and writability, but the operator remains
  responsible for the hosting provider's durability, retention, encryption, and
  disaster-recovery guarantees.
- Remote access depends on deployment-provided TLS.

## Database and migration

- Foundation Schema 4 is applied additively and idempotently during bootstrap.
  Legacy business-data migrations remain dry-run-first and owner-approved.
- Finance, Health, Housing, Vehicle, and Food retain domain-owned SQLite schemas
  behind the common Database Foundation adapter.
- `app/`, `core/`, `modules/`, and `shared/` remain compatibility aliases;
  removing them would be a breaking change.
- Canonical Hub and legacy flat-file workflows coexist. Startup does not migrate
  legacy business records.
- Capacity warnings are local file-size thresholds; distributed scaling and
  continuous query optimization are outside v2.0.5.

## Product boundaries

- The Hub is single-owner. Multi-user authorization and shared collaboration
  permissions are not implemented.
- AI availability depends on operator credentials and remains explicit,
  foreground, and draft-only.
- Global Timeline, Global Search, integrated reports, advanced analytics, Cross
  Analysis, Chat, OCR, Voice, automatic classification, Wardrobe, schedulers,
  triggers, background automation, and external integrations are deferred.

## Food Subsystem v1.0

- Nutrition values are owner-entered deterministic records, not medical guidance.
- Units are limited to `g`, `kg`, `ml`, `l`, `item`, and `serving`; conversions
  and estimates are not performed.
- Food and Health nutrition remain deliberately independent.

## Vehicle Subsystem v1.0

- GPS/trips, reminders, external integrations, Finance posting, and legacy
  migration remain excluded.
- Vehicle uses kilometers and integer owner-currency costs only.

## Finance Subsystem v1.0

- Maturity projections use simple day-count interest before tax; actual product
  compounding, fees, and tax may differ.
- Monthly closings are immutable. Corrections use later ledger records.
- Legacy Finance migration remains explicit and never runs automatically.
