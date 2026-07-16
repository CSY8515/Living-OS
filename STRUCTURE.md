# Living OS v1.4 Repository Structure

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

## Health Subsystem v1.0

    subsystems/health/
      __init__.py       public HealthSubsystem export
      subsystem.py      Living OS interface and composition root
      engines/          weight, body_composition, health_checkup, sleep,
                        exercise, nutrition, trend, goal, report,
                        migration, storage, validation

Default sensitive state is `data/health/health.sqlite3`. No v1.2 data path is changed.

## Housing Subsystem v1.0

    subsystems/housing/
      __init__.py       public HousingSubsystem export
      subsystem.py      Living OS interface and composition root
      engines/          candidate, scoring, comparison, report,
                        migration, storage, validation

Default sensitive state is `data/housing/housing.sqlite3`. Existing `modules/housing.py`, its canonical compatibility engine, and `data/housing_candidates.json` remain unchanged.
