# Finance Subsystem v1.0 Structure

    subsystems/finance/
      __init__.py               public export: FinanceSubsystem
      subsystem.py              composition root and external facade
      engines/
        storage.py              lazy transactional SQLite storage
        validation.py           money, rate, date, month, and text validation
        ledger.py               income, expense, transaction queries
        budget.py               budgets, usage, remaining budget
        cash_flow.py            monthly income, expense, net cash flow
        savings.py              installment savings, deposits, progress, maturity
        report.py               summaries, status output, immutable monthly close
        migration.py            legacy finance_budget.json adoption

Runtime data defaults to data/finance/finance.sqlite3 and can be replaced with an injected database path. The compatibility modules.finance API and data/finance_budget.json remain unchanged.
