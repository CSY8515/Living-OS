# Finance Subsystem v1.0 Architecture Review

## Previous state

Living OS contained a compatibility Finance calculator backed by data/finance_budget.json. It calculated income, fixed expenses, savings goals, remaining amount, and risk, but it was a single UI-oriented module rather than an independently mountable Subsystem.

## Decision

Finance is now a first-class Living OS Subsystem with one supported external facade: FinanceSubsystem. Ledger, Budget, Cash Flow, Savings, Report, Migration, Storage, and Validation Engines remain private implementation details.

## Reference rules

- External code imports FinanceSubsystem only.
- Engines depend only on other Finance engines and the Python standard library.
- Storage is injected and uses a versioned SQLite schema.
- Reads are lazy and do not create files.
- Writes are transactional.
- Monthly closings are immutable.
- Legacy migration is explicit, checksum-guarded, idempotent, and transactional.
- Integer monetary units and basis-point rates avoid binary floating-point storage errors.

This is the reference architecture for future production-grade Living OS subsystems.
