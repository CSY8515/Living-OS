# Living OS v1.2 Stable

Living OS is the Module layer in the official Skeleton Architecture:

Living OS (Module) → Subsystem → Engine → Function

v1.2 is an architecture migration, not a feature release. All runtime implementation now lives under subsystems/ in Foundation, Operations, Insight, Experience, or Compatibility. Existing app.*, core.*, modules.*, and shared.* paths remain exact module aliases, preserving imports and monkeypatch behavior.

## Run

    python -m pip install -r requirements.txt
    python -m streamlit run app.py

## Verify

    python -m compileall -q app.py app core modules shared subsystems tests
    python -m unittest discover -s tests -v

Existing data paths and structures, backups, explicit migration approval, and AI non-write guarantees are preserved. See ARCHITECTURE.md, STRUCTURE.md, VERSION.md, RELEASE_NOTES_v1.2.md, and docs/v1.2/.

## Finance Subsystem v1.0

Finance is the first official production-grade reference Subsystem. Use only its public facade:

    from pathlib import Path
    from subsystems.finance import FinanceSubsystem

    finance = FinanceSubsystem(Path.cwd())
    finance.record_income(3000000, "Salary", "2026-07-01")
    status = finance.summary_report("2026-07")

It provides Ledger, Budget, Cash Flow, Savings, Report, and explicit legacy Migration behavior. See docs/finance-subsystem-v1.0/ and RELEASE_NOTES_FINANCE_SUBSYSTEM_v1.0.md.

## Production deployment

Production URL: [https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/](https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/)

Streamlit Community Cloud coordinates:

- Repository: `CSY8515/Living-OS`
- Branch: `main`
- Entrypoint: `app.py`
- Python: 3.12 recommended
- Secrets: none required

The current file-backed stores are intended for a single-owner runtime. Community Cloud's local filesystem is not durable finance storage; keep backups or use an externally managed persistent store for long-lived production records.