# Living OS v1.2 Repository Structure

    subsystems/
      foundation/engines/    platform and state
      operations/engines/    journal, decision, knowledge, reports, settings, catalog
      insight/engines/       projections and explicit AI
      experience/engines/    shell, pages, responsive layout
      compatibility/engines/ stable historical workflows

app/, core/, modules/, and shared/ contain compatibility aliases. Tests may use public or canonical paths. Runtime data stays in data/, logs/, reports/, state/, config/, and backups/.

| Previous implementation | Canonical owner |
|---|---|
| core/*.py; shared/time.py | foundation/engines |
| canonical domain services | operations/engines |
| projections and AI services | insight/engines |
| app/*.py | experience/engines |
| legacy flat modules | compatibility/engines |

All previous public paths remain available.

## Finance Subsystem v1.0

    subsystems/finance/
      __init__.py       public FinanceSubsystem export
      subsystem.py      composition root
      engines/          storage, validation, ledger, budget, cash_flow,
                        savings, report, migration

Default private runtime state: data/finance/finance.sqlite3. Existing modules/finance.py remains the legacy compatibility alias and data/finance_budget.json remains unchanged.
