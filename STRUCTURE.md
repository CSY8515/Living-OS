# Living OS v1.7 Repository Structure — Stable

    subsystems/
      foundation/engines/    platform and state
      operations/engines/    journal, decision, knowledge, reports, settings, catalog
      insight/engines/       projections and explicit AI
      experience/engines/    shell, pages, responsive layout
      compatibility/engines/ stable historical workflows
      database/              Database Data Plane public facade
        subsystem.py
        engines/             connection, migrations, repository,
                             execution, integrity, contracts
      database_management/   Database Control Plane public facade
        subsystem.py
        engines/             health, operational report

app/, core/, modules/, and shared/ contain compatibility aliases. Tests may use public or canonical paths. Runtime data stays in data/, logs/, reports/, state/, config/, and backups/.

| Previous implementation | Canonical owner |
|---|---|
| core/*.py; shared/time.py | foundation/engines |
| canonical domain services | operations/engines |
| projections and AI services | insight/engines |
| app/*.py | experience/engines |
| legacy flat modules | compatibility/engines |

All previous public paths remain available.

## Database Foundation v1.7

Runtime canonical database: `data/hub/living_os.sqlite3`.

Verified v1.7 backups: `backups/v1.7/database/`.

Database Foundation documents: `docs/03_Database/`.

Release-preparation evidence: `docs/releases/v1.7/`.

The existing Finance, Health, Housing, Vehicle, and Food database paths remain unchanged. No startup path performs the v1.7 Schema migration automatically.

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

## Vehicle Subsystem v1.0

    subsystems/vehicle/
      __init__.py       public VehicleSubsystem export
      subsystem.py      interface and composition root
      engines/          vehicle, odometer, maintenance, schedule,
                        energy, report, storage, validation

Default sensitive state is `data/vehicle/vehicle.sqlite3`. No legacy compatibility path or Vehicle migration exists. Reads do not create the database.

## Food Subsystem v1.0

    subsystems/food/
      __init__.py       public FoodSubsystem export
      subsystem.py      interface and composition root
      engines/          ingredient, recipe, cooking, meal, nutrition,
                        report, storage, validation

Default sensitive state is `data/food/food.sqlite3`. No legacy compatibility path or Food migration exists. Reads do not create the database.
