# Living OS v1.7 Stable Known Issues

## Database Foundation v1.7

- The real workspace Hub database remains on its existing Schema until the owner explicitly approves the additive v1.7 Migration in Settings.
- Finance, Health, Housing, Vehicle, and Food retain independent SQLite storage in v1.7; conversion to the common Repository is intentionally deferred to separately approved incremental migrations.
- Health performance currently measures explicit check duration; continuous query telemetry and automated optimization are deferred.
- Capacity warning uses a configurable local file-size threshold. Distributed storage and automatic scaling are outside v1.7.
- Local Streamlit storage, including backups, is not durable on ephemeral hosting. Production requires an approved durable storage and backup profile.

- `app/`, `core/`, `modules/`, and `shared/` remain compatibility aliases; removing them would be a breaking change.
- Canonical Hub and flat-file workflows coexist; startup does not migrate data.
- Pre-existing encoding damage is preserved rather than guessed.
- Remote access depends on deployment-provided TLS.
- The Hub is single-owner; offline concurrent editing is unsupported.
- Credential-store and optional AI availability are environment-dependent; AI stays draft-only.
- Streamlit remains the application shell.
- Streamlit Community Cloud's local filesystem is ephemeral and should not be treated as durable finance storage.

## Food Subsystem v1.0

- Food SQLite storage remains single-owner and is not durable on Streamlit Community Cloud.
- Nutrition values are owner-entered deterministic records, not medical guidance or externally verified data.
- Units are limited to `g`, `kg`, `ml`, `l`, `item`, and `serving`; no conversions or estimates are performed.
- Food and Health nutrition remain deliberately independent and are not synchronized.

## Vehicle Subsystem v1.0

- Vehicle SQLite storage remains single-owner and is not durable on Streamlit Community Cloud.
- GPS/trips, reminders, external integrations, Finance posting, and legacy migration are deliberately excluded.
- Vehicle v1.0 uses kilometers and integer owner-currency costs only; unit and currency conversion are excluded.

## Finance Subsystem v1.0

- Maturity projections use simple day-count interest before tax; actual bank compounding, fees, tax, and product-specific rules may differ.
- Monthly closings are immutable; corrections are made through later ledger records rather than editing a closed snapshot.
- Legacy Finance migration is explicit and is never run automatically.
