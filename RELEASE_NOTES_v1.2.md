# Living OS v1.2 Release Notes

Release date: 2026-07-15
Status: Stable

## Summary

Living OS v1.2 applies the official Module → Subsystem → Engine → Function architecture to the complete v1.1 runtime and ships Finance Subsystem v1.0 as the first production reference subsystem. Existing capabilities and data contracts remain compatible.

## Major changes

- Introduced Foundation, Operations, Insight, Experience, and Compatibility subsystems.
- Relocated runtime implementations below subsystem engine packages.
- Preserved `app.*`, `core.*`, `modules.*`, and `shared.*` as exact canonical module aliases.
- Added Finance Subsystem v1.0 behind the single public `FinanceSubsystem` facade.
- Added architecture, boundary, compatibility, migration, and Finance regression tests.
- Synchronized architecture, structure, migration, compatibility, regression, and release documentation.

## Architecture

```text
Living OS (Module)
└── Subsystem
    └── Engine
        └── Function
```

Runtime ownership is canonical under `subsystems/`. Compatibility paths contain no duplicate implementations.

## Finance Subsystem v1.0

Finance is independently mountable, testable, replaceable, and rollback-friendly. Its public facade coordinates private Ledger, Budget, Cash Flow, Savings, Report, Storage, Validation, and Migration Engines.

- Ledger: record income and expenses; query transactions.
- Budget: create budgets; calculate usage and remaining budget.
- Cash Flow: calculate monthly income, monthly expenses, and net cash flow.
- Savings: manage installments and deposits; calculate goal progress and maturity.
- Report: create immutable monthly closings, summaries, and financial status.
- Infrastructure: isolated persistence, input integrity, and explicit transactional legacy migration.

## Compatibility

Existing entry points, Python symbols, monkeypatch targets, data paths, JSON/JSONL schemas, report and backup formats, explicit migration controls, Streamlit pages, and draft-only AI rules are retained. The unreleased `V2_STABLE_MANIFESTS` name remains an alias.

Finance retains `modules.finance` behavior and `data/finance_budget.json`. The new SQLite store is lazy and isolated under `data/finance/`; no migration or database creation occurs merely by importing or rendering the application.

## Verification

- Historical and architecture baseline: 49/49 tests passed.
- Finance and integrated final suite: 60/60 tests passed.
- Compilation: passed.
- Legacy and canonical Streamlit page smoke tests: passed.
- Architecture placement, forbidden-import, facade identity, storage safety, rollback, and transactional migration checks: passed.

Streamlit bare-mode `ScriptRunContext` warnings during headless page tests are expected and do not indicate failures.

## Migration and upgrade

1. Back up the existing workspace data.
2. Install dependencies from the root `requirements.txt`.
3. Deploy or run the repository at tag `v1.2`.
4. Keep compatibility imports unchanged; migration to canonical imports is optional.
5. Invoke Finance legacy migration only after explicit operator review and approval.

The application never auto-migrates user data on startup.

## Deployment

Production URL: [https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/](https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/)

- Repository: `CSY8515/Living-OS`
- Branch/tag: `main` / `v1.2`
- Entrypoint: `app.py`
- Dependency file: root `requirements.txt`
- Recommended Python: 3.12
- Required secrets: none; OpenAI credentials are optional and AI output remains draft-only.

## Known limitations

- Streamlit Community Cloud local files are not a durable multi-user database.
- Finance maturity projections do not model every bank's compounding, fees, taxes, or product rules.
- The Hub remains a single-owner workflow and does not support offline concurrent editing.
- Credential-store and optional AI availability depend on the deployment environment.

## Next direction

Future work may add independently versioned subsystems and durable hosted storage. Those items are outside v1.2.
