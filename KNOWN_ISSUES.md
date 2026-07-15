# Living OS v1.2 Known Issues

- `app/`, `core/`, `modules/`, and `shared/` remain compatibility aliases; removing them would be a breaking change.
- Canonical Hub and flat-file workflows coexist; startup does not migrate data.
- Pre-existing encoding damage is preserved rather than guessed.
- Remote access depends on deployment-provided TLS.
- The Hub is single-owner; offline concurrent editing is unsupported.
- Credential-store and optional AI availability are environment-dependent; AI stays draft-only.
- Streamlit remains the application shell.
- Streamlit Community Cloud's local filesystem is ephemeral and should not be treated as durable finance storage.

## Finance Subsystem v1.0

- Maturity projections use simple day-count interest before tax; actual bank compounding, fees, tax, and product-specific rules may differ.
- Monthly closings are immutable; corrections are made through later ledger records rather than editing a closed snapshot.
- Legacy Finance migration is explicit and is never run automatically.